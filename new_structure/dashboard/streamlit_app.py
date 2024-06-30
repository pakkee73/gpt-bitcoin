import sys
import os

# 프로젝트 루트 디렉터리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.graph_objects as go
from data.fetcher import fetch_all_data
from db.database import get_recent_decisions
from trading.executor import get_current_portfolio
from utils.performance_monitor import calculate_performance
import streamlit as st

def get_price_data():
    raw_data = fetch_all_data()
    ohlcv_data = raw_data['ohlcv']['1m']  # Assuming we want to use 1-minute data
    df = pd.DataFrame(ohlcv_data)
    df.reset_index(inplace=True)  # 인덱스를 열로 변환
    df.rename(columns={'index': 'timestamp'}, inplace=True)  # 열 이름 변경
    return df

def get_recent_trades():
    # This function will get recent trades from the database
    decisions = get_recent_decisions(10)  # Get last 10 decisions
    return pd.DataFrame(decisions, columns=['timestamp', 'action', 'amount', 'price', 'reason'])

def run_dashboard():
    st.title('Bitcoin Trading Bot Dashboard')

    # 현재 포트폴리오 상태
    portfolio = get_current_portfolio()
    st.write(f"Current BTC Balance: {portfolio['btc_balance']}")
    st.write(f"Current KRW Balance: {portfolio['krw_balance']}")

    # 최근 거래 내역
    trades = get_recent_trades()
    st.subheader('Recent Trades')
    st.table(trades)

    # 가격 차트
    price_data = get_price_data()
    
    # 열 이름 확인
    st.write("Price Data Columns:", price_data.columns)
    
    fig = go.Figure(data=[go.Candlestick(x=price_data['timestamp'],
                    open=price_data['open'],
                    high=price_data['high'],
                    low=price_data['low'],
                    close=price_data['close'])])
    st.plotly_chart(fig)

    # 성능 메트릭
    performance = calculate_performance()
    st.subheader('Performance Metrics')
    st.write(f"Total Profit: {performance['total_profit']}")
    st.write(f"Win Rate: {performance['win_rate']}%")

if __name__ == '__main__':
    run_dashboard()
