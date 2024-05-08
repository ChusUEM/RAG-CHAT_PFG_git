from elasticsearch_dsl import Search
import openai


# Generar una respuesta a partir de una pregunta introducida por el usuario en el chat (Terminal)
class ChatByTerminal:
    def generate_response_terminal(self, question):
        try:
            # Buscar los documentos más relevantes para la pregunta
            search = (
                Search(using=self.es, index="rag-chat2-vectorized")
                .query("match", document=question)
                .sort("_score")
            )
            # Ejecutar la búsqueda y obtener los documentos
            response = search[0:5].execute()
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
            return openai_response["choices"][0]["message"]["content"]
        # Manejar cualquier error que pueda ocurrir
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
