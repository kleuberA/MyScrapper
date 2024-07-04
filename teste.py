from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

url = 'https://www.qconcursos.com/questoes-de-concursos/disciplinas'
driver.get(url)

page_number = 1

data_links = []

def fechar_propaganda():
    try:
        # Esperar até que o botão de fechar seja clicável (até 10 segundos)
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "interactive-close-button"))
        )
        close_button.click()
        print('Fechei a propaganda')
    except:
        print('Nenhuma propaganda encontrada ou não foi possível fechar')

while True:
    try:
        # Verificar e fechar a propaganda, se necessário
        fechar_propaganda()

        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        disciplinas = soup.find_all('div', class_='q-discipline-item')

        # Corrigir o método de obtenção do atributo 'href'
        disciplinas_links = [(disciplina.find('a').get_text(strip=True), disciplina.find('a')['href']) for disciplina in disciplinas]
        data_links.extend(disciplinas_links)

        # Esperar até que o link 'próxima' esteja presente e visível
        next_page = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[rel='next']"))
        )

        # Rolar até o elemento 'next' para garantir que seja clicável
        driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
        time.sleep(2)  # Esperar um pouco após o scroll

        # Clicar no link 'próxima'
        next_page.click()
        print(f'Cliquei no link para a próxima página: {page_number}')

        # Esperar até que a nova página carregue completamente
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "q-page-results-title"))
        )

        # Verificar se a página realmente mudou
        new_page_content = driver.page_source
        soup = BeautifulSoup(new_page_content, 'html.parser')
        if soup.find(class_="q-page-results-title"):
            print(f'Página {page_number} carregada com sucesso')
        else:
            print(f'Falha ao carregar a página {page_number}')
            break

        # Incrementar o número da página
        page_number += 1

        # Aguardar alguns segundos para garantir que a página mudou completamente
        time.sleep(2)  # Espera 2 segundos

    except:
        print(f'Link para a próxima página não encontrado. Última página alcançada ou erro.')
        break

data = []

for disciplina_nome, disciplina_link in data_links:
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
