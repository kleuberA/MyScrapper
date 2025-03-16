from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from collections import Counter

service = Service()
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Edge(service=service, options=options)

def get_imdb_lancamentos():
    driver.get("https://www.imdb.com/calendar/")
    driver.implicitly_wait(1)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    movies = []

    for article in soup.select(".ipc-page-section--base > article.sc-54f5ef07-1"):
        title_element = article.select_one('h3.ipc-title__text')
        title = title_element.get_text(strip=True) if title_element else "Sem título"

        movie_list_ul = article.select_one("ul.ipc-metadata-list--base")

        if not movie_list_ul:
            continue 

        for movie_li in movie_list_ul.select("li.ipc-metadata-list-summary-item"):
            name_element = movie_li.select_one(".ipc-metadata-list-summary-item__t")
            name = name_element.get_text(strip=True) if name_element else "Sem nome"

            img_tag = movie_li.select_one("img.ipc-image")
            img_src = img_tag["src"] if img_tag else None

            categories = [
                cat.get_text(strip=True) 
                for cat in movie_li.select("ul.ipc-metadata-list-summary-item__tl > li.ipc-inline-list__item > span.ipc-metadata-list-summary-item__li")
            ]

            actors = [
                actor.get_text(strip=True)
                for actor in movie_li.select("ul.ipc-metadata-list-summary-item__stl > li.ipc-inline-list__item > span.ipc-metadata-list-summary-item__li")
            ]

            movies.append({
                "date_section": title,
                "name": name,
                "image": img_src,
                "categories": categories,
                "actors": actors
            })

    driver.quit()
    return movies

def contar_categorias(movies):
    todas_categorias = []
    for movie in movies:
        todas_categorias.extend(movie['categories'])
    
    categoria_contagem = Counter(todas_categorias)
    
    return categoria_contagem

if __name__ == "__main__":
    movies = get_imdb_lancamentos()
    
    categoria_contagem = contar_categorias(movies)
    
    print("Categorias mais comuns:")
    for categoria, quantidade in categoria_contagem.most_common():
        print(f"{categoria}: {quantidade} vezes")
    
    for movie in movies:
        print(f"Seção: {movie['date_section']}")
        print(f"Filme: {movie['name']}")
        print(f"Categorias: {movie['categories']}")
        print(f"Atores: {movie['actors']}")
        print(f"Imagem: {movie['image']}")
        print("-" * 50)
