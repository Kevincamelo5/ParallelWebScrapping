import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import threading

#se realiza la conexion con la pagina web
driver = "https://books.toscrape.com/index.html"

#obtener el html de la pagina 
catalogos = requests.get(driver)
soup = BeautifulSoup(catalogos.content, 'html.parser')

#busca el indice de la pagina
categories = soup.find('ul', class_='nav nav-list')

#extrae cada clasificacion y enlace
categories_link = []
li_items = soup.find_all('li')
for li in categories.find_all('li')[1:]:
    link = li.find('a')
    if link:
        catalogo = link.get_text(strip=True) #texto de la categoria
        href = link['href'] #Enlace de la cateroria
        categories_link.append(href)

#ingresar a cada categoria una por una