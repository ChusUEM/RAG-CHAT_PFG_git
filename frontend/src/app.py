from flask import Flask, request, jsonify, render_template
import sys

sys.path.insert(0, "/Users/chus/Desktop/PFG/CODIGO_PFG/searcher/src/indexer/")
from indexer_front import Indexer

app = Flask(__name__)
indexer = Indexer()


@app.route("/")
def home():
    return render_template("form.html")


@app.route("/ask", methods=["POST"])
def ask():
    # Obtener la pregunta del cuerpo de la solicitud
    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Pasar la pregunta a generate_response y obtener la respuesta
    response = indexer.generate_response(question)

    # Devolver la respuesta en el cuerpo de la respuesta
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
