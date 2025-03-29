from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import yfinance as yf
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_sma(data, window):
    return data.rolling(window=window).mean()

def calculate_rsi(data, periods=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_bollinger_bands(data, window=20, num_std=2):
    sma = data.rolling(window=window).mean()
    std = data.rolling(window=window).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return upper, sma, lower

def calculate_technical_indicators(hist):
    """Calculate enhanced technical indicators"""
    # Moving Averages
    hist['SMA_20'] = calculate_sma(hist['Close'], 20)
    hist['SMA_50'] = calculate_sma(hist['Close'], 50)
    hist['SMA_200'] = calculate_sma(hist['Close'], 200)
    
    # RSI
    hist['RSI'] = calculate_rsi(hist['Close'])
    
    # MACD
    exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
    exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
    hist['MACD'] = exp1 - exp2
    hist['Signal_Line'] = hist['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    hist['BB_upper'], hist['BB_middle'], hist['BB_lower'] = calculate_bollinger_bands(hist['Close'])
    
    # Volume Indicators
    hist['Volume_SMA'] = calculate_sma(hist['Volume'], 20)
    hist['Volume_Ratio'] = hist['Volume'] / hist['Volume_SMA']
    
    return hist

def get_stock_analysis(stock_data, hist):
    """Enhanced analysis with additional indicators"""
    analysis = []
    latest = hist.iloc[-1]
    
    # Price Analysis
    analysis.append(f"Current Price: ${stock_data['current_price']:.2f}")
    analysis.append(f"Daily Change: {stock_data['change']:.2f}%")
    
    # Trend Analysis
    trend_long = "BULLISH" if latest['Close'] > latest['SMA_200'] else "BEARISH"
    trend_short = "BULLISH" if latest['Close'] > latest['SMA_20'] else "BEARISH"
    
    analysis.append(f"\nTrend Analysis:")
    analysis.append(f"Short-term Trend: {trend_short}")
    analysis.append(f"Long-term Trend: {trend_long}")
    analysis.append(f"RSI (14): {latest['RSI']:.2f}")
    
    # Technical Signals
    analysis.append("\nTechnical Signals:")
    
    # RSI Analysis
    if latest['RSI'] > 70:
        analysis.append("⚠️ Overbought (RSI > 70)")
    elif latest['RSI'] < 30:
        analysis.append("⚠️ Oversold (RSI < 30)")
    
    # MACD Analysis
    if latest['MACD'] > latest['Signal_Line']:
        analysis.append("✅ MACD Bullish Crossover")
    else:
        analysis.append("🔻 MACD Bearish Crossover")
    
    # Bollinger Bands
    if latest['Close'] > latest['BB_upper']:
        analysis.append("⚠️ Price above upper Bollinger Band - Potential reversal")
    elif latest['Close'] < latest['BB_lower']:
        analysis.append("⚠️ Price below lower Bollinger Band - Potential reversal")
    
    # Volume Analysis
    analysis.append(f"\nVolume Analysis:")
    analysis.append(f"Current Volume: {stock_data['volume']:,.0f}")
    if latest['Volume_Ratio'] > 1.5:
        analysis.append("📈 High volume activity (50% above average)")
    
    return "\n".join(analysis)

def analyze_stock(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="3mo")
        
        if hist.empty:
            return {'error': 'No data available for this symbol'}
            
        hist = calculate_technical_indicators(hist)
        
        data = {
            'current_price': hist['Close'].iloc[-1],
            'volume': hist['Volume'].iloc[-1],
            'change': (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100,
            'hist': hist
        }
        return data
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {str(e)}")
        return {'error': f"Failed to analyze stock: {str(e)}"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get("prompt", "")
        
        if not prompt:
            return jsonify({"error": "Empty prompt"}), 400

        # Check for stock symbol patterns
        symbol_match = re.search(r'\$([A-Za-z]+)', prompt)
        if symbol_match:
            symbol = symbol_match.group(1).upper()
            stock_data = analyze_stock(symbol)
            if 'error' not in stock_data:
                analysis = get_stock_analysis(stock_data, stock_data['hist'])
                response = f"Analysis for ${symbol}:\n\n{analysis}"
            else:
                return jsonify({"error": stock_data['error']}), 400
        else:
            response = "Please include a stock symbol with $ prefix (e.g., $AAPL) for analysis."
        
        return jsonify({"response": response})

    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/model-info', methods=['GET'])
def model_info():
    try:
        model_name = "GitHub Copilot"
        model_version = "Pro"
        model_description = "AI-powered code and analysis assistant powered by GitHub Copilot"
        return jsonify({
            "name": model_name, 
            "version": model_version, 
            "description": model_description
        })
    except Exception as e:
        logger.error(f"Error fetching model info: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
