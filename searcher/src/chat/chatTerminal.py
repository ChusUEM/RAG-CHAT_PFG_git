from elastic_transport import SecurityWarning
import openai  # type: ignore
from elasticsearch_dsl import Search  # type: ignore
import os
import ssl
from elasticsearch import Elasticsearch  # type: ignore
from elasticsearch_dsl import Search  # type: ignore
from elasticsearch_dsl import Q  # type: ignore
from joblib import load  # type: ignore
from urllib3.util.ssl_ import create_urllib3_context
import warnings
from urllib3.exceptions import InsecureRequestWarning


class ChatTerminal:
    def __init__(self):
        # Cargar el vectorizador desde el archivo
        self.vectorizer = load("../../etc/models/tfidf_vectorizer.joblib")
        self.pca = load("../../etc/models/pca.joblib")
        # Conexión con Elasticsearch
        context = create_urllib3_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        es_url = os.getenv("ELASTICSEARCH_URL")
        if not es_url:
            raise ValueError("ELASTICSEARCH_URL environment variable is not set")
        # Ignora las advertencias de seguridad
        warnings.filterwarnings("ignore", category=SecurityWarning)

        # Ignora las advertencias de deprecación
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # Ignora las advertencias de solicitudes no seguras
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)
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
        self.question = input("\nPor favor, introduce tu pregunta: ")

    def transform_question_to_vector(self, question):
        question_bow = self.vectorizer.transform([question])
        question_vector = self.pca.transform(question_bow.toarray())
        question_vector = question_vector[0].tolist()
        return question_vector

    def generate_response(self):
        if not self.question.strip():
            return "Tienes que introducir alguna pregunta para obtener una respuesta..."
        try:
            question_vector = self.transform_question_to_vector(self.question)
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
            response = s.execute()
            best_matches = response.hits[0:10]
            document_url = []
            documents = []
            for match in best_matches[:3]:
                document_title = match.url  # Accede al atributo 'url' de match
                document_content = (
                    match.document
                )  # Accede al atributo 'document' de match
                document_url.append(document_title)
                documents.append(document_content)
            document_url_str = ", ".join(document_url)
            documents_str = " ".join(documents)
            openai_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Estás chateando con un asistente de IA que sabe mucho sobre muchos temas.",
                    },
                    {"role": "user", "content": self.question},
                    {"role": "assistant", "content": documents_str},
                ],
            )
            responses = openai_response["choices"][0]["message"]["content"]
            print("Pregunta recibida: ", self.question)
            print("Respuesta emitida:: ", responses)
            print("Para más información, consulta: ", document_url_str)
            return responses, best_matches[:3]

        except Exception as e:
            print(f"Error generating response: {e}")
            return None, None


chat = ChatTerminal()
chat.generate_response()
