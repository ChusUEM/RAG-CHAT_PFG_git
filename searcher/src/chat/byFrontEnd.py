from elasticsearch_dsl import Search, Q
import json


class ChatByFrontEnd:
    def generate_response_frontend(self, question, session_id):
        try:
            # Añadir la pregunta del usuario al historial de chat
            self.add_user_message_to_history(session_id, question)

            # Crear una consulta condensada
            condensed_question = self.condense_question(question, session_id)

            # Buscar los documentos más relevantes para la pregunta condensada
            search = (
                Search(using=self.es, index="rag-chat2-vectorized")
                .query("match", document=condensed_question)
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
            # Añadir la respuesta de la IA al historial de chat
            self.add_ai_message_to_history(
                session_id, openai_response["choices"][0]["message"]["content"]
            )

            # Devolver el contenido de la respuesta
            return openai_response["choices"][0]["message"]["content"]
        # Manejar cualquier error que pueda ocurrir
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

    def add_user_message_to_history(self, session_id, message):
        # Aquí debes implementar la lógica para añadir el mensaje del usuario al historial de chat en Elasticsearch
        pass

    def add_ai_message_to_history(self, session_id, message):
        # Aquí debes implementar la lógica para añadir el mensaje de la IA al historial de chat en Elasticsearch
        pass

    def condense_question(self, question, session_id):
        # Aquí debes implementar la lógica para condensar la pregunta basándote en el historial de chat
        return question
