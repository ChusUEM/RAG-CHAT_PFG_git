import json

with open("etc/webpages_clean.jsonl", "r") as f:
    for line in f:
        obj = json.loads(line)
        print(obj)  # Imprime el objeto JSON para verificar su estructura
        break  # Rompe el bucle después de imprimir el primer objeto
