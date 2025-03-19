from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import json  # Adicione esta importação

service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

def get_quotes():
    driver.get("https://quotes.toscrape.com/")
    driver.implicitly_wait(1)
    quotes = []
    
    while True:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'quote'))
        )
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        element_quote = soup.select("div.col-md-8 > div.quote")
        
        for quote in element_quote:
            text = quote.select_one("span.text").get_text(strip=True)
            author = quote.select_one("small.author").get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote.select("a.tag")]
            quotes.append({
                "text": text,
                "author": author,
                "tags": tags
            })
        
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.next > a")
            next_button.click()
        except NoSuchElementException:
            break 
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'quote')))
        except TimeoutException:
            break  
    
    driver.quit()
    return quotes

if __name__ == "__main__":
    quotes = get_quotes()
    print(f"Total de citações coletadas: {len(quotes)}")
    
    # Salvar em JSON
    with open("./quote/quotes.json", "w", encoding="utf-8") as arquivo:
        json.dump(quotes, arquivo, ensure_ascii=False, indent=4)
    
    print("Arquivo 'quotes.json' gerado com sucesso!")