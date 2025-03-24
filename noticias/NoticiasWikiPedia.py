from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException,WebDriverException
from bs4 import BeautifulSoup
import json

service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

def get_g1_news():
    driver = None
    try:
        driver = webdriver.Edge(service=service, options=options)
        driver.get("https://g1.globo.com/")
        
        # Aceitar cookies (se necessário)
        try:
            cookie_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@id="cookie-banner-lgpd-accept"]'))
            )
            cookie_btn.click()
        except Exception:
            pass
        
        # Esperar carregamento das notícias
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bastian-page'))
        )
        # time.sleep(2)  # Espera para conteúdo dinâmico
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        news = []

        print(soup.select('div._evg'))
        
        # Extrair notícias principais
        # for article in soup.select('div.feed-post-body'):
            # try:
            #     title = article.select_one('a.feed-post-link').text.strip()
            #     link = article.select_one('a.feed-post-link')['href']
                
            #     # Extrair resumo (se existir)
            #     summary = article.select_one('div.feed-post-body-resumo')
            #     summary = summary.text.strip() if summary else ''
                
            #     # Extrair metadados
            #     time_element = article.select_one('span.feed-post-datetime')
            #     time = time_element.text.strip() if time_element else ''
                
            #     news.append({
            #         'titulo': title,
            #         'resumo': summary,
            #         'horario': time,
            #         'link': link
            #     })
                
            # except Exception as e:
            #     print(f"Erro ao processar artigo: {str(e)}")
            #     continue
        
        return news

    except WebDriverException as e:
        print(f"Erro no WebDriver: {str(e)}")
        return []
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return []
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    noticias = get_g1_news()
    print(f"Notícias encontradas: {len(noticias)}")
    
    with open("./noticias/noticias_g1.json", "w", encoding="utf-8") as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)
    
    print("Dados salvos em noticias_g1.json")