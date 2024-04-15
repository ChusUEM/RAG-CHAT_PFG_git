"""# Unir todos los archivos json de searcher/etc/wepages en uno solo

import json
import os

# El directorio que contiene los archivos JSON
directorio = "searcher/etc/webpages"

# Un diccionario para almacenar los datos de todos los archivos JSON
datos = {}

# Enumera todos los archivos en el directorio
for nombre_archivo in os.listdir(directorio):
    # Asegúrate de que solo estás procesando archivos JSON
    if nombre_archivo.endswith(".json"):
        # Construye la ruta completa al archivo
        ruta_archivo = os.path.join(directorio, nombre_archivo)

        # Abre el archivo y carga los datos JSON
        with open(ruta_archivo, "r") as f:
            webpages = json.load(f)

        # Obtiene el nombre del archivo sin la extensión .json
        nombre_sin_extension = os.path.splitext(nombre_archivo)[0]

        # Agrega los datos del archivo al diccionario
        datos[nombre_sin_extension] = webpages

# Escribe todos los datos a un nuevo archivo JSON
with open("searcher/src/joiner/webpages.json", "w") as f:
    json.dump(datos, f)

# Crear un nuevo archivo JSON adaptado para elasticsearch
with open("searcher/src/joiner/elasticsearch_webpages.json", "w") as f:
    for doc_id, doc in datos.items():
        # Crear la línea de acción
        action = {"index": {"_index": "webpages", "_id": doc_id}}
        # Escribir la línea de acción y el documento en el nuevo archivo
        f.write(json.dumps(action) + "\n" + json.dumps(doc) + "\n")
"""

import os
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Descargar los conjuntos de datos de NLTK necesarios
nltk.download("punkt")
nltk.download("stopwords")


class Joiner:
    def join_jsons(self):
        # Obtén el directorio actual de trabajo
        directorio_actual = os.getcwd()
        # Une el directorio actual de trabajo con la ruta relativa
        directorio = os.path.join(directorio_actual, "etc/webpages")

        # Un diccionario para almacenar los datos de todos los archivos JSON
        datos = {}

        # Un contador para los ids de los documentos
        contador_id = 1

        # Enumera todos los archivos en el directorio
        for nombre_archivo in os.listdir(directorio):
            # Asegúrate de que solo estás procesando archivos JSON
            if nombre_archivo.endswith(".json"):
                # Construye la ruta completa al archivo
                ruta_archivo = os.path.join(directorio, nombre_archivo)

                # Abre el archivo y carga los datos JSON
                with open(ruta_archivo, "r") as f:
                    webpages = json.load(f)

                # Procesamiento del lenguaje natural y limpieza
                text = webpages["text"]
                tokens = word_tokenize(text)
                tokens = [word for word in tokens if word.isalpha()]
                stop_words = set(stopwords.words("spanish"))
                tokens = [word for word in tokens if not word in stop_words]

                # Obtiene el título omitiendo el inicio de la URL
                title = webpages["url"].replace(
                    "https://universidadeuropea.com/blog/", ""
                )

                # Almacena los datos limpios
                datos[nombre_archivo] = {
                    "id": contador_id,
                    "title": title,
                    "url": webpages["url"],
                    "text": " ".join(tokens),
                }

                # Incrementa el contador de ids
                contador_id += 1

        # Escribe todos los datos a un nuevo archivo JSON
        with open("etc/webpages_clean.json", "w") as f:
            json.dump(datos, f)
