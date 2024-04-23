from flask import Flask, request, jsonify
from elasticsearch_dsl import Search
import openai

app = Flask(__name__)


class ChatByFrontEnd:
    def __init__(self, es):
        self.es = es

    def generate_response_frontend(self, question):
        try:
            search = (
                Search(using=self.es, index="rag-chat2-vectorized")
                .query("match", document=question)
                .sort("_score")
            )
            response = search[0:5].execute()
            context = " ".join([hit.document for hit in response])
            openai_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": question},
                ],
            )
            return openai_response["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error generating response: {e}")
            return None


chat = ChatByFrontEnd(es)  # Asume que 'es' es tu cliente de Elasticsearch


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()
    question = data["question"]
    response = chat.generate_response_frontend(question)
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
