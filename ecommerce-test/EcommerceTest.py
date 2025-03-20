from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import json
import time

service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
# options.add_argument('--headless')  # Descomente para modo headless

driver = webdriver.Edge(service=service, options=options)

def get_products():
    driver.get("https://webscraper.io/test-sites/e-commerce/allinone")
    products = []
    
    try:
        while True:
            try:
                # Espera carregar os produtos
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'col-sm-4'))
                )

                soup = BeautifulSoup(driver.page_source, "html.parser")
                product_cards = soup.select('div.row > div')
                print(product_cards)
                
                for card in product_cards:
                    title = card.select_one('a.title').get_text(strip=True)
                    price = card.select_one('h4.price').get_text(strip=True)
                    description = card.select_one('p.description').get_text(strip=True)
                    rating = card.select_one('div.ratings p[data-rating]')['data-rating']
                    link = 'https://webscraper.io' + card.find('a')['href']
                    
                    products.append({
                        "title": title,
                        "price": price,
                        "description": description,
                        "rating": rating,
                        "link": link
                    })
                
            except (NoSuchElementException, TimeoutException):
                break

    except Exception as e:
        print(f"Erro durante o scraping: {str(e)}")
        
    finally:
        driver.quit()
    
    return products

if __name__ == "__main__":
    try:
        products = get_products()
        print(f"Total de produtos coletados: {len(products)}")
        print(products)
        
        # Salvar em JSON
        with open("./ecommerce-test/products.json", "w", encoding="utf-8") as file:
            json.dump(products, file, ensure_ascii=False, indent=4)
            
        print("Dados salvos em products.json")
        
    except Exception as e:
        print(f"Erro na execução: {str(e)}")