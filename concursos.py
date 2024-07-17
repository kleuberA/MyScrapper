from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv
import json
import re

service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

url = 'https://concursosnobrasil.com/concursos/br/'
driver.get(url)

time.sleep(3)

page_content = driver.page_source

soup = BeautifulSoup(page_content, 'html.parser')

menu_estados = soup.find('ul', class_='menu-estados')

estados = menu_estados.find_all('li')

estados_links = [(estado.find('a').get_text(strip=True), estado.find('a')['href']) for estado in estados]

data = []

for estado_nome, estado_link in estados_links:
    if estado_nome != 'NACIONAL':
        driver.get(estado_link)
        time.sleep(3)
        
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')

        conteudo = soup.find('main', class_='taxonomy')
        
        header_title = ""
        header_subtitle = ""
        header = conteudo.find('header')
        if header:
            header_title_elem = header.find('h1')
            if header_title_elem:
                header_title = header_title_elem.get_text(strip=True)
            header_subtitle_elem = header.find('h2')
            if header_subtitle_elem:
                header_subtitle = header_subtitle_elem.get_text(strip=True)
        
        concursos_data = []
        tabela_concursos = conteudo.find('table')
        if tabela_concursos:
            concursos = tabela_concursos.find_all('tr')
            for concurso in concursos:
                cols = concurso.find_all('td')
                if len(cols) == 2: 
                    orgao = cols[0].get_text(strip=True)
                    vagas = cols[1].get_text(strip=True)
                    is_previsto = "previsto" in orgao.lower()

                    orgao = orgao.replace("previsto", "").strip()
                    concursos_data.append({"orgao": orgao, "vagas": vagas, "previsto": is_previsto})
        
        estado_data = {
            "estado": estado_nome,
            "titulo": header_title,
            "subtitulo": header_subtitle,
            "concursos": concursos_data
        }
        
        data.append(estado_data)

driver.quit() 

for estado in data:
    print(f"Estado: {estado['estado']}")
    print(f"Título: {estado['titulo']}")
    print(f"Subtítulo: {estado['subtitulo']}")
    for concurso in estado['concursos']:
        print(f"  Órgão: {concurso['orgao']}, Vagas: {concurso['vagas']}")

with open('concurso.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print('Dados extraídos e salvos em concurso.json')