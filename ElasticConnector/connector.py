# TEST TEST TEST TEST
# Conexión con docker de elasticsearch y kibana (ubicados en red docker)

import os
import json
from elasticsearch import Elasticsearch
from urllib3 import disable_warnings, exceptions

# Crear una conexión a Elasticsearch
disable_warnings(exceptions.InsecureRequestWarning)

es = Elasticsearch(
    ["https://localhost:9200/"], verify_certs=False
)  # Reemplaza "https://localhost:9200" con la dirección de tu Elasticsearch

# Usa es.options() para las opciones de transporte (si es necesario)
# opciones = es.options()
# opciones.use_ssl = False  # Ejemplo de opción

# Crear un índice
es.indices.create(index="my-index", ignore=400)

# Directorio donde se encuentran los archivos
directory = "searcher/etc/webpages"

# Leer y subir cada archivo en el directorio
for filename in os.listdir(directory):
    if filename.endswith(
        ".json"
    ):  # Asegúrate de que sólo estás leyendo los archivos que quieres (en este caso, .json)
        with open(os.path.join(directory, filename), "r") as file:
            data = json.load(file)

            # Subir los datos al índice
            res = es.index(index="my-index", body=data)
            print(f'Resultado de subir {filename}: {res["result"]}')
