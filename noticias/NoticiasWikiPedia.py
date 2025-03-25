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
        news_items = []

        # Encontrar todos os itens de notícia
        for item in soup.select('div.bastian-feed-item[data-type="materia"]'):
            try:
                # Extrair dados principais
                title_elem = item.select_one('a.feed-post-link')
                title = title_elem.text.strip() if title_elem else ''
                link = title_elem['href'] if title_elem else ''
                
                time_element = item.select_one('span.feed-post-datetime')
                time_text = time_element.text.strip() if time_element else ''
                
                section_element = item.select_one('span.feed-post-metadata-section')
                section = section_element.text.strip() if section_element else ''
                
                # Extrair imagem
                img_element = item.select_one('img.bstn-fd-picture-image')
                img_url = img_element['src'] if img_element else ''
                img_alt = img_element['alt'] if img_element else ''
                
                # Extrair conteúdo relacionado
                related = []
                for related_item in item.select('li.bstn-relateditem'):
                    related_title = related_item.select_one('a.bstn-relatedtext').text.strip()
                    related_link = related_item.select_one('a.bstn-relatedtext')['href']
                    related_time = related_item.select_one('span.feed-post-datetime').text.strip() if related_item.select_one('span.feed-post-datetime') else ''
                    
                    related.append({
                        'titulo_relacionado': related_title,
                        'link_relacionado': related_link,
                        'horario_relacionado': related_time
                    })

                news_items.append({
                    'titulo': title,
                    'link': link,
                    'horario': time_text,
                    'secao': section,
                    'imagem': {
                        'url': img_url,
                        'descricao': img_alt
                    },
                    'conteudo_relacionado': related
                })

            except Exception as e:
                print(f"Erro ao processar item: {str(e)}")
                continue

        return news_items

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