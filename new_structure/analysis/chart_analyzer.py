import os
import base64
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from utils.logger import get_logger


logger = get_logger()

def get_upbit_chart_image():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(90)  # 타임아웃을 90초로 증가
        driver.get("https://upbit.com/exchange?code=CRIX.UPBIT.KRW-BTC")

        wait = WebDriverWait(driver, 90)  # 대기 시간을 90초로 증가
        chart_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tradingview-chart")))
        
        # JavaScript 실행을 통해 차트가 완전히 로드되었는지 확인
        is_chart_loaded = driver.execute_script("""
            var chart = document.querySelector('.tradingview-chart');
            return chart && chart.innerHTML !== '';
        """)
        
        if not is_chart_loaded:
            logger.warning("Chart might not be fully loaded, but proceeding with capture")
        
        time.sleep(15)  # 추가 대기 시간을 15초로 증가

        chart_image = chart_element.screenshot_as_png
        return base64.b64encode(chart_image).decode()

    except Exception as e:
        logger.error(f"Error capturing chart: {e}")
        return None  # 에러 발생 시 None 반환

    finally:
        if 'driver' in locals():
            driver.quit()

def get_placeholder_image():
    # 간단한 플레이스홀더 이미지 생성 (예: 빈 이미지)
    placeholder = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xcc\xed\xc3\x00\x00\x00\x00IEND\xaeB`\x82'
    return base64.b64encode(placeholder).decode()

if __name__ == "__main__":
    result = get_upbit_chart_image()
    if result:
        logger.info("Chart image captured successfully")
    else:
        logger.error("Failed to capture chart image")