from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import re

def limpar_texto(texto):
    return re.sub(r'\s+', ' ', texto).strip()

service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

url = 'https://www.planalto.gov.br/CCIVIL_03/Decreto-Lei/Del2848compilado.htm'
driver.get(url)

time.sleep(3)

page_content = driver.page_source

soup = BeautifulSoup(page_content, 'html.parser')

data = []
todos_artigos = []

paragrafos = soup.find_all('p')

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
epigrafe_atual = None  # Variável para armazenar a epígrafe
parte_atual = None  # Variável para armazenar a parte (Geral ou Especial)

def salvar_capitulo_ou_secao():
    if artigos:
        todos_artigos.append({
            "parte": parte_atual,  # Adiciona a parte atual ao artigo
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

def extrair_conteudo_apos_br(elemento):
    br_tag = elemento.find('br')
    if br_tag and br_tag.next_sibling:
        return limpar_texto(br_tag.next_sibling.get_text(strip=True) if br_tag.next_sibling.name else str(br_tag.next_sibling))
    return None

for i, p in enumerate(paragrafos):
    texto_elemento = limpar_texto(p.get_text(separator=" ", strip=True))
    
    if p.find('b') and p.find('font'): 
        epigrafe_atual = limpar_texto(p.get_text(separator=" ", strip=True))
    
    # Detectar a parte (Geral ou Especial)
    if re.match(r'PARTE (GERAL|ESPECIAL)', texto_elemento, re.IGNORECASE):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        
        salvar_capitulo_ou_secao()
        
        parte_atual = re.search(r'(PARTE (GERAL|ESPECIAL))', texto_elemento,re.IGNORECASE).group(1)
        print('PARTE ATUAL: ' , parte_atual)

    elif re.search(r'LIVRO [IVXLCDM]+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None
        
        salvar_capitulo_ou_secao()
        
        livro_atual = re.search(r'(LIVRO [IVXLCDM]+)', texto_elemento).group(1)
        nome_livro = extrair_conteudo_apos_br(p) or texto_elemento.replace(livro_atual, '').strip() or limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        titulo_atual = None
        nome_titulo = None
        capitulo_atual = None
        nome_capitulo = None
        secao_atual = None
        nome_secao = None
        subsecao_atual = None
        nome_subsecao = None
        artigos = []

    elif re.search(r'(TÍTULO (ÚNICO|[IVXLCDM]+))', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None

        salvar_capitulo_ou_secao()

        titulo_atual = re.search(r'(TÍTULO (ÚNICO|[IVXLCDM]+))', texto_elemento).group(1)
        nome_titulo = extrair_conteudo_apos_br(p) or texto_elemento.replace(titulo_atual, '').strip() or limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        capitulo_atual = None
        nome_capitulo = None
        secao_atual = None
        nome_secao = None
        subsecao_atual = None
        nome_subsecao = None
        artigos = []

    elif re.search(r'CAPÍTULO [IVXLCDM]+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None

        salvar_capitulo_ou_secao()

        capitulo_atual = re.search(r'(CAPÍTULO [IVXLCDM]+)', texto_elemento).group(1)
        nome_capitulo = extrair_conteudo_apos_br(p) or texto_elemento.replace(capitulo_atual, '').strip() or limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        secao_atual = None
        nome_secao = None
        subsecao_atual = None
        nome_subsecao = None
        artigos = []

    elif re.search(r'Seção [IVXLCDM]+', texto_elemento, re.IGNORECASE):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None

        salvar_capitulo_ou_secao()

        secao_atual = re.search(r'(Seção [IVXLCDM]+)', texto_elemento, re.IGNORECASE).group(1)
        nome_secao = extrair_conteudo_apos_br(p) or texto_elemento.replace(secao_atual, '').strip() or limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        subsecao_atual = None
        nome_subsecao = None
        artigos = []
    
    elif re.search(r'Subseção [IVXLCDM]+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)
            artigo_atual = None

        salvar_capitulo_ou_secao()

        subsecao_atual = re.search(r'(Subseção [IVXLCDM]+)', texto_elemento).group(1)
        nome_subsecao = extrair_conteudo_apos_br(p) or texto_elemento.replace(subsecao_atual, '').strip() or limpar_texto(paragrafos[i + 1].get_text(strip=True)) if i + 1 < len(paragrafos) else None
        artigos = []

    elif re.match(r'Art\. \d+', texto_elemento):
        if artigo_atual:
            artigos.append(artigo_atual)

        # Format the article to change "Art. Xº" to "Art. X°" and remove any trailing hyphen
        artigo_formatado = re.sub(r'Art\.\s*(\d+)\º', r'Art. \1°', texto_elemento).replace(" -", "")

        # Armazena a epígrafe com o artigo atual
        artigo_atual = {
            "artigo": artigo_formatado,  # Use the formatted article
            "conteudo": [],
            "epigrafe": epigrafe_atual  # Associa a epígrafe ao artigo
        }
        epigrafe_atual = None  # Limpa a epígrafe logo após salvar no artigo

    # ...

    elif artigo_atual and not ('TÍTULO' in texto_elemento or 'CAPÍTULO' in texto_elemento or 'Seção' in texto_elemento):
        # Adiciona o conteúdo ao artigo atual, mas só se não for epígrafe
        # Remove any leading or trailing hyphen before adding content
        conteudo_formatado = limpar_texto(texto_elemento).replace(" -", "")
        artigo_atual['conteudo'].append(conteudo_formatado)


if artigo_atual:
    artigos.append(artigo_atual)

salvar_capitulo_ou_secao()

data.append({
    "tipo": "Código Penal",
    "todos_artigos": todos_artigos
})

driver.quit()

with open('./CodigoPenal/codigo-penal-dados.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Arquivo JSON criado com sucesso!")
