from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import json

service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

def get_products():
    driver.get("https://webscraper.io/test-sites/e-commerce/allinone")
    products = []
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_cards = soup.select('div.row > div.col-md-4')
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
    
    return products

if __name__ == "__main__":
    try:
        products = get_products()
        print(f"Total de produtos coletados: {len(products)}")
        
        # Salvar em JSON
        with open("./ecommerce-test/products.json", "w", encoding="utf-8") as file:
            json.dump(products, file, ensure_ascii=False, indent=4)
            
        print("Dados salvos em products.json")
        
    except Exception as e:
        print(f"Erro na execução: {str(e)}")