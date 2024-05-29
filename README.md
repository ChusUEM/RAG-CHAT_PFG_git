# RAG-CHAT: Sistema de recuperación de información en la web oficial de la Universidad Europea de Madrid.
#https://www.elastic.co/es/what-is/retrieval-augmented-generation
#https://www.elastic.co/search-labs/tutorials/chatbot-tutorial/welcome
#Proyecto Final de Grado en Ingeniería Informática (Online). Universidad Europea de Madrid. Curso 2023-2024.
 Fase de obtención de datos en los blogs de la web oficial de la Universidad Europea de Madrid.

 # PASO 1: INSTALACIÓN DE DOCKER
 #  Docker (https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
Ejecución de un nodo ElasticSearch en un contenedor de Docker: Ejecutar el script:
  #Crear red Elastic y Kibana
  `docker network create elastic`
  #Descargar imagen de ElasticSearch
  `docker pull docker.elastic.co/elasticsearch/elasticsearch:8.12.2`
  #Instalar Cosign
  `wget https://artifacts.elastic.co/cosign.pub
    cosign verify --key cosign.pub docker.elastic.co/elasticsearch/elasticsearch:8.12.2`
  #Ejecutar contenedor de ElasticSearch
  `docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:8.12.2`
  #Exportar comtraseña de ElasticSearch
  `export ELASTIC_PASSWORD="your_password"`
  #Copiar el certificado SSL
  `docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .`
  #Crear REST API con ElasticSearch
  `curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200`
  #Descargar imagen de Kibana
  `docker pull docker.elastic.co/kibana/kibana:8.12.2`
  #Ejecutar contenedor de Kibana
  `docker run --name kib01 --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.12.2`
  #Hacer login con usuario+contraseña de ElasticSearch en la web de Kibana
  #Desde la consola, ejecutamos el siguiente comando para comprabar que el nodo de ElasticSearch está en funcionamiento:
  `curl -k -u <elastic-user>:<elastic-password> <elastic-url>/_nodes'`

#  PASO 2: Almacenar la URL, usuario y contraseña en el PATH de ZSH
#Abrir el archivo de configuración
`open ~/.zshrc`
#Añadir las siguientes líneas al final del archivo:
`export ELASTICSEARCH_URL=<tu_url>`
`export ELASTICSEARCH_USER=<tu_usuario>`
`export ELASTICSEARCH_PASSWORD=<tu_contraseña>`
#Ejecutar el siguiente comando para guardar la clave de conexión con la API de OpenAI:
#Crear API Key en https://platform.openai.com/account/api-keys
`export OPENAI_API_KEY="tu_clave_de_api"` 
#Guardar el archivo
#Recargar el archivo de configuración
#Reiniciar la terminal
 
# PASO 3: Configuración inicial del entorno de desarrollo:
#Scripts necesarios con HomeBrew (MacOS)
#Open ssl //Certificados SSL
`brew install openssl`
#Python
`brew install pyenv`
`pyenv install 3.8.18`

# PASO 4: Crear el entorno virtual
#Opcion a: Crear entorno de Python
`python -m venv envElastic`
#Activar entorno de Python
`source envElastic/bin/activate`
#Instalar dependencias --> 
`cd searcher`
`pip install -r requirements.txt`
#Cargo las variables de entorno, desde el directorio raíz del proyecto
`source .env` o `export PYTHONPATH="${PYTHONPATH}:/Users/chus/Desktop/PFG/RAG-CHAT_PFG_git/RAG-CHAT_PFG_git/searcher/src"`

#Opcion b: Crear entorno de Conda
`conda env create --name websearcher --file requirements.yml`
#Activar entorno de Conda
`conda activate websearcher`
#Instalar dependencias
`cd searcher`
`conda env update --file requirements.yml --prune`


# PASO 5: Ejecución de los scripts contenidos en el crawler, adapter e indexer 
#Acceder al directorio "/searcher"
#Ejecutar los programas crawler, adapter, indexer y chatbot para realizar el proceso completo del TFG. Este proces obtendrá los datos de los blogs de las páginas web de la Universidad Europea de Madrid, realizará un proceso PLN, unirá los .json en uno solo y lo adaptará para crear un único archivo .jsonl preparado para indexar en ElasticSearch. Posteriormente realizará la indexación en Elasticsearch y ejecutará la aplicación web a través de la cual se realizarán las consultas al chatbot (pregunta-respuesta con búsqueda de la información en el índice vectorizado y almacenado en Elasticsearch, devolviendo la respuesta más precisa al usuario, así como los blogs de referencia sobre los que basa su respuesta).
`python -m src.crawler.app` --> obtenemos etc/webpages(archivos .json).
`python -m src.adapter.app` --> procesa los archivos .json obtenidos almacenados en etc/webpages y los une en un solo archivo .json llamado "webpages_clean.json". También adapta el archivo "webpages_clean.json" en "webpages_clean.jsonl", para ser indexado posteriormente en ElasticSearch.
`python -m src.indexer.app` --> indexa el contenido de "webpages_clean.jsonl" en ElasticSearch creando un índice de vectores.

# PASO 6: Visualizar el estado de Elasticsearch a través de Kibana en la web.
#Comprobar el nodo de ElasticSearch en el navegador web con la dirección http://localhost:9200: 
  Acceder a: http://localhost:5601/app/dev_tools#/console
  Introducir en la consola: `GET /_cat/nodes?v`
#Comprobar que el índice se ha creado correctamente en ElasticSearch y que los datos se han indexado correctamente.
  Acceder a: http://localhost:5601/app/dev_tools#/console
  Introducir en la consola: `GET webpages/_search`
#Para comprobar el índice de forma más visual, acceder a la dirección http://localhost:5601/app/management/data/index_management/indices
  Seleccionar el índice webpages y hacer click en el botón "Discover Index" para visualizar la información.
#Además, en el buscador podemos realizar búsquedas filtradas por los campos de las páginas web indexadas.


# PASO 7: Test ElasticSearch POR TERMINAL:
Situarse en el directorio searcher/src/chat y ejecutar el siguiente comando para ejecutar el archivo:
`python chatTerminal.py`
Realizar una consulta al chatbot como ejemplo:
¿Qué factores afectan al sueldo de un desarrollador web?


# PASO 8: Ejecutar el archivo de la aplicación frontEnd
`python frontEnd/app.py` --> ejecutar el frontEnd sobre el que se emitirán preguntas y se recibirán respuestas a través de consultas al índice de ElasticSearch.
#En caso de obtener error de carga de variables de entorno (no se encuentra el directorio "src" por ejemplo), ejecutar el siguiente comando:
`export PYTHONPATH="${PYTHONPATH}:/Users/chus/Desktop/PFG/RAG-CHAT_PFG_git/RAG-CHAT_PFG_git/searcher/src"`
#En caso de error de puerto ocupado, ejecutar el siguiente comando:
`lsof -i :5001`
`kill -9 <PID>` --> PID es el número de proceso que aparece en la consola.


# PASO 9: Realizar una consulta al chatbot a través de la aplicación web.
Abrir el navegador web mencionado al ejecutar la aplicación: http://127.0.0.1:5001
Ejemplo de pregunta al chatbot:
¿Qué factores afectan al sueldo de un desarrollador web?






