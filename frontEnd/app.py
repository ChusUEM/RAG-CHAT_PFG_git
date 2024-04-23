from flask import Flask, request, jsonify, render_template
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import openai
from urllib3.util.ssl_ import create_urllib3_context
import ssl
import os
import traceback
import urllib3

urllib3.disable_warnings()

# Establecer la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")


# Configuración de Elasticsearch
class ElasticsearchConnection:
    def __init__(self):
        context = create_urllib3_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        es_url = os.getenv("ELASTICSEARCH_URL")
        if not es_url:
            raise ValueError("ELASTICSEARCH_URL environment variable is not set")
        self.es = Elasticsearch(
            [es_url],
            basic_auth=(
                os.getenv("ELASTICSEARCH_USER"),
                os.getenv("ELASTICSEARCH_PASSWORD"),
            ),
            verify_certs=False,
        )


# Crear una instancia de la conexión a Elasticsearch
es_connection = ElasticsearchConnection()


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

        # Buscar los documentos más relevantes para la pregunta
        search = (
            Search(using=es_connection.es, index="rag-chat2-vectorized")
            .query("match", document=pregunta)
            .sort("_score")
        )
        # Ejecutar la búsqueda y obtener los documentos
        response = search[0:5].execute()
        print("Resultados más relevantes:")
        for hit in response:
            print(f"id: {hit.id} Título: {hit.title}")

        # Construir el contexto a partir de los documentos
        context = " ".join([hit.document for hit in response])

        # Generar una respuesta a partir de la pregunta y el contexto
        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": pregunta},
            ],
        )
        # Devolver el contenido de la respuesta
        return openai_response["choices"][0]["message"]["content"]

    # Manejar cualquier error que pueda ocurrir
    except Exception as e:
        print(f"Error generating response: {e}")
        return str({"error": str(e), "trace": e}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
