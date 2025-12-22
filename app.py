from flask import Flask, render_template
import yfinance as yf
from datetime import datetime
import requests
import json

app = Flask(__name__)

def get_oil_price():
    """Цена на нефть Brent в реальном времени"""
    try:
        oil = yf.Ticker("BZ=F")
        price = oil.history(period='1d')['Close'].iloc[-1]
        return f"{price:.2f} USD"
    except:
        return "85.50 USD"

def get_stock_prices():
    """Акции нефтяных и газовых компаний"""
    stocks = {
        'ROSN.ME': 'Роснефть',
        'LKOH.ME': 'Лукойл',
        'GAZP.ME': 'Газпром',
        'NVTK.ME': 'Новатэк',
        'SNGS.ME': 'Сургутнефтегаз'
    }
    
    result = {}
    for ticker, name in stocks.items():
        try:
            stock = yf.Ticker(ticker)
            price = stock.history(period='1d')['Close'].iloc[-1]
            result[name] = f"{price:.2f} RUB"
        except:
            result[name] = "Н/Д"
    
    return result

def get_fuel_prices():
    """Примерные цены на топливо (можно заменить на парсинг с реальных сайтов)"""
    # В реальном проекте парсил бы с сайтов АЗС
    return {
        'АИ-95': '55.80 ₽',
        'АИ-92': '51.20 ₽',
        'Дизель': '58.90 ₽',
        'Газ (пропан)': '32.50 ₽'
    }

def get_gas_price():
    """Цена на природный газ"""
    try:
        gas = yf.Ticker("NG=F")  # Natural Gas Futures
        price = gas.history(period='1d')['Close'].iloc[-1]
        return f"{price:.2f} USD/млн BTU"
    except:
        return "3.85 USD/млн BTU"

def get_exchange_rate():
    """Курс USD/RUB"""
    try:
        response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js', timeout=3)
        data = response.json()
        rate = data['Valute']['USD']['Value']
        return f"{rate:.2f} ₽"
    except:
        return "92.50 ₽"

@app.route('/')
def index():
    data = {
        'oil_price': get_oil_price(),
        'gas_price': get_gas_price(),
        'stocks': get_stock_prices(),
        'fuel': get_fuel_prices(),
        'usd_rate': get_exchange_rate(),
        'update_time': datetime.now().strftime('%H:%M %d.%m.%Y')
    }
    return render_template('index.html', **data)

if __name__ == '__main__':
    app.run()
