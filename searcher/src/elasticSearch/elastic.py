# Preparar el archivo etc/webpages_clean.json para la indexación en elasticsearch.
import json


class Elastic:
    def __init__(self):
        pass

    def prepare_elastic(self):
        """Construye el índice en Elasticsearch (contenido de las webs crawleadas, parseado pero sin vectorizar) utilizando los archivos JSON especificados.

        Parámetros:

        json_file: La ruta al archivo JSON que contiene los datos de las páginas web.
        jsonl_file: La ruta al archivo JSONL para almacenar los datos preparados.
        Devuelve: Nada"""
        elastic_index("etc/webpages_clean.json", "etc/webpages_clean.jsonl")


def elastic_index(input_file, output_file):
    with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
        data = json.load(f_in)
        for filename, doc in data.items():
            new_doc = {
                key: doc[key] for key in ["id", "title", "url", "text"] if key in doc
            }
            metadata = {"index": {"_index": "rag-chat", "_id": new_doc["id"]}}
            f_out.write(json.dumps(metadata))
            f_out.write("\n")
            f_out.write(json.dumps(new_doc))
            f_out.write("\n")
