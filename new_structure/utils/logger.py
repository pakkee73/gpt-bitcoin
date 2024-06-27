import logging
from config import LOG_FILE

def setup_logger():
    logger = logging.getLogger('bitcoin_trader')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger