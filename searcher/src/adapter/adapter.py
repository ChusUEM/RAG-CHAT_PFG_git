# Unir todos los archivos json de searcher/etc/wepages en uno solo

import json
import os

import nltk  # type: ignore
from nltk.corpus import stopwords  # type: ignore
from nltk.tokenize import word_tokenize  # type: ignore

# Descargar los conjuntos de datos de NLTK necesarios
nltk.download("punkt")
nltk.download("stopwords")


class Joiner:
    def join_jsons(
        self,
    ):  # Unifica todos los archivos json crawleados en "etc/webpages", en un único archivo llamado 'webpages_clean.json'.

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
                tokens = [word for word in tokens if word not in stop_words]

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
        with open("etc/webpages_clean/webpages_clean.json", "w") as f:
            json.dump(datos, f)


class PrepareJsonL:
    def __init__(self):
        pass

    def prepare_jsonL(
        self,
    ):  # Prepara el archivo'webpages_clean.json' (contenido de las webs crawleadas, parseado pero sin vectorizar) en el archivo 'webpages_clean.jsonl'.
        adapt_json(
            "etc/webpages_clean/webpages_clean.json",
            "etc/webpages_clean/webpages_clean.jsonl",
        )


def adapt_json(
    input_file, output_file
):  # Adapta un archivo formato 'json' en un archivo formato 'jsonl'.

    with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
        data = json.load(f_in)
        for filename, doc in data.items():
            new_doc = {
                key: doc[key]
                for key in ["id", "title", "url", "text"]
                if key in doc
            }
            metadata = {"index": {"_index": "rag-chat", "_id": new_doc["id"]}}
            f_out.write(json.dumps(metadata))
            f_out.write("\n")
            f_out.write(json.dumps(new_doc))
            f_out.write("\n")
