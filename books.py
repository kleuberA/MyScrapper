from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

service = Service()

options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

url = 'https://books.toscrape.com/'
driver.get(url)

books_list = []

books = driver.find_elements(By.CSS_SELECTOR, 'article.product_pod')

for book in books:
    title = book.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a').get_attribute('title')
    price = book.find_element(By.CLASS_NAME, 'price_color').text
    availability = book.find_element(By.CLASS_NAME, 'availability').text.strip()
    
    book_details = {
        'title': title,
        'price': price,
        'availability': availability
    }
    
    books_list.append(book_details)

next_page = driver.find_element(By.CLASS_NAME, 'next')

driver.quit()


print(books_list)
