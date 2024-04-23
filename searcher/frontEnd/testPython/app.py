from flask import Flask, request, jsonify, render_template
from elasticsearch import Elasticsearch
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

        # Realizar una búsqueda en Elasticsearch
        resultado_elasticsearch = es_connection.es.search(
            index="rag-chat2-vectorized",
            body={"query": {"match": {"document": pregunta}}},
        )

        # Acceder a los documentos que coinciden con la consulta
        documentos_coincidentes = resultado_elasticsearch["hits"]["hits"]

        # Imprimir los documentos que coinciden con la consulta
        for doc in documentos_coincidentes:
            print(doc)

    except Exception as e:
        print(f"Error: {e}")
        tb = traceback.format_exc()
        return str({"error": str(e), "trace": tb}), 500

    # Procesamiento con la API de OpenAI
    try:
        respuesta_openai = openai.Completion.create(
            engine="davinci-002", prompt=pregunta, max_tokens=50
        )
        mejor_respuesta = respuesta_openai.choices[0].text.strip()
    except Exception as e:
        print(f"Error: {e}")
        tb = traceback.format_exc()
        return str({"error": str(e), "trace": tb}), 500

    # Devolver solo la respuesta de OpenAI como un string
    return mejor_respuesta


if __name__ == "__main__":
    app.run(debug=True, port=5001)
