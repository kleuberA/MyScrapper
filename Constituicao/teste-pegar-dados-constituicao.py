from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from colorama import Fore, Style, init
from difflib import unified_diff
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import os
import re

init(autoreset=True)

def limpar_texto(texto):
    return re.sub(r'\s+', ' ', texto).strip()

def extrair_texto(elemento):
    return limpar_texto(' '.join([t for t in elemento.stripped_strings]))

def verificar_diferencas(texto_antigo, texto_novo):
    diferencas = list(unified_diff(
        texto_antigo.splitlines(),
        texto_novo.splitlines(),
        lineterm='',
        fromfile='Texto Antigo',
        tofile='Texto Novo'
    ))
    return '\n'.join(diferencas)

service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

url = 'https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm'
driver.get(url)

time.sleep(3)

page_content = driver.page_source

soup = BeautifulSoup(page_content, 'html.parser')

data_atual = {
    "tipo": "Constituição da República Federativa do Brasil de 1988",
    "todos_artigos": []
}

titulo_atual = None
nome_titulo = None
capitulo_atual = None
nome_capitulo = None
secao_atual = None
nome_secao = None
artigo_atual = None
artigos = []

def salvar_capitulo_ou_secao():
    if capitulo_atual or secao_atual or artigos:
        data_atual["todos_artigos"].append({
            "titulo": titulo_atual,
            "nome_titulo": nome_titulo,
            "capitulo": capitulo_atual,
            "nome_capitulo": nome_capitulo,
            "secao": secao_atual,
            "nome_secao": nome_secao,
            "artigos": artigos
        })

paragrafos = soup.find_all('p')

for i, p in enumerate(paragrafos):
    texto_elemento = extrair_texto(p)
    
    if re.search(r'TÍTULO [IVXLCDM]+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        salvar_capitulo_ou_secao()
        titulo_atual = re.search(r'(TÍTULO [IVXLCDM]+)', texto_elemento).group(1)
        nome_titulo = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        capitulo_atual = None
        nome_capitulo = None
        secao_atual = None
        nome_secao = None
        artigos = []

    elif re.search(r'CAPÍTULO [IVXLCDM]+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        salvar_capitulo_ou_secao()
        capitulo_atual = re.search(r'(CAPÍTULO [IVXLCDM]+)', texto_elemento).group(1)
        nome_capitulo = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        secao_atual = None
        nome_secao = None
        artigos = []

    elif re.search(r'Seção [IVXLCDM]+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        salvar_capitulo_ou_secao()
        secao_atual = re.search(r'(Seção [IVXLCDM]+)', texto_elemento).group(1)
        nome_secao = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        artigos = []

    elif re.match(r'Art\. \d+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
        artigo_atual = {"artigo": texto_elemento, "conteudo": []}

    elif artigo_atual:
        artigo_atual['conteudo'].append(texto_elemento)

if artigo_atual:
    artigos.append(artigo_atual)
salvar_capitulo_ou_secao()

arquivo_json = './Constituicao/constituicao-dados.json'
arquivo_alteracoes = './Constituicao/alteracoes.json'

primeira_execucao = not os.path.exists(arquivo_json)

alteracoes = []
json_alteracoes = []

if primeira_execucao:
    os.makedirs(os.path.dirname(arquivo_json), exist_ok=True)
    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump([data_atual], f, ensure_ascii=False, indent=4)
    
    print("Primeira execução detectada. Dados salvos no arquivo JSON.")
    print(f"Arquivo salvo em: {arquivo_json}")
else:
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados_antigos = json.load(f)

    if isinstance(dados_antigos, list) and len(dados_antigos) > 0:
        dados_antigos = dados_antigos[0]
    elif not isinstance(dados_antigos, dict):
        dados_antigos = {"todos_artigos": []}

    artigos_antigos = {
        artigo['artigo']: artigo
        for item in dados_antigos.get("todos_artigos", [])
        for artigo in item.get("artigos", [])
    }
    artigos_novos = {
        artigo['artigo']: artigo
        for item in data_atual["todos_artigos"]
        for artigo in item["artigos"]
    }

    for chave, artigo_novo in artigos_novos.items():
        artigo_antigo = artigos_antigos.get(chave)
        if not artigo_antigo:
            alteracoes.append(f"{Fore.GREEN}Novo artigo adicionado:{Style.RESET_ALL} {chave}")
            json_alteracoes.append({"tipo": "novo", "artigo": chave, "conteudo_novo": artigo_novo["conteudo"]})
        elif artigo_antigo['conteudo'] != artigo_novo['conteudo']:
            diferencas = verificar_diferencas(
                '\n'.join(artigo_antigo['conteudo']),
                '\n'.join(artigo_novo['conteudo'])
            )
            alteracoes.append(f"{Fore.YELLOW}Artigo alterado:{Style.RESET_ALL} {chave}\n{Fore.BLUE}Diferenças:{Style.RESET_ALL}\n{diferencas}")
            json_alteracoes.append({
                "tipo": "alterado",
                "artigo": chave,
                "conteudo_antigo": artigo_antigo["conteudo"],
                "conteudo_novo": artigo_novo["conteudo"]
            })

    for chave in artigos_antigos.keys():
        if chave not in artigos_novos:
            alteracoes.append(f"{Fore.RED}Artigo removido:{Style.RESET_ALL} {chave}")
            json_alteracoes.append({"tipo": "removido", "artigo": chave, "conteudo_antigo": artigos_antigos[chave]["conteudo"]})

os.makedirs(os.path.dirname(arquivo_json), exist_ok=True)
with open(arquivo_json, 'w', encoding='utf-8') as f:
    json.dump([data_atual], f, ensure_ascii=False, indent=4)

arquivo_alteracoes = './Constituicao/alteracoes.json'
with open(arquivo_alteracoes, 'w', encoding='utf-8') as f:
    json.dump(json_alteracoes, f, ensure_ascii=False, indent=4)

if alteracoes:
    print("\n### ALTERAÇÕES DETECTADAS ###")
    for alteracao in alteracoes:
        print(alteracao)
else:
    print("\nNenhuma alteração detectada.")
