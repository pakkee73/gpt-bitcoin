from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import time
import requests
import pandas as pd
from utils.logger import get_logger
from data.fetcher import get_alternative_data


logger = get_logger()

def get_upbit_chart_image():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(180)

        logger.info("Navigating to Upbit exchange page")
        driver.get("https://upbit.com/exchange?code=CRIX.UPBIT.KRW-BTC")

        wait = WebDriverWait(driver, 180)
        logger.info("Waiting for chart to load")
        chart_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tradingview-chart")))
        
        time.sleep(30)  # Additional wait time

        logger.info("Capturing chart screenshot")
        chart_image = chart_element.screenshot_as_png
        return base64.b64encode(chart_image).decode()

    except Exception as e:
        logger.error(f"Error capturing chart: {e}")
        return None
    finally:
        if 'driver' in locals():
            driver.quit()

def get_upbit_chart_data(interval='minutes', count=60):
    url = f"https://api.upbit.com/v1/candles/{interval}/1"
    querystring = {"market":"KRW-BTC", "count":str(count)}
    response = requests.request("GET", url, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df
    else:
        logger.error(f"Failed to fetch data: {response.status_code}")
        return None

def get_market_data():
    logger.info("Fetching Upbit chart image and data")
    chart_image = get_upbit_chart_image()
    chart_data = get_upbit_chart_data()
    
    if chart_image is not None and chart_data is not None:
        logger.info("Successfully fetched chart image and data")
        return {
            'chart_image': chart_image,
            'chart_data': chart_data.to_dict(orient='records')
        }
    else:
        logger.warning("Failed to fetch chart image or data, using alternative data")
        return get_alternative_data()
    
    logger.info("차트 이미지 캡처 성공")
    return {'chart_image': chart_image}

__all__ = ['get_market_data']

def get_placeholder_image():
    # 간단한 플레이스홀더 이미지 생성 (예: 빈 이미지)
    placeholder = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xcc\xed\xc3\x00\x00\x00\x00IEND\xaeB`\x82'
    return base64.b64encode(placeholder).decode()


if __name__ == "__main__":
    result = get_market_data()
    if 'chart_image' in result:
        logger.info("차트 이미지 캡처 성공")
    else:
        logger.info("대체 데이터 사용 중")
    logger.debug(f"시장 데이터: {result}")