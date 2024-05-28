from flask import Flask, request, jsonify, render_template
from elasticsearch import Elasticsearch
import openai  # type: ignore
from urllib3.util.ssl_ import create_urllib3_context
import os
import urllib3

# Importar la clase Chatbot de chatbot.py
from src.chat.chatbot import (
    Chatbot,
)

urllib3.disable_warnings()

# Establecer la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Crear una instancia de la conexión a Elasticsearch
es_connection = Chatbot()  # Utilizar la clase Chatbot para la conexión a Elasticsearch

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

        # Llamar al método transform_question_to_vector con la pregunta del usuario
        es_connection.transform_question_to_vector(pregunta)
        # Utilizar el método generate_response de la clase Chatbot para generar la respuesta y obtener relevant_doc_info
        respuesta, relevant_docs_info = es_connection.generate_response(pregunta)

        # Convertir los objetos Hit en diccionarios que solo contienen el título
        relevant_docs_info = [
            {
                "title": doc["title"],
            }
            for doc in relevant_docs_info
        ]

        print(f"Documentos para la respuesta: {relevant_docs_info}")

        # Devolver el contenido de la respuesta y los enlaces en un objeto JSON
        return jsonify({"respuesta": respuesta, "enlaces": relevant_docs_info})

    # Manejar cualquier error que pueda ocurrir
    except Exception as e:
        print(f"Error generating response: {e}")
        return str({"error": str(e), "trace": e}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
