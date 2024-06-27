import logging
from config import LOG_FILE

def setup_logger():
    logger = logging.getLogger('bitcoin_trader')
    logger.setLevel(logging.DEBUG)  # 로그 레벨을 DEBUG로 변경
    
    file_handler = logging.FileHandler(LOG_FILE)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)  # 파일 핸들러의 로그 레벨도 DEBUG로 설정
    
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG)  # 콘솔 핸들러의 로그 레벨도 DEBUG로 설정
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger