# Importar las librerías necesarias
import os
import ssl

import jsonlines  # type: ignore
import nltk  # type: ignore
import openai  # type: ignore
import urllib3
from elasticsearch import Elasticsearch  # type: ignore
from joblib import dump  # type: ignore
from nltk.corpus import stopwords  # type: ignore
from sklearn.decomposition import PCA  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from urllib3.util.ssl_ import create_urllib3_context

nltk.download("stopwords")
openai.api_key = os.getenv("OPENAI_API_KEY")
# Desactivar las advertencias de solicitudes inseguras
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Descargar las palabras de parada en español
nltk.download("stopwords")
spanish_stopwords = stopwords.words("spanish")
# Crear el vectorizador con las palabras de parada en español
vectorizer = TfidfVectorizer(stop_words=spanish_stopwords)


# Se encarga de la indexación y generación de respuestas
class Indexer:
    # Conexión con Elasticsearch
    def __init__(self):
        context = create_urllib3_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        es_url = os.getenv("ELASTICSEARCH_URL")
        if not es_url:
            raise ValueError(
                "ELASTICSEARCH_URL environment variable is not set"
            )
        self.es = Elasticsearch(
            [es_url],
            http_auth=(
                os.getenv("ELASTICSEARCH_USER"),
                os.getenv("ELASTICSEARCH_PASSWORD"),
            ),
            verify_certs=False,
        )
        self.vectorizer = TfidfVectorizer(
            sublinear_tf=True, max_df=0.5, stop_words=spanish_stopwords
        )
        self.model = None
        self.dct = None

    def indexer(self):
        # Ruta relativa al archivo
        file_path = "etc/webpages_clean/webpages_clean.jsonl"
        documents = []

        # Lectura del archivo jsonl
        with jsonlines.open(file_path) as reader:
            lines = list(reader)
            for i in range(
                1, len(lines), 2
            ):  # Comenzar en la segunda línea y saltar cada dos líneas
                obj = lines[i]
                documents.append(obj["text"])

        # Ajustar el vectorizador a tus documentos y transformar los documentos en vectores
        X = self.vectorizer.fit_transform(documents)

        # Guardar el vectorizador
        dump(self.vectorizer, "etc/models/tfidf_vectorizer.joblib")

        # Reducir la dimensionalidad de los vectores a 169
        pca = PCA(n_components=169)
        X_reduced = pca.fit_transform(X.toarray())

        # Guardar el PCA
        dump(pca, "etc/models/pca.joblib")

        # Eliminar el índice si ya existe
        if self.es.indices.exists(index="rag-chat_index"):
            self.es.indices.delete(index="rag-chat_index")

        # Crear un mapeo para el índice
        mapping = {
            "mappings": {
                "properties": {"vector": {"type": "dense_vector", "dims": 169}}
            }
        }

        # Crear el índice con el mapeo
        self.es.indices.create(index="rag-chat_index", body=mapping)

        # Indexar cada vector de documento en Elasticsearch
        for i, vector in enumerate(X_reduced):
            # Crear un documento que contenga el vector TF-IDF
            doc = {
                "id": lines[i * 2 + 1]["id"],
                "title": lines[i * 2 + 1]["title"],
                "url": lines[i * 2 + 1]["url"],
                "document": lines[i * 2 + 1]["text"],
                "vector": vector.tolist(),
            }

            # Indexar el documento en Elasticsearch
            self.es.index(index="rag-chat_index", id=i, body=doc)


indexer = Indexer()
indexer.indexer()
