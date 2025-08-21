import logging

import fire

from fontmod.main import main

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fire.Fire(main)
