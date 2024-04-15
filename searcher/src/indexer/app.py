from .indexer import Indexer

if __name__ == "__main__":
    indexer = Indexer()
    indexer.indexer()

    # Solicita una pregunta del usuario
    question = input("Por favor, introduce tu pregunta: ")

    # Genera y muestra la respuesta
    response = indexer.generate_response(question)
    print("Respuesta:", response)
