from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import re
import csv

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

# Encontrar todos os elementos <p>
paragrafos = soup.find_all('p')

# Variáveis para armazenar o título atual, capítulos e artigos
titulo_atual = None
nome_titulo = None
capitulo_atual = None
nome_capitulo = None
artigo_atual = None
artigos = []

# Filtrar e extrair o texto das tags <font> que contêm o texto "TÍTULO", "CAPÍTULO" e "Art."
for i, p in enumerate(paragrafos):
    texto_elemento = limpar_texto(p.get_text(strip=True))
    
    # Verifica se o elemento é um Título (contém "TÍTULO")
    if 'TÍTULO' in texto_elemento:
        # Salvar os dados do capítulo anterior
        if capitulo_atual or artigos:
            data.append({
                "titulo": titulo_atual,
                "nome_titulo": nome_titulo,
                "capitulo": capitulo_atual,
                "nome_capitulo": nome_capitulo,
                "artigos": artigos
            })
        # Iniciar novo Título
        titulo_atual = texto_elemento
        nome_titulo = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        capitulo_atual = None
        nome_capitulo = None
        artigos = []
        artigo_atual = None
    
    # Verifica se o elemento é um Capítulo (contém "CAPÍTULO")
    elif 'CAPÍTULO' in texto_elemento:
        # Salvar os dados do artigo anterior
        if artigo_atual:
            artigos.append(artigo_atual)
        if artigos:
            data.append({
                "titulo": titulo_atual,
                "nome_titulo": nome_titulo,
                "capitulo": capitulo_atual,
                "nome_capitulo": nome_capitulo,
                "artigos": artigos
            })
        
        # Iniciar novo Capítulo
        capitulo_atual = texto_elemento
        nome_capitulo = limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
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
        # Verifica se o conteúdo não contém "TÍTULO" ou "CAPÍTULO", para evitar captura incorreta
        if not ('TÍTULO' in texto_elemento or 'CAPÍTULO' in texto_elemento):
            artigo_atual['conteudo'].append(texto_elemento)

# Adicionar o último conjunto de dados
if artigo_atual:
    artigos.append(artigo_atual)

if artigos:
    data.append({
        "titulo": titulo_atual,
        "nome_titulo": nome_titulo,
        "capitulo": capitulo_atual,
        "nome_capitulo": nome_capitulo,
        "artigos": artigos
    })

driver.quit()  # Encerrar o WebDriver

# Salvar os dados em um arquivo JSON
with open('constituicao.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# Criar o arquivo CSV
with open('constituicao.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    
    # Escrever o cabeçalho
    csvwriter.writerow(['Título', 'Nome do Título', 'Capítulo', 'Nome do Capítulo', 'Artigo', 'Conteúdo'])

    # Preencher o CSV com os dados extraídos
    for item in data:
        titulo = item['titulo']
        nome_titulo = item['nome_titulo']
        capitulo = item['capitulo']
        nome_capitulo = item['nome_capitulo']
        for artigo in item['artigos']:
            artigo_numero = artigo['artigo']
            conteudo = " ".join(artigo['conteudo'])  # Unir o conteúdo em uma única string
            # Escrever os dados no CSV
            csvwriter.writerow([titulo, nome_titulo, capitulo, nome_capitulo, artigo_numero, conteudo])

print("Arquivos JSON e CSV criados com sucesso!")
