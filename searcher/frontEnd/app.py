from flask import Flask, request, jsonify, render_template
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q
import openai
from urllib3.util.ssl_ import create_urllib3_context
import ssl
import os
import traceback
import urllib3
from src.indexer.indexer import (
    Indexer,
)  # Importar la clase Indexer de indexer.py

urllib3.disable_warnings()

# Establecer la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Crear una instancia de la conexión a Elasticsearch
es_connection = Indexer()  # Utilizar la clase Indexer para la conexión a Elasticsearch
es_connection.indexer()  # Llamar al método indexer para inicializar los atributos

app = Flask(__name__, static_folder="static")
app.debug = True


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/<path:path>")
def static_file(path):
    return app.send_static_file(path)


# Ruta para manejar la solicitud de búsqueda
@app.route("/buscar", methods=["POST"])
def buscar_respuesta():
    try:
        data = request.get_json()
        pregunta = data["pregunta"]
        print(f"Pregunta recibida: {pregunta}")

        # Utilizar el método generate_response de la clase Indexer para generar la respuesta y obtener relevant_doc_info
        respuesta, relevant_doc_info = es_connection.generate_response(pregunta)
        print(f"Documentos para la respuesta: {relevant_doc_info}")
        # Devolver el contenido de la respuesta
        return respuesta

    # Manejar cualquier error que pueda ocurrir
    except Exception as e:
        print(f"Error generating response: {e}")
        return str({"error": str(e), "trace": e}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
