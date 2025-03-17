from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup

service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

def get_quotes():
    driver.get("https://quotes.toscrape.com/")
    driver.implicitly_wait(1)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    quotes = []

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

    driver.quit()
    return quotes

if __name__ == "__main__":
    quotes = get_quotes()
    print(quotes)
