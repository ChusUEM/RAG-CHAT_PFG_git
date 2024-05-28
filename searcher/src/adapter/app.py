from .adapter import Joiner, PrepareJsonL

if __name__ == "__main__":
    joiner = Joiner()
    elastic = PrepareJsonL()
    joiner.join_jsons()
    elastic.prepare_jsonL()
