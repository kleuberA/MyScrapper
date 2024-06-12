from bs4 import BeautifulSoup
import requests

url = "https://www.dadosdemercado.com.br/acoes"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

dados = soup.find_all('table', class_='normal-table')

resultado = []

for dado in dados:
    rows = dado.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 1:
            Ticker = cols[0].text.strip()
            Nome = cols[1].text.strip()
            Negocios = cols[2].text.strip()
            Ultima = cols[3].text.strip()
            Variacao = cols[4].text.strip()
            resultado.append({'Ticker': Ticker, 'Nome': Nome, 'Negocios': Negocios, 'Ultima': Ultima, 'Variacao': Variacao})

print("Lista desordenada.")
for item in resultado:
    print(f"Ticker: {item['Ticker']}, Nome: {item['Nome']}, Negocios: {item['Negocios']}, Última (R$): {item['Ultima']}, Variação: {item['Variacao']}")
print('***************************************************')

resultado_ordenado = sorted(resultado, key=lambda x: x['Ultima'], reverse=True)

print("Lista das ações ordenadas, do maior para o menor do valor da coluna 'Última (R$)'.")
for acao in resultado_ordenado:
    print(f"Ticker: {acao['Ticker']}, Nome: {acao['Nome']}, Negocios: {acao['Negocios']}, Última (R$): {acao['Ultima']}, Variação: {acao['Variacao']}")