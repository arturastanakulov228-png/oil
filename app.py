from flask import Flask, render_template, jsonify
import yfinance as yf
from datetime import datetime
import requests
import json

app = Flask(__name__)

# ========== ФУНКЦИИ ДЛЯ МОНИТОРИНГА ЦЕН ==========
def get_oil_price():
    """Цена на нефть Brent в реальном времени"""
    try:
        oil = yf.Ticker("BZ=F")
        price = oil.history(period='1d')['Close'].iloc[-1]
        return f"{price:.2f} USD"
    except:
        return "85.50 USD"

def get_stock_prices():
    """Акции нефтяных и газовых компаний с резервными данными"""
    stocks = {
        'ROSN.ME': 'Роснефть',
        'LKOH.ME': 'Лукойл', 
        'GAZP.ME': 'Газпром',
        'NVTK.ME': 'Новатэк',
        'SNGS.ME': 'Сургутнефтегаз',
        'TATN.ME': 'Татнефть'
    }
    
    result = {}
    for ticker, name in stocks.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='5d')
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                result[name] = f"{price:.2f} RUB"
            else:
                # Резервные данные если биржа закрыта
                backup_prices = {
                    'Роснефть': '580.50',
                    'Лукойл': '7520.80',
                    'Газпром': '165.30',
                    'Новатэк': '1720.50',
                    'Сургутнефтегаз': '45.20',
                    'Татнефть': '890.40'
                }
                result[name] = f"{backup_prices.get(name, '0')} RUB"
        except:
            # Полностью резервные данные
            backup_prices = {
                'Роснефть': '580.50 RUB',
                'Лукойл': '7520.80 RUB',
                'Газпром': '165.30 RUB',
                'Новатэк': '1720.50 RUB',
                'Сургутнефтегаз': '45.20 RUB',
                'Татнефть': '890.40 RUB'
            }
            result[name] = backup_prices.get(name, "Н/Д")
    
    return result

def get_fuel_prices():
    """Цены на топливо в России"""
    return {
        'АИ-95': '55.80 ₽',
        'АИ-92': '51.20 ₽',
        'Дизель': '58.90 ₽',
        'Газ (пропан)': '32.50 ₽'
    }

def get_gas_price():
    """Цена на природный газ"""
    try:
        gas = yf.Ticker("NG=F")
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

# ========== ФУНКЦИИ ДЛЯ СТРАНИЦЫ АНАЛИТИКИ ==========
def get_industry_data():
    """Данные о значении нефтегазовой отрасли для России"""
    return {
        'gdp_share': '15%',
        'export_share': '50%',
        'employment': '2.2 млн',
        'budget_share': '40%',
        'reserves': {
            'oil': '80 млрд баррелей',
            'gas': '37 трлн м³'
        },
        'world_rank': {
            'oil': '2-е место',
            'gas': '1-е место'
        },
        'top_companies': [
            'Роснефть', 'Лукойл', 'Газпром', 
            'Сургутнефтегаз', 'Новатэк', 'Татнефть'
        ]
    }

def get_world_comparison():
    """Сравнение с другими странами"""
    return [
        {'country': '🇷🇺 Россия', 'oil_production': '10.5', 'gas_production': '701', 'reserves_oil': '80'},
        {'country': '🇺🇸 США', 'oil_production': '11.9', 'gas_production': '934', 'reserves_oil': '69'},
        {'country': '🇸🇦 Саудовская Аравия', 'oil_production': '9.0', 'gas_production': '117', 'reserves_oil': '298'},
        {'country': '🇨🇦 Канада', 'oil_production': '4.6', 'gas_production': '172', 'reserves_oil': '170'},
        {'country': '🇮🇷 Иран', 'oil_production': '3.1', 'gas_production': '254', 'reserves_oil': '208'}
    ]

def get_timeline_data():
    """Исторические вехи развития отрасли"""
    return [
        {'year': '1960-е', 'event': 'Открытие гигантских месторождений в Западной Сибири'},
        {'year': '1970-е', 'event': 'Строительство нефтепровода "Дружба" в Европу'},
        {'year': '1990-е', 'event': 'Приватизация и создание вертикально-интегрированных компаний'},
        {'year': '2000-е', 'event': 'Становление России как энергетической сверхдержавы'},
        {'year': '2010-е', 'event': 'Освоение арктического шельфа и сланцевых месторождений'},
        {'year': '2020-е', 'event': 'Диверсификация экономики при сохранении роли энергетики'}
    ]

# ========== МАРШРУТЫ ==========
@app.route('/')
def index():
    """Главная страница - мониторинг цен"""
    data = {
        'oil_price': get_oil_price(),
        'gas_price': get_gas_price(),
        'stocks': get_stock_prices(),
        'fuel': get_fuel_prices(),
        'usd_rate': get_exchange_rate(),
        'update_time': datetime.now().strftime('%H:%M %d.%m.%Y')
    }
    return render_template('index.html', **data)

@app.route('/about')
def about_industry():
    """Страница о значении отрасли"""
    return render_template('about.html', 
        industry=get_industry_data(),
        comparison=get_world_comparison(),
        timeline=get_timeline_data()
    )

@app.route('/api/world-data')
def api_world_data():
    """API для получения данных сравнения (для графиков)"""
    return jsonify(get_world_comparison())

if __name__ == '__main__':
    app.run()
