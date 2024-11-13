import requests
from bs4 import BeautifulSoup
from threading import Thread

# máxima cantidad de revisiones en cada catálogo
maxiSearch = 20

# URL base de la página
base_url = "https://books.toscrape.com/"

# obtener el HTML de la página inicial
response = requests.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')

# buscar el índice de categorías en la página
categories = soup.find('ul', class_='nav nav-list')

# extraer cada clasificación y enlace
categories_link = []
categories_name = []
for li in categories.find_all('li')[1:]:
    link = li.find('a')
    if link:
        href = link['href']  # enlace de la categoría
        namecat = link.get_text(strip=True)
        categories_link.append(base_url + href)  # agrega el link completo a la lista de enlaces
        categories_name.append(namecat)

# función para inspeccionar cada categoría y obtener los datos de cada producto
def inspCategorias(category_link):
    try:
        response = requests.get(category_link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # lista para almacenar los datos de cada libro
        product_list = []

        # encontrar todos los productos en la página
        products = soup.find_all('article', class_='product_pod')

        # extraer información de cada producto
        for product in products[:maxiSearch]:  # limitar por `maxiSearch`
            title = product.find('h3').find('a')['title']
            price = product.find('p', class_='price_color').text
            availability = product.find('p', class_='instock availability').text.strip()
            
            # agregar los datos del producto a la lista
            product_list.append({
                'title': title,
                'price': price,
                'availability': availability
            })
        
        return product_list

    except Exception as e:
        print(f"Error al procesar la categoría {category_link}: {e}")
        return []

# crear y manejar hilos para cada categoría
threads = []
for i in range(len(categories_link)):
    t = Thread(target=inspCategorias, args=(categories_link[i],))
    threads.append(t)
    t.start()

# esperar a que todos los hilos terminen
for t in threads:
    t.join()

# Ejemplo de cómo obtener e imprimir los resultados de cada categoría
for link in categories_link:
    products = inspCategorias(link)
    for product in products:
        print(f"Título: {product['title']}")
        print(f"Precio: {product['price']}")
        print(f"Disponibilidad: {product['availability']}")
        print("-" * 40)
