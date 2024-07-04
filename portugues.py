from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv

# Configurar o WebDriver do Edge
service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

url = 'https://www.qconcursos.com/questoes-de-concursos/disciplinas/direito-direito-constitucional'
driver.get(url)

time.sleep(5)

page_content = driver.page_source

driver.quit()

soup = BeautifulSoup(page_content, 'html.parser')

subject_group_list = soup.find('div', class_='q-subject-group-list')

if subject_group_list:
    subject_group_items = subject_group_list.find_all('div', class_='q-subject-group-item')
    
    data = []

    for item in subject_group_items:
        heading = item.find('div', class_='panel-heading')
        if heading:
            main_topic = heading.find('h2', class_='q-title').get_text(strip=True)
            
            nested_subjects_div = item.find('div', class_='q-nested-subjects')

            if nested_subjects_div:
                subtopics_ul = nested_subjects_div.find('ul', class_='list-group')
                
                if subtopics_ul:
                    subtopics_li = subtopics_ul.find_all('li', class_='list-group-item')
                    
                    for subtopic in subtopics_li:
                        subtopic_text = subtopic.find('h3', class_='q-title').get_text(strip=True)
                        data.append([main_topic, subtopic_text])
            else:
                data.append([main_topic, ""])
    print(data)

    with open('direito_constitucional_topics.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Main Topic', 'Subtopic'])
        writer.writerows(data)
    
    print('Dados extraídos e salvos em direito_constitucional_topics.csv')
else:
    print('Div com class "q-subject-group-list" não encontrada')
