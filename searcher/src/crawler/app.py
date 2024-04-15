from argparse import ArgumentParser

from .crawler import Crawler


def parse_args():
    parser = ArgumentParser(
        prog="Crawler",
        description="Script para ejecutar el crawler. El crawler recibe una"
        " URL y un número máximo de webs e irá almacenando los"
        " resultados en disco",
    )

    parser.add_argument(
        "-u",
        "--url",
        type=str,
        default="https://universidadeuropea.com/blog/",
        help="URL base desde donde empezar a crawlear.",
    )

    parser.add_argument(
        "-m",
        "--max_webs",
        type=int,
        default=300,
        help="Número máximo de webs a crawlear.",
    )

    parser.add_argument(
        "-o",
        "--output-folder",
        type=str,
        default="etc/webpages",
        help="Carpeta destino donde almacenar el contenido" " de las URLs crawleadas.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    crawler = Crawler(args)
    crawler.crawl()
