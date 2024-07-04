from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv
import json
import re

# Configurar o WebDriver do Edge
service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

# Acessar a página principal de disciplinas
url = 'https://www.qconcursos.com/questoes-de-concursos/disciplinas'
driver.get(url)

time.sleep(5)

page_content = driver.page_source

soup = BeautifulSoup(page_content, 'html.parser')

disciplinas = soup.find_all('div', class_='q-discipline-item')

# Corrigir o método de obtenção do atributo 'href'
disciplinas_links = [(disciplina.find('a').get_text(strip=True), disciplina.find('a')['href']) for disciplina in disciplinas]

data = []

for disciplina_nome, disciplina_link in disciplinas_links:
    driver.get('https://www.qconcursos.com' + disciplina_link)
    time.sleep(5)
    
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')

    subject_group_list = soup.find('div', class_='q-subject-group-list')

    if subject_group_list:
        subject_group_items = subject_group_list.find_all('div', class_='q-subject-group-item')

        discipline_data = {"Discipline": disciplina_nome, "Topics": []}

        for item in subject_group_items:
            heading = item.find('div', class_='panel-heading')
            if heading:
                main_topic = heading.find('h2', class_='q-title').get_text(strip=True)
                
                nested_subjects_div = item.find('div', class_='q-nested-subjects')

                topic_data = {"Main Topic": main_topic, "Subtopics": []}

                if nested_subjects_div:
                    subtopics_ul = nested_subjects_div.find('ul', class_='list-group')
                    
                    if subtopics_ul:
                        subtopics_li = subtopics_ul.find_all('li', class_='list-group-item')
                        
                        for subtopic in subtopics_li:
                            subtopic_text = subtopic.find('h3', class_='q-title').get_text(strip=True)
                            # Adicionar espaço entre número e texto
                            subtopic_text = re.sub(r'(\d+\.\d+)([A-Za-z])', r'\1 \2', subtopic_text)
                            topic_data["Subtopics"].append(subtopic_text)
                
                discipline_data["Topics"].append(topic_data)

        data.append(discipline_data)

# Fechar o navegador
driver.quit()

print(data)

# Salvar os dados em um arquivo CSV
with open('disciplinas_topics.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Discipline', 'Main Topic', 'Subtopics'])
    for discipline in data:
        for topic in discipline["Topics"]:
            writer.writerow([discipline["Discipline"], topic["Main Topic"], ", ".join(topic["Subtopics"])])

print('Dados extraídos e salvos em disciplinas_topics.csv')

# Salvar os dados em um arquivo JSON
with open('disciplinas_topics.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print('Dados extraídos e salvos em disciplinas_topics.json')
