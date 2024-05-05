# Importar las librerías necesarias
import ssl
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q
from elasticsearch_dsl import Search
import os
from urllib3 import disable_warnings, exceptions
import jsonlines
from urllib3.util.ssl_ import create_urllib3_context
import urllib3
import openai
from gensim.corpora import Dictionary
from gensim.models import TfidfModel

# Establecer la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
# Desactivar las advertencias de solicitudes inseguras
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Se encarga de la indexación y generación de respuestas
class Indexer:
    # Conexión con Elasticsearch
    def __init__(self):
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

    def indexer(self):
        # Ruta relativa al archivo
        file_path = "etc/webpages_clean.jsonl"
        documents = []
        # Lectura del archivo jsonl
        with jsonlines.open(file_path) as reader:
            lines = list(reader)
            for i in range(
                1, len(lines), 2
            ):  # Comenzar en la segunda línea y saltar cada dos líneas
                obj = lines[i]
                documents.append(obj["text"].split())

        # Crear un diccionario a partir de los documentos
        self.dct = Dictionary(documents)
        # Crear una representación de bolsa de palabras de los documentos
        corpus = [self.dct.doc2bow(doc) for doc in documents]
        # Entrenar el modelo TF-IDF
        self.model = TfidfModel(corpus)
        # Guardar el modelo
        print("Saving model...")
        model_save_path = "/Users/chus/Desktop/PFG/RAG-CHAT_PFG_git/RAG-CHAT_PFG_git/searcher/etc/models/tfidf_model"
        if not os.path.exists(os.path.dirname(model_save_path)):
            os.makedirs(os.path.dirname(model_save_path))
        self.model.save(model_save_path)
        print(f"Model saved at {model_save_path}.")

        # Cargar el modelo
        print("Loading model...")
        model_load_path = "/Users/chus/Desktop/PFG/RAG-CHAT_PFG_git/RAG-CHAT_PFG_git/searcher/etc/models/tfidf_model"
        self.loaded_model = TfidfModel.load(model_load_path)
        print(f"Model loaded from {model_load_path}.")
        # Vectorizar los documentos
        vectors = [self.model[doc] for doc in corpus]
        # Convertir los vectores a listas de floats
        vectors = [[value for id, value in vector] for vector in vectors]
        # Ajustar la dimensionalidad de los vectores a 231
        vectors = [(vector[:231] + [0.0] * (231 - len(vector))) for vector in vectors]

        # Eliminar el índice si ya existe
        if self.es.indices.exists(index="rag-chat3-vectorized"):
            self.es.indices.delete(index="rag-chat3-vectorized")

        # Crear el índice con el mapeo correcto
        self.es.indices.create(
            index="rag-chat3-vectorized",
            body={
                "mappings": {
                    "properties": {
                        "vector": {
                            "type": "dense_vector",
                            "dims": 231,  # Cambiar el número de dimensiones aquí si fuese necesario
                        },
                    },
                },
            },
            ignore=400,  # Ignorar el error si el índice ya existe
        )

        # Indexar los documentos vectorizados con TF-IDF en Elasticsearch
        for i in range(
            1, len(lines), 2
        ):  # Comenzar en la segunda línea y salta cada dos líneas
            obj = lines[i]
            vector = vectors[
                i // 2
            ]  # Usar la división entera para obtener el índice correcto
            self.es.index(
                index="rag-chat3-vectorized",
                body={
                    "id": obj["id"],
                    "title": obj["title"],
                    "url": obj["url"],
                    "document": obj["text"],
                    "vector": vector,
                },
            )

    # Transformar una pregunta en un vector
    def transform_question_to_vector(self, question):
        # Preprocesar la pregunta y convertirla en una bolsa de palabras
        question_bow = self.dct.doc2bow(question.lower().split())
        # Transformar la bolsa de palabras en un vector TF-IDF
        question_vector = self.loaded_model[question_bow]
        # Convertir el vector en una lista de floats
        question_vector = [value for id, value in question_vector]
        # Ajustar la dimensionalidad del vector a 231
        question_vector = question_vector[:231] + [0.0] * (231 - len(question_vector))
        return question_vector

    # Generar una respuesta a partir de una pregunta introducida por el usuario en el chatbot
    def generate_response(self, question):
        try:
            # Transformar la pregunta en un vector
            question_vector = self.transform_question_to_vector(question)

            # Crear una consulta de similitud de coseno
            cosine_sim_query = Q(
                "script_score",
                query={"match_all": {}},
                script={
                    "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                    "params": {"query_vector": question_vector},
                },
            )

            # Buscar los documentos más relevantes para la pregunta
            search = (
                Search(using=self.es, index="rag-chat3-vectorized")
                .query(cosine_sim_query)
                .sort("_score")
            )

            # Ejecutar la búsqueda y obtener los documentos
            response = search[0:10].execute()

            relevant_docs_info = [
                {"url": hit.url, "title": hit.title} for hit in response
            ]

            context = " ".join([hit.document for hit in response])
            # Generar una respuesta a partir de la pregunta y el contexto
            openai_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": question},
                ],
            )
            # Devolver el contenido de la respuesta
            return (
                openai_response["choices"][0]["message"]["content"],
                relevant_docs_info,
            )

        # Manejar cualquier error que pueda ocurrir
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
