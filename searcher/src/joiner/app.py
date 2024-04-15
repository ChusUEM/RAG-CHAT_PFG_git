from argparse import ArgumentParser

from .joiner import Joiner

if __name__ == "__main__":
    indexer = Joiner()
    indexer.join_jsons()
