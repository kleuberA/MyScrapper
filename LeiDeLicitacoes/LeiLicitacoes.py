from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import re

def limpar_texto(texto):
    return re.sub(r'\s+', ' ', texto).strip() 

def extrair_texto(elemento):
    for strike_tag in elemento.find_all('strike'):
        strike_tag.decompose() 
    
    return limpar_texto(' '.join([t for t in elemento.stripped_strings]))
    # return limpar_texto(' '.join([t for t in elemento.stripped_strings]))

service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

url = 'https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm'
driver.get(url)

time.sleep(3)

page_content = driver.page_source

soup = BeautifulSoup(page_content, 'html.parser')

data = []
todos_artigos = []

paragrafos = soup.find_all('p')

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
        todos_artigos.append({
            "titulo": titulo_atual,
            "nome_titulo": nome_titulo,
            "capitulo": capitulo_atual,
            "nome_capitulo": nome_capitulo,
            "secao": secao_atual,
            "nome_secao": nome_secao,
            "artigos": artigos
        })

for i, p in enumerate(paragrafos):
    texto_elemento = extrair_texto(p)
    
    if re.search(r'TÍTULO [IVXLCDM]+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        salvar_capitulo_ou_secao()
        
        titulo_atual = re.search(r'(TÍTULO [IVXLCDM]+)', texto_elemento).group(1)
        
        nome_titulo = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        
        if nome_titulo == titulo_atual:
            nome_titulo = ""

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
        
        if nome_capitulo == capitulo_atual:
            nome_capitulo = ""

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
        
        artigo_atual = {
            "artigo": texto_elemento,
            "conteudo": []
        }

    elif artigo_atual and not ('TÍTULO' in texto_elemento or 'CAPÍTULO' in texto_elemento or 'Seção' in texto_elemento):
        artigo_atual['conteudo'].append(texto_elemento)

if artigo_atual:
    artigos.append(artigo_atual)

salvar_capitulo_ou_secao()

data.append({
    "tipo": "LEI Nº 14.133 - Lei de Licitações e Contratos Administrativos",
    "todos_artigos": todos_artigos
})

driver.quit() 

with open('./LeiDeLicitacoes/leiLicitacoes-dados.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Arquivo JSON criado com sucesso!")
