import json
import os
import re
import shutil
from argparse import Namespace
from io import BytesIO
from queue import Queue
from typing import List, Set
from urllib.parse import urlparse

import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from PyPDF2 import PdfReader  # type: ignore
from tqdm import tqdm  # type: ignore
from unidecode import unidecode  # type: ignore


def get_data() -> Set[str]:
    my_list: List[str] = []
    return set(my_list)


queue: List[str] = []


class Crawler:
    """Clase que representa un Crawler"""

    def __init__(self, args: Namespace):
        self.args = args
        self.queue: Queue[str] = Queue(self.args.max_webs)

    def crawl(self) -> None:
        """Método para crawlear la URL base. `crawl` crawlea, desde
        la URL base `args.url`, usando la librería `requests` de Python,
        el número máximo de webs especificado en `args.max_webs`.

        Para cada nueva URL que se visite, almacena en el directorio
        `args.output_folder` un fichero .json con lo siguiente:

        - "url": URL de la web
        - "text": Contenido completo (en crudo, sin parsear) de la web
        """

        # Limpiamos el directorio de ficheros
        if os.path.exists(self.args.output_folder):
            # Borrar el directorio y su contenido
            shutil.rmtree(self.args.output_folder)

        # Crear el directorio de salida
        os.mkdir(self.args.output_folder)

        # Creamos la cola y añadimos la URL base
        queue: Queue[str] = Queue(self.args.max_webs)
        queue.put(self.args.url)

        # Creamos un contador para no pasarnos del límite de max_webs
        iteration = 0

        # Creamos una barra de progreso
        progress_bar = tqdm(total=self.args.max_webs, desc="Crawling")

        # Creamos un contador para el id
        id_counter = 1

        # Iteramos la cola
        while not queue.empty() and iteration < self.args.max_webs:
            iteration = iteration + 1

            # Extraemos elemento de la cola
            url = queue.get()

            # Añadimos el esquema y el dominio base si la URL encontrada es relativa
            if url.startswith("/"):
                parsed_url = urlparse(self.args.url)
                url = f"{parsed_url.scheme}://{parsed_url.netloc}{url}"

            # Hacemos la petición HTTP y sacamos el HTML de la URL
            res = requests.get(url)
            content = ""
            # Comprobamos si la URL es un enlace a un fichero PDF
            if url.lower().endswith(".pdf"):
                # Creamos el fichero PDF desde la URL
                pdf_file = BytesIO(res.content)
                # Creamos el objeto de lectura del PDF
                pdf_reader = PdfReader(pdf_file)
                # Extraemos la longitud del documento
                num_pages = len(pdf_reader.pages)
                # Leemos el contenido de cada página
                for page_num in range(num_pages):
                    pdf_page = pdf_reader.pages[page_num]
                    content += pdf_page.extract_text()

            # Si es un HTML, guardamos el texto directamente
            else:
                content = res.text

            soup = BeautifulSoup(content, "html.parser")

            # Extraemos los títulos, párrafos, encabezados y texto en negrita
            title = unidecode(soup.title.string) if soup.title else None
            paragraphs = [unidecode(p.get_text()) for p in soup.find_all("p")]
            headers = [
                unidecode(h.get_text())
                for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            ]
            bold_texts = [unidecode(b.get_text()) for b in soup.find_all("b")]

            # Concatenamos todo el contenido en un solo texto
            text = f"{title} {' '.join(paragraphs)} {' '.join(headers)} {' '.join(bold_texts)}"

            # Almacenamos el contenido en un fichero de texto
            self.store_url(id_counter, url, title, text)

            # Incrementamos el contador de id
            id_counter += 1

            # Extraemos nuevas URLs para parsear
            urls = self.find_urls(content)

            # Añadimos las nuevas URLs encontradas a la cola
            for url in urls:
                try:
                    queue.put(url, block=False)
                except Exception:
                    break

            # Actualizamos la barra de progreso
            progress_bar.update(1)

        # Cerramos la barra de progreso
        progress_bar.close()

    def store_url(self, id: int, url: str, title: str, text: str):
        """Método para almacenar el contenido de una URL en un archivo JSON
        dentro de la carpeta especificada como parámetro en la llamada al programa.

        Args:
            url (str): la URL del documento que se está almacenando
            content (str): el contenido HTML en crudo de la URL
        Returns:
            Void
        """
        # Generamos un diccionario
        data = {
            "id": id,
            "url": url,
            "title": title,
            "text": text,
        }

        # Generamos el nombre del archivo
        parsed_url = urlparse(url)
        file_name = (parsed_url.netloc + parsed_url.path).replace(
            "/", "-"
        ) + ".json"

        # Escribimos el archivo con el contenido del diccionario
        with open(
            os.path.join(self.args.output_folder, file_name), "w"
        ) as file:
            json.dump(data, file)

    def find_urls(self, text: str) -> Set[str]:
        """Método para encontrar URLs de la Universidad Europea en el
        texto de una web. SOLO se extraen URLs que aparezcan
        como valores "href" y que sean blogs de la Universidad, esto es,
        deben empezar por "https://universidadeuropea.com/blog/".
        `find_urls` es útil para el proceso de crawling en el método `crawl`

        Args:
            text (str): text de una web
        Returns:
            Set[str]: conjunto de urls (únicas) extraídas de la web
        """

        # Parseamos la URL de entrada, para sacar sólo el dominio
        urlparse(self.args.url)

        # Definimos la expresión regular para encontrar enlaces que comiencen con la url que se pasa por parámetro, tanto webs como ficheros PDF
        pattern = re.compile(
            r'<a[^>]* href=\"(/blog/[^\"\']*(\.pdf)?)["\'][^>]*>',
            re.IGNORECASE,
        )

        # Encuentra todos los enlaces que coincidan con la expresión regular
        matches = pattern.findall(text)

        # Convertimos las tuplas a cadenas
        matches = [match[0] for match in matches]

        # Devolvemos la lista de enlaces
        return set(matches)
