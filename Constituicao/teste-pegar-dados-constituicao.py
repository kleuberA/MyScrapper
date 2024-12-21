from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import time
import json
import re
from difflib import unified_diff

# Função para limpar o texto
def limpar_texto(texto):
    return re.sub(r'\s+', ' ', texto).strip()  # Remove quebras de linha e múltiplos espaços

# Função auxiliar para extrair texto, ignorando tags HTML
def extrair_texto(elemento):
    return limpar_texto(' '.join([t for t in elemento.stripped_strings]))

# Função para comparar diferenças entre dois textos
def verificar_diferencas(texto_antigo, texto_novo):
    diferencas = list(unified_diff(
        texto_antigo.splitlines(),
        texto_novo.splitlines(),
        lineterm='',
        fromfile='Texto Antigo',
        tofile='Texto Novo'
    ))
    return '\n'.join(diferencas)

# Configurações do Selenium WebDriver
service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

# URL da Constituição Federal do Brasil
url = 'https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm'
driver.get(url)

# Aguardar a página carregar completamente
time.sleep(3)

# Pegar o conteúdo da página
page_content = driver.page_source

# Analisar o conteúdo com BeautifulSoup
soup = BeautifulSoup(page_content, 'html.parser')

# Inicializar a lista de dados
data_atual = {
    "tipo": "Constituição da República Federativa do Brasil de 1988",
    "data": "",
    "todos_artigos": []
}

# Variáveis para armazenar o título atual, capítulos, seções e artigos
titulo_atual = None
nome_titulo = None
capitulo_atual = None
nome_capitulo = None
secao_atual = None
nome_secao = None
artigo_atual = None
artigos = []

# Função auxiliar para salvar capítulos e seções
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

# Encontrar todos os elementos <p>
paragrafos = soup.find_all('p')

# Modificação para capturar títulos, capítulos e seções de forma mais robusta e genérica
for i, p in enumerate(paragrafos):
    texto_elemento = extrair_texto(p)
    
    # Verifica se é um Título
    if re.search(r'TÍTULO [IVXLCDM]+', texto_elemento):
        # Salvar o capítulo, seção ou artigos anteriores
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        salvar_capitulo_ou_secao()
        
        # Iniciar novo Título
        titulo_atual = re.search(r'(TÍTULO [IVXLCDM]+)', texto_elemento).group(1)
        nome_titulo = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        if nome_titulo == titulo_atual:
            nome_titulo = ""

        capitulo_atual = None
        nome_capitulo = None
        secao_atual = None
        nome_secao = None
        artigos = []

    # Verifica se é um Capítulo
    elif re.search(r'CAPÍTULO [IVXLCDM]+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        salvar_capitulo_ou_secao()
        
        capitulo_atual = re.search(r'(CAPÍTULO [IVXLCDM]+)', texto_elemento).group(1)
        nome_capitulo = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        if nome_capitulo == capitulo_atual:
            nome_capitulo = ""

        secao_atual = None
        nome_secao = None
        artigos = []

    # Verifica se é uma Seção
    elif re.search(r'Seção [IVXLCDM]+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        salvar_capitulo_ou_secao()
        
        secao_atual = re.search(r'(Seção [IVXLCDM]+)', texto_elemento).group(1)
        nome_secao = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        artigos = []

    # Verifica se é um Artigo (começa com "Art.")
    elif re.match(r'Art\. \d+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
        
        artigo_atual = {
            "artigo": texto_elemento,
            "conteudo": []
        }

    # Caso o artigo já tenha sido iniciado, adiciona o conteúdo subsequente
    elif artigo_atual and not ('TÍTULO' in texto_elemento or 'CAPÍTULO' in texto_elemento or 'Seção' in texto_elemento):
        artigo_atual['conteudo'].append(texto_elemento)

# Adicionar o último conjunto de dados
if artigo_atual:
    artigos.append(artigo_atual)

# Salvar o último capítulo ou seção
salvar_capitulo_ou_secao()

# Nome do arquivo JSON
arquivo_json = './Constituicao/constituicao-dados.json'

# Carregar dados antigos, se existirem
if os.path.exists(arquivo_json):
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados_antigos = json.load(f)
else:
    dados_antigos = {"todos_artigos": []}

# Verificar se o JSON antigo é uma lista e ajustar
if isinstance(dados_antigos, list) and len(dados_antigos) > 0:
    dados_antigos = dados_antigos[0]
elif not isinstance(dados_antigos, dict):
    dados_antigos = {"todos_artigos": []}

# Processar artigos antigos e novos
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

# Lista para registrar alterações
alteracoes = []

# Checar por artigos novos ou alterados
for chave, artigo_novo in artigos_novos.items():
    artigo_antigo = artigos_antigos.get(chave)
    if not artigo_antigo:
        alteracoes.append(f"Novo artigo adicionado: {chave}")
    elif artigo_antigo['conteudo'] != artigo_novo['conteudo']:
        diferencas = verificar_diferencas(
            '\n'.join(artigo_antigo['conteudo']),
            '\n'.join(artigo_novo['conteudo'])
        )
        alteracoes.append(f"Artigo alterado: {chave}\nDiferenças:\n{diferencas}")

# Checar por artigos removidos
for chave in artigos_antigos.keys():
    if chave not in artigos_novos:
        alteracoes.append(f"Artigo removido: {chave}")

# Salvar o novo arquivo JSON
os.makedirs(os.path.dirname(arquivo_json), exist_ok=True)
with open(arquivo_json, 'w', encoding='utf-8') as f:
    json.dump([data_atual], f, ensure_ascii=False, indent=4)

# Exibir relatório de alterações
if alteracoes:
    print("Alterações detectadas no conteúdo:")
    for alteracao in alteracoes:
        print(alteracao)
else:
    print("Nenhuma alteração foi detectada no conteúdo.")
