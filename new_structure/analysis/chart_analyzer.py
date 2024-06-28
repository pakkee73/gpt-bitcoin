import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import base64
import time
from utils.logger import setup_logger

logger = setup_logger()

def get_upbit_chart_image():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')

    # ChromeDriver 경로를 상대 경로로 변경
    chromedriver_path = os.path.join(os.path.dirname(__file__), '..', '..', 'chromedriver.exe')
    service = Service(chromedriver_path)

    try:
        logger.info("Initializing Chrome WebDriver")
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)  # 페이지 로드 타임아웃 설정

        logger.info("Navigating to Upbit exchange page")
        driver.get("https://upbit.com/exchange?code=CRIX.UPBIT.KRW-BTC")

        # 명시적 대기 사용
        wait = WebDriverWait(driver, 20)
        logger.info("Waiting for chart to load")
        chart_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "tradingview-chart"))
        )

        # 추가 대기 시간
        time.sleep(5)

        logger.info("Capturing chart screenshot")
        chart_image = chart_element.screenshot_as_png
        base64_image = base64.b64encode(chart_image).decode()

        logger.info("Successfully captured Upbit chart image")
        return base64_image

    except TimeoutException:
        logger.error("Timeout occurred while loading the page or finding elements")
    except WebDriverException as e:
        logger.error(f"WebDriver error occurred: {e}")
    except Exception as e:
        logger.error(f"Unexpected error occurred while capturing Upbit chart image: {e}")
    finally:
        if 'driver' in locals():
            logger.info("Closing WebDriver")
            driver.quit()

    return "chart_image"

if __name__ == "__main__":
    # 테스트 목적으로 함수 실행
    result = get_upbit_chart_image()
    if result:
        logger.info("Chart image captured successfully")
    else:
        logger.error("Failed to capture chart image")