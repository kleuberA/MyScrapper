from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import re

# Função para limpar o texto
def limpar_texto(texto):
    return re.sub(r'\s+', ' ', texto).strip()  # Remove quebras de linha e múltiplos espaços

# Configurações do Selenium WebDriver
service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

# URL da Constituição Federal do Brasil
url = 'https://www.planalto.gov.br/ccivil_03/Leis/2002/L10406compilada.htm'
driver.get(url)

# Aguardar a página carregar completamente
time.sleep(3)

# Pegar o conteúdo da página
page_content = driver.page_source

# Analisar o conteúdo com BeautifulSoup
soup = BeautifulSoup(page_content, 'html.parser')

# Inicializar a lista de dados
data = []
todos_artigos = []

# Encontrar todos os elementos <p>
paragrafos = soup.find_all('p')

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
    if capitulo_atual and (secao_atual or artigos):
        todos_artigos.append({
            "titulo": titulo_atual,
            "nome_titulo": nome_titulo,
            "capitulo": capitulo_atual,
            "nome_capitulo": nome_capitulo,
            "secao": secao_atual,
            "nome_secao": nome_secao,
            "artigos": artigos
        })

# Modificação para capturar títulos, capítulos e seções com <br> separando as linhas
for i, p in enumerate(paragrafos):
    font_tags = p.find_all('font')
    
    # Verifica se existem tags <font> e processa conforme o caso
    if len(font_tags) > 0:
        texto_elemento = limpar_texto(font_tags[0].get_text(separator=" ", strip=True))

        # Verifica se é um Título
        if 'TÍTULO' in texto_elemento:
            # Salvar o capítulo ou seção anterior
            salvar_capitulo_ou_secao()
            
            # Iniciar novo Título
            titulo_atual = re.match(r'(TÍTULO [IVXLCDM]+)', texto_elemento).group(1) if re.match(r'(TÍTULO [IVXLCDM]+)', texto_elemento) else None
            nome_titulo = limpar_texto(font_tags[0].find_next('br').next_sibling.strip()) if font_tags[0].find_next('br') else None
            capitulo_atual = None
            nome_capitulo = None
            secao_atual = None
            nome_secao = None
            artigos = []
            artigo_atual = None

        # Verifica se é um Capítulo
        elif 'CAPÍTULO' in texto_elemento:
            # Salvar o capítulo ou seção anterior
            salvar_capitulo_ou_secao()
            
            # Iniciar novo Capítulo
            capitulo_atual = re.match(r'(CAPÍTULO [IVXLCDM]+)', texto_elemento).group(1) if re.match(r'(CAPÍTULO [IVXLCDM]+)', texto_elemento) else None
            nome_capitulo = limpar_texto(font_tags[0].find_next('br').next_sibling.strip()) if font_tags[0].find_next('br') else None
            secao_atual = None
            nome_secao = None
            artigos = []
            artigo_atual = None

        # Verifica se é uma Seção
        elif 'Seção' in texto_elemento:
            # Salvar o capítulo ou seção anterior
            salvar_capitulo_ou_secao()
            
            # Iniciar nova Seção
            secao_atual = re.match(r'(Seção [IVXLCDM]+)', texto_elemento).group(1) if re.match(r'(Seção [IVXLCDM]+)', texto_elemento) else None
            nome_secao = limpar_texto(font_tags[0].find_next('br').next_sibling.strip()) if font_tags[0].find_next('br') else None
            artigos = []
            artigo_atual = None

    # Verifica se é um Artigo (começa com "Art.")
    texto_elemento = limpar_texto(p.get_text(strip=True))
    if re.match(r'Art\. \d+', texto_elemento):
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

data.append({
    "titulo": "ARQUIVO TESTE COD CIVIL",
    "data": "",
    "todos_artigos": todos_artigos
})

driver.quit()  # Encerrar o WebDriver

# Salvar os dados em um arquivo JSON
with open('codcivil-teste.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Arquivo JSON criado com sucesso!")
