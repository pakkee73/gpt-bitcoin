import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from data.fetcher import fetch_ohlcv_data, fetch_orderbook, fetch_balance, fetch_fear_and_greed_index

def test_fetch_ohlcv_data():
    data = fetch_ohlcv_data()
    assert 'daily' in data
    assert 'hourly' in data
    assert len(data['daily']) > 0
    assert len(data['hourly']) > 0

def test_fetch_orderbook():
    orderbook = fetch_orderbook()
    assert 'orderbook_units' in orderbook
    assert len(orderbook['orderbook_units']) > 0

def test_fetch_balance():
    balance = fetch_balance()
    assert isinstance(balance, list)
    assert len(balance) > 0

def test_fetch_fear_and_greed_index():
    index = fetch_fear_and_greed_index()
    assert isinstance(index, list)
    assert len(index) == 30