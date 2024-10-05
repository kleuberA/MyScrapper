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

# URL do Código Civil
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
livro_atual = None
nome_livro = None
titulo_atual = None
nome_titulo = None
capitulo_atual = None
nome_capitulo = None
secao_atual = None
nome_secao = None
subsecao_atual = None
nome_subsecao = None
artigo_atual = None
artigos = []

# Função auxiliar para salvar capítulos e seções
def salvar_capitulo_ou_secao():
    if artigos:
        todos_artigos.append({
            "livro": livro_atual,
            "nome_livro": nome_livro,
            "titulo": titulo_atual,
            "nome_titulo": nome_titulo,
            "capitulo": capitulo_atual,
            "nome_capitulo": nome_capitulo,
            "secao": secao_atual,
            "nome_secao": nome_secao,
            "subsecao": subsecao_atual,
            "nome_subsecao": nome_subsecao,
            "artigos": artigos
        })

# Função auxiliar para extrair o próximo conteúdo após uma quebra de linha <br>
def extrair_conteudo_apos_br(elemento):
    br_tag = elemento.find('br')
    if br_tag and br_tag.next_sibling:
        return limpar_texto(br_tag.next_sibling.get_text(strip=True) if br_tag.next_sibling.name else str(br_tag.next_sibling))
    return None

# Modificação para capturar títulos, capítulos e seções com <br> ou outras variações
for i, p in enumerate(paragrafos):
    texto_elemento = limpar_texto(p.get_text(separator=" ", strip=True))
    
    if re.search(r'LIVRO [IVXLCDM]+', texto_elemento):
        # Salvar o artigo em andamento antes de redefinir as variáveis
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        
        # Salvar a estrutura anterior
        salvar_capitulo_ou_secao()
        
        # Iniciar novo Livro
        livro_atual = re.search(r'(LIVRO [IVXLCDM]+)', texto_elemento).group(1)
        nome_livro = extrair_conteudo_apos_br(p) or texto_elemento.replace(livro_atual, '').strip()
        titulo_atual = None
        nome_titulo = None
        capitulo_atual = None
        nome_capitulo = None
        secao_atual = None
        nome_secao = None
        subsecao_atual = None
        nome_subsecao = None
        artigos = []

    # Verifica se é um Título
    elif re.search(r'TÍTULO [IVXLCDM]+', texto_elemento):
        # Salvar o artigo em andamento antes de redefinir as variáveis
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None

        # Salvar a estrutura anterior
        salvar_capitulo_ou_secao()

        # Iniciar novo Título
        titulo_atual = re.search(r'(TÍTULO [IVXLCDM]+)', texto_elemento).group(1)
        nome_titulo = extrair_conteudo_apos_br(p) or texto_elemento.replace(titulo_atual, '').strip()
        capitulo_atual = None
        nome_capitulo = None
        secao_atual = None
        nome_secao = None
        subsecao_atual = None
        nome_subsecao = None
        artigos = []

    # Verifica se é um Capítulo
    elif re.search(r'CAPÍTULO [IVXLCDM]+', texto_elemento):
        # Salvar o artigo em andamento antes de redefinir as variáveis
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None

        # Salvar a estrutura anterior
        salvar_capitulo_ou_secao()

        # Iniciar novo Capítulo
        capitulo_atual = re.search(r'(CAPÍTULO [IVXLCDM]+)', texto_elemento).group(1)
        nome_capitulo = extrair_conteudo_apos_br(p) or texto_elemento.replace(capitulo_atual, '').strip()
        secao_atual = None
        nome_secao = None
        subsecao_atual = None
        nome_subsecao = None
        artigos = []

    # Verifica se é uma Seção
    elif re.search(r'Seção [IVXLCDM]+', texto_elemento):
        # Salvar o artigo em andamento antes de redefinir as variáveis
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None

        # Salvar a estrutura anterior
        salvar_capitulo_ou_secao()

        # Iniciar nova Seção
        secao_atual = re.search(r'(Seção [IVXLCDM]+)', texto_elemento).group(1)
        nome_secao = extrair_conteudo_apos_br(p) or texto_elemento.replace(secao_atual, '').strip()
        subsecao_atual = None
        nome_subsecao = None
        artigos = []
    
    # Verifica se é uma Subseção
    elif re.search(r'Subseção [IVXLCDM]+', texto_elemento):
        # Salvar o artigo em andamento antes de redefinir as variáveis
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None

        # Salvar a estrutura anterior
        salvar_capitulo_ou_secao()

        # Iniciar nova Subseção
        subsecao_atual = re.search(r'(Subseção [IVXLCDM]+)', texto_elemento).group(1)
        nome_subsecao = extrair_conteudo_apos_br(p) or texto_elemento.replace(subsecao_atual, '').strip()
        artigos = []

    # Verifica se é um Artigo (começa com "Art.")
    elif re.match(r'Art\. \d+', texto_elemento):
        # Salvar o artigo anterior antes de começar um novo
        if artigo_atual:
            artigos.append(artigo_atual)
        
        artigo_atual = {
            "artigo": texto_elemento,
            "conteudo": []
        }

    # Caso o artigo já tenha sido iniciado, adiciona o conteúdo subsequente
    elif artigo_atual and not ('TÍTULO' in texto_elemento or 'CAPÍTULO' in texto_elemento or 'Seção' in texto_elemento):
        artigo_atual['conteudo'].append(texto_elemento)

# Adicionar o último artigo, se houver
if artigo_atual:
    artigos.append(artigo_atual)

# Salvar o último capítulo ou seção
salvar_capitulo_ou_secao()

data.append({
    "tipo": "Código Civil",
    "todos_artigos": todos_artigos
})

driver.quit()  # Encerrar o WebDriver

# Salvar os dados em um arquivo JSON
with open('./CodigoCivil/codcivil-dados-teste.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Arquivo JSON criado com sucesso!")
