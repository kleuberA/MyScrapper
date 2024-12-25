from sklearn.feature_extraction.text import TfidfVectorizer
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from sklearn.ensemble import RandomForestClassifier
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import re
import os

def limpar_texto(texto):
    return re.sub(r'\s+', ' ', texto).strip()

def extrair_texto(elemento):
    return limpar_texto(' '.join([t for t in elemento.stripped_strings]))

app = FastAPI()

PASTA_JSON = "./Constituicao"
ARQUIVO_JSON = f"{PASTA_JSON}/constituicao-dados.json"
ARQUIVO_ALTERACOES = f"{PASTA_JSON}/alteracoes.json"

dados_exemplo = [
    ("TÍTULO I", "Título"),
    ("Dos Princípios Fundamentais", "Nome_Título"),
    ("CAPÍTULO II", "Capítulo"),
    ("Da Organização do Estado", "Nome_Capítulo"),
    ("Seção I", "Seção"),
    ("Dos Municípios", "Nome_Seção"),
    ("Art. 1º Esta é a redação do artigo", "Artigo"),
    ("§ 1º Este é o parágrafo de um artigo", "Conteúdo_Artigo"),
]

textos, labels = zip(*dados_exemplo)
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(textos)
y = labels

classifier = RandomForestClassifier(random_state=42)
classifier.fit(X, y)

@app.get("/scrape/")
def realizar_scraping(url: str):
    try:
        service = Service()
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--headless')

        driver = webdriver.Edge(service=service, options=options)
        driver.get(url)
        time.sleep(3) 

        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        driver.quit()

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

        os.makedirs(PASTA_JSON, exist_ok=True)
        primeira_execucao = not os.path.exists(ARQUIVO_JSON)

        alteracoes = []
        json_alteracoes = []

        if primeira_execucao:
            with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
                json.dump([data_atual], f, ensure_ascii=False, indent=4)
            return JSONResponse(content={"dados": data_atual, "alteracao": False})
        else:
            with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
                dados_antigos = json.load(f)[0]

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
                    json_alteracoes.append({"tipo": "novo", "artigo": chave, "conteudo_novo": artigo_novo["conteudo"]})
                elif artigo_antigo['conteudo'] != artigo_novo['conteudo']:
                    json_alteracoes.append({
                        "tipo": "alterado",
                        "artigo": chave,
                        "conteudo_antigo": artigo_antigo["conteudo"],
                        "conteudo_novo": artigo_novo["conteudo"]
                    })

            for chave in artigos_antigos.keys():
                if chave not in artigos_novos:
                    json_alteracoes.append({"tipo": "removido", "artigo": chave, "conteudo_antigo": artigos_antigos[chave]["conteudo"]})

        with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
            json.dump([data_atual], f, ensure_ascii=False, indent=4)

        with open(ARQUIVO_ALTERACOES, 'w', encoding='utf-8') as f:
            json.dump(json_alteracoes, f, ensure_ascii=False, indent=4)

        
        return JSONResponse(content={"dados": data_atual, "alteracoes": json_alteracoes, "alteracao": json_alteracoes != [] })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao realizar scraping: {str(e)}")