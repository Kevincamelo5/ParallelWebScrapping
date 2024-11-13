import requests
from bs4 import BeautifulSoup
from threading import Thread
import pymysql

# máxima cantidad de revisiones en cada catálogo
maxiSearch = 20

# URL base de la página
base_url = "https://books.toscrape.com/"

# obtener el HTML de la página inicial
response = requests.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')

# buscar el índice de categorías en la página
categories = soup.find('ul', class_='nav nav-list')

#conectarse con la base de datos
def conectar_db():
    try:
        conexion = pymysql.connect(
            host="localhost",
            user="root",   # Reemplaza con tu usuario de MySQL
            password="guest",  # Reemplaza con tu contraseña de MySQL
            database="StoreBooks"
        )
        return conexion
    except pymysql.MySQLError as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None
    
    # función para insertar datos en la tabla 'estante'
def insertar_libro_en_estante(conexion, titulo, precio, disponibilidad, genero, enlace):
    try:
        with conexion.cursor() as cursor:
            consulta = """
                INSERT INTO estante (titulo, precio, disponibilidad, genero, enlace)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(consulta, (titulo, precio, disponibilidad, genero, enlace))
            conexion.commit()
    except pymysql.MySQLError as e:
        print(f"Error al insertar en la tabla estante: {e}")

# extraer cada clasificación y enlace
categories_link = []
for li in categories.find_all('li')[1:]:
    link = li.find('a')
    if link:
        href = link['href']  # enlace de la categoría
        category_name = link.get_text(strip=True)  # nombre de la categoría
        categories_link.append({
            'name': category_name,
            'url': base_url + href
        })  # agrega un diccionario con el nombre y enlace de la categoría

# función para inspeccionar cada categoría y obtener los datos de cada producto
def inspCategorias(category):
    category_name = category['name']
    category_url = category['url']
    
    try:
        response = requests.get(category_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # lista para almacenar los datos de cada libro
        product_list = []

        # encontrar todos los productos en la página
        products = soup.find_all('article', class_='product_pod')

        # extraer información de cada producto
        for product in products[:maxiSearch]:  # limitar por maxiSearch
            title = product.find('h3').find('a')['title']
            price = product.find('p', class_='price_color').text
            availability = product.find('p', class_='instock availability').text.strip()
            book_link = base_url + "catalogue/" + product.find('h3').find('a')['href']
            
            # agregar los datos del producto a la lista, incluyendo la categoría
            product_list.append({
                'category': category_name,
                'title': title,
                'price': price,
                'availability': availability,
                'book_link': book_link
            })
        
        return product_list

    except Exception as e:
        print(f"Error al procesar la categoría {category_url}: {e}")
        return []

# crear y manejar hilos para cada categoría
threads = []
results = []  # lista para almacenar los resultados de cada hilo

# función para ejecutar y almacenar el resultado de cada hilo
def thread_function(category):
    products = inspCategorias(category)
    results.extend(products)

for category in categories_link:
    t = Thread(target=thread_function, args=(category,))
    threads.append(t)
    t.start()

# esperar a que todos los hilos terminen
for t in threads:
    t.join()

# imprimir los resultados
for product in results:
    print(f"Categoría: {product['category']}")
    print(f"Título: {product['title']}")
    print(f"Precio: {product['price']}")
    print(f"Disponibilidad: {product['availability']}")
    print(f"Enlace del libro: {product['book_link']}")
    print("-" * 40)