import psutil
from utils.logger import setup_logger

logger = setup_logger()

def calculate_performance():
    return {'total_profit': 1000000, 'win_rate': 60}

def log_performance():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    logger.info(f"Performance: CPU {cpu_percent}%, Memory {memory_percent}%")


    print("Performance logged")