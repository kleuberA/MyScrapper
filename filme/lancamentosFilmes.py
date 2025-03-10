from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import csv

service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

def get_imdb_lancamentos():
    driver.get("https://www.imdb.com/calendar/")
    driver.implicitly_wait(0.1)  
    
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, "html.parser")
    movie_list = soup.select(".ipc-page-section--base > article.sc-54f5ef07-1")

    for idx, movie in enumerate(movie_list, 1):
        title_element = movie.select('div > hgroup > h3.ipc-title__text')[0]
        title = title_element.get_text(strip=True)
        
        # Selecting the metadata list
        ul_element_list = movie.select('.ipc-metadata-list')
        for ul_element in ul_element_list:
            # Extract the <img> tag and its src attribute
            img_tag = ul_element.select('.ipc-metadata-list-summary-item img')
            if img_tag:
                img_src = img_tag[0].get('src')
                print(f"Image {idx}: {img_src}")
            name_movie_element = ul_element.select(".ipc-metadata-list-summary-item__t")[0]
            name_movie = name_movie_element.get_text(strip=True)
            print(f"Name Movie: {name_movie}")
        
        # Optionally, print the movie title
        print(f"Movie {idx}: {title}")

    driver.quit()

if __name__ == "__main__":
    get_imdb_lancamentos()
