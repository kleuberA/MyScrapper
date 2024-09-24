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
url = 'https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm'
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

# Filtrar e extrair o texto das tags <font> e <small> que contêm o texto "CAPÍTULO" ou "Seção"
for i, p in enumerate(paragrafos):
    texto_elemento = limpar_texto(p.get_text(strip=True))
    
    # Verifica se o elemento é um Título (contém "TÍTULO")
    if 'TÍTULO' in texto_elemento:
        # Salvar os dados do capítulo ou seção anterior
        salvar_capitulo_ou_secao()
        
        # Iniciar novo Título
        titulo_atual = texto_elemento
        nome_titulo = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        capitulo_atual = None
        nome_capitulo = None
        secao_atual = None
        nome_secao = None
        artigos = []
        artigo_atual = None
    
    # Verifica se o elemento é um Capítulo, que está dentro de uma tag <small> ou <font>
    elif p.find('small') and 'CAPÍTULO' in p.find('small').get_text(strip=True):
        # Salvar os dados do artigo e capítulo ou seção anterior
        salvar_capitulo_ou_secao()
        
        # Iniciar novo Capítulo
        capitulo_atual = limpar_texto(p.find('small').get_text(strip=True))
        nome_capitulo = None
        secao_atual = None  # Resetar a seção quando um novo capítulo é encontrado
        nome_secao = None
        # Tentar encontrar o próximo <small> que contém o nome do capítulo
        small_elements = p.find_all('small')
        if len(small_elements) > 1:
            nome_capitulo = limpar_texto(small_elements[1].get_text(strip=True))
        
        artigos = []
        artigo_atual = None
    
    # Verifica se o elemento é uma Seção, que está dentro de uma tag <font> e <small>
    elif p.find('font') and p.find('small') and 'Seção' in p.find('small').get_text(strip=True):
        # Salvar os dados do artigo anterior, se houver
        salvar_capitulo_ou_secao()
        
        # Iniciar nova Seção
        secao_atual = limpar_texto(p.find('small').get_text(strip=True))
        nome_secao = None
        
        # Tentar encontrar o próximo <small> dentro do <font> que contém o nome da seção
        small_elements = p.find_all('small')
        if len(small_elements) > 1:
            nome_secao = limpar_texto(small_elements[1].get_text(strip=True))
        
        # Reiniciar a lista de artigos e a variável de artigo atual
        artigos = []
        artigo_atual = None

    # Verifica se o elemento é um Artigo (inicia com "Art.")
    elif re.match(r'Art\. \d+', texto_elemento):
        # Salvar o artigo anterior
        if artigo_atual:
            artigos.append(artigo_atual)
        
        # Iniciar novo Artigo
        artigo_atual = {
            "artigo": texto_elemento,
            "conteudo": []
        }
    
    # Caso o artigo já tenha sido iniciado, adicione o conteúdo subsequente
    elif artigo_atual:
        # Verifica se o conteúdo não contém "TÍTULO", "CAPÍTULO" ou "Seção", para evitar captura incorreta
        if not ('TÍTULO' in texto_elemento or 'CAPÍTULO' in texto_elemento or 'Seção' in texto_elemento):
            artigo_atual['conteudo'].append(texto_elemento)

# Adicionar o último conjunto de dados
if artigo_atual:
    artigos.append(artigo_atual)

# Salvar o último capítulo ou seção
salvar_capitulo_ou_secao()

data.append({
    "titulo": "ARQUIVO TESTE COD TRANSITO",
    "data": "05/10/1988",
    "todos_artigos": todos_artigos
})

driver.quit()  # Encerrar o WebDriver

# Salvar os dados em um arquivo JSON
with open('codtransito-teste2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Arquivo JSON criado com sucesso!")
