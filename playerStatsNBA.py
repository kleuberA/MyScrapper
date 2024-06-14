from bs4 import BeautifulSoup
import requests

url = "https://www.basketball-reference.com/leagues/NBA_2024_totals.html#totals_stats::pts"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table', class_='stats_table')
head_table = table.findAll('thead')


rows = table.find('tbody').find_all('tr')

data = []

for row in rows:
    if row.find('th', {"scope": "row"}) is None:
        continue
    
    cells = row.find_all('td')
    if len(cells) > 0:
        player_data = [cell.getText() for cell in cells]
        data.append(player_data)

print(data)