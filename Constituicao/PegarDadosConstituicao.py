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

# Função auxiliar para extrair texto, ignorando tags HTML
def extrair_texto(elemento):
    return limpar_texto(' '.join([t for t in elemento.stripped_strings]))

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
        
        # Captura o nome do título, ignorando o formato
        nome_titulo = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        
        # Garantir que o nome do título não seja igual ao título
        if nome_titulo == titulo_atual:
            nome_titulo = ""

        capitulo_atual = None
        nome_capitulo = None
        secao_atual = None
        nome_secao = None
        artigos = []

    # Verifica se é um Capítulo
    elif re.search(r'CAPÍTULO [IVXLCDM]+', texto_elemento):
        # Salvar o capítulo, seção ou artigos anteriores
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        salvar_capitulo_ou_secao()
        
        # Iniciar novo Capítulo
        capitulo_atual = re.search(r'(CAPÍTULO [IVXLCDM]+)', texto_elemento).group(1)
        
        # Captura o nome do capítulo, ignorando o formato
        nome_capitulo = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        
        # Garantir que o nome do capítulo não seja igual ao capítulo
        if nome_capitulo == capitulo_atual:
            nome_capitulo = ""

        secao_atual = None
        nome_secao = None
        artigos = []

    # Verifica se é uma Seção
    elif re.search(r'Seção [IVXLCDM]+', texto_elemento):
        # Salvar o capítulo, seção ou artigos anteriores
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        salvar_capitulo_ou_secao()
        
        # Iniciar nova Seção
        secao_atual = re.search(r'(Seção [IVXLCDM]+)', texto_elemento).group(1)
        
        # Captura o nome da seção, ignorando o formato
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

data.append({
    "tipo": "Constituição da República Federativa do Brasil de 1988",
    "data": "",
    "todos_artigos": todos_artigos
})

driver.quit()  # Encerrar o WebDriver

# Salvar os dados em um arquivo JSON
with open('./Constituicao/constituicao-dados.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Arquivo JSON criado com sucesso!")
