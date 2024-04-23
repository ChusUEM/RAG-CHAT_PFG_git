from flask import Flask, request, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

es = Elasticsearch(
    [{"host": "localhost", "port": 9200}]
)  # Asegúrate de reemplazar 'localhost' y '9200' con la dirección y el puerto de tu servidor Elasticsearch


@app.route("/api/chat", methods=["POST"])
def chat():
    question = request.json["question"]
    response = search_es(question)
    return jsonify(response=response)


def search_es(query):
    s = Search(
        using=es, index="my_index"
    )  # Asegúrate de reemplazar 'my_index' con el nombre de tu índice Elasticsearch
    s = s.query("match", message=query)
    response = s.execute()
    if response.hits:
        return response.hits[0].message  # Asume que la respuesta está en el primer hit
    else:
        return "No se encontró ninguna respuesta."


if __name__ == "__main__":
    app.run(
        port=5000
    )  # Asegúrate de reemplazar '5000' con el puerto en el que quieres que se ejecute tu servidor Flask
