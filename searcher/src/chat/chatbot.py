import os
import ssl

import openai  # type: ignore
from elasticsearch import Elasticsearch  # type: ignore
from elasticsearch_dsl import Search  # type: ignore
from elasticsearch_dsl import Q  # type: ignore
from joblib import load  # type: ignore
from urllib3.util.ssl_ import create_urllib3_context


class Chatbot:
    def __init__(self):
        # Cargar el vectorizador desde el archivo
        self.vectorizer = load("./etc/models/tfidf_vectorizer.joblib")
        self.pca = load("etc/models/pca.joblib")
        # Conexión con Elasticsearch
        context = create_urllib3_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        es_url = os.getenv("ELASTICSEARCH_URL")
        if not es_url:
            raise ValueError("ELASTICSEARCH_URL environment variable is not set")
        self.es = Elasticsearch(
            [es_url],
            http_auth=(
                os.getenv("ELASTICSEARCH_USER"),
                os.getenv("ELASTICSEARCH_PASSWORD"),
            ),
            verify_certs=False,
        )
        self.model = None
        self.dct = None

    # Transformar una pregunta en un vector
    def transform_question_to_vector(self, question):
        # Preprocesar la pregunta y convertirla en una bolsa de palabras
        question_bow = self.vectorizer.transform([question])

        # Transformar la bolsa de palabras en un vector TF-IDF
        question_vector = self.pca.transform(question_bow.toarray())

        # Convertir el vector en una lista de floats
        question_vector = question_vector[0].tolist()

        return question_vector

    def generate_response(self, question):
        # Verificar si la pregunta está vacía
        if not question.strip():
            return "Tienes que introducir alguna pregunta para obtener una respuesta..."
        try:
            # Transformar la pregunta en un vector
            question_vector = self.transform_question_to_vector(question)

            # Crear una consulta de similitud coseno
            s = Search(using=self.es, index="rag-chat_index").query(
                {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                            "params": {"query_vector": question_vector},
                        },
                    }
                }
            )

            # Ejecutar la consulta
            response = s.execute()

            # Obtener los 10 documentos con la puntuación más alta
            best_matches = response.hits[0:10]

            responses = []
            # Inicializar una lista vacía para almacenar los documentos
            documents = []

            # Limitar el número de matches a 3 para evitar alcanzar el límite de RPM
            for match in best_matches[:3]:
                # Obtener el contenido del documento
                document = match.document
                # Añadir el documento a la lista de documentos
                documents.append(document)

            # Concatenar los documentos en una sola cadena
            documents_str = " ".join(documents)

            # Utilizar OpenAI para generar una respuesta basada en los documentos
            openai_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Estás chateando con un asistente de IA que sabe mucho sobre muchos temas.",
                    },
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": documents_str},
                ],
            )

            responses.append(openai_response["choices"][0]["message"]["content"])

            return responses, best_matches[:3]

        except Exception as e:
            print(f"Error generating response: {e}")
            return None, None
