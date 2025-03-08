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

def get_imdb_top250():
    driver.get("https://www.imdb.com/chart/top/")
    driver.implicitly_wait(5)  
    
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, "html.parser")
    movie_list = soup.select("ul.ipc-metadata-list > li")

    if len(movie_list) == 0:
        print("Não conseguimos encontrar filmes. O seletor CSS pode estar incorreto ou a página não foi carregada corretamente.")
        driver.quit()
        return
    
    movies = []
    for idx, movie in enumerate(movie_list[:250], 1):
        try:
            title_element = movie.select_one("h3.ipc-title__text")
            title = title_element.get_text(strip=True).split(". ", 1)[1]
            
            metadata = movie.select("span.cli-title-metadata-item")
            year = metadata[0].get_text(strip=True) if len(metadata) > 0 else "N/A"
            duration = metadata[1].get_text(strip=True) if len(metadata) > 1 else "N/A"
            age_group = metadata[2].get_text(strip=True) if len(metadata) > 2 else "N/A"
            
            rating_element = movie.select_one("span.ipc-rating-star")
            rating_text = rating_element.get_text(strip=True)
            
            rating_part = rating_text.split('(')[0].strip() 
            votes_part = rating_text.split('(')[1].replace(')', '').strip() if '(' in rating_text else "0"  
            
            rating_part = rating_part.replace(',', '.')
            
            rating = float(rating_part)
            
            votes_part = votes_part.replace('\xa0', '').replace('mil', '').replace('mi', '').strip()  

            votes_part = votes_part.replace(',', '.')
            
            multiplier = 1
            if 'M' in votes_part:
                multiplier = 1_000_000
                votes_part = votes_part.replace('M', '')
            elif 'K' in votes_part:
                multiplier = 1_000
                votes_part = votes_part.replace('K', '')
            
            if 'mil' in votes_part or 'mi' in votes_part:
                votes_part = votes_part.replace('mil', '').replace('mi', '').strip()
                multiplier = 1000
            
            if votes_part:
                votes = int(float(votes_part) * multiplier)
            else:
                votes = 0
            
            movies.append({
                "rank": idx,
                "title": title,
                "year": year,
                "duration": duration,
                "AgeGroup": age_group,
                "rating": rating,
                "votes": votes
            })
        except Exception as e:
            print(f"Erro no filme {idx}: {str(e)}")
            continue

    if movies:
        with open("imdb_top250.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=movies[0].keys())
            writer.writeheader()
            writer.writerows(movies)
        print(f"Extraídos {len(movies)}/250 filmes com sucesso!")

    else:
        print("Nenhum filme foi extraído.")

    driver.quit()

if __name__ == "__main__":
    get_imdb_top250()
