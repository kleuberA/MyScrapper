from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import csv

service = Service()

options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

url = 'https://books.toscrape.com/'
driver.get(url)

booksList = []

while True:
    books = driver.find_elements(By.CSS_SELECTOR, 'article.product_pod')
    
    for book in books:
        title = book.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a').get_attribute('title')
        price = book.find_element(By.CLASS_NAME, 'price_color').text
        availability = book.find_element(By.CLASS_NAME, 'availability').text.strip()
        
        bookDetails = {
            'title': title,
            'price': price,
            'availability': availability
        }
        
        booksList.append(bookDetails)
    
    try:
        nextButton = driver.find_element(By.CLASS_NAME, 'next')
        nextButton.find_element(By.TAG_NAME, 'a').click()
        time.sleep(2)
    except:
        break 

driver.quit()

name = 'books.csv'

campos = ['title', 'price', 'availability']

with open(name, mode='w', newline='', encoding='utf-8') as arquivoCsv:
    escritorCsv = csv.DictWriter(arquivoCsv, fieldnames=campos)
    
    escritorCsv.writeheader()
    
    escritorCsv.writerows(booksList)

print(f"Arquivo '{name}' criado com sucesso.")