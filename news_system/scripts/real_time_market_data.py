#!/usr/bin/env python3
"""
Real-time Market Data Integration
Integrates live market data sources for enhanced analysis
"""

import json
import requests
import sqlite3
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeMarketData:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.market_symbols = [
            'SPY',    # S&P 500 ETF
            'QQQ',    # NASDAQ ETF  
            'IWM',    # Russell 2000
            'DIA',    # Dow Jones ETF
            'VTI',    # Total Market ETF
            'TLT',    # 20+ Year Treasury
            'GLD',    # Gold ETF
            'USO',    # Oil ETF
            'VIX'     # Volatility Index
        ]
        
        # Key individual stocks for sentiment analysis
        self.key_stocks = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
            'JPM', 'JNJ', 'PG', 'V', 'MA', 'DIS', 'NFLX'
        ]
        
    def get_current_market_data(self) -> Dict:
        """Get current market data for key indicators"""
        try:
            market_data = {}
            
            # Get S&P 500, NASDAQ, and VIX data
            spy = yf.Ticker('SPY')
            qqq = yf.Ticker('QQQ')
            vix = yf.Ticker('VIX')
            
            # Current prices and daily change
            spy_info = spy.history(period="1d", interval="1m")
            qqq_info = qqq.history(period="1d", interval="1m")
            vix_info = vix.history(period="1d", interval="1m")
            
            if not spy_info.empty:
                latest_spy = spy_info.iloc[-1]
                market_data['SPY'] = {
                    'price': float(latest_spy['Close']),
                    'change': float(latest_spy['Close'] - spy_info.iloc[0]['Open']),
                    'change_percent': float((latest_spy['Close'] - spy_info.iloc[0]['Open']) / spy_info.iloc[0]['Open'] * 100),
                    'volume': int(latest_spy['Volume'])
                }
            
            if not qqq_info.empty:
                latest_qqq = qqq_info.iloc[-1]
                market_data['QQQ'] = {
                    'price': float(latest_qqq['Close']),
                    'change': float(latest_qqq['Close'] - qqq_info.iloc[0]['Open']),
                    'change_percent': float((latest_qqq['Close'] - qqq_info.iloc[0]['Open']) / qqq_info.iloc[0]['Open'] * 100),
                    'volume': int(latest_qqq['Volume'])
                }
                
            if not vix_info.empty:
                latest_vix = vix_info.iloc[-1]
                market_data['VIX'] = {
                    'price': float(latest_vix['Close']),
                    'level': 'Low' if latest_vix['Close'] < 20 else 'High' if latest_vix['Close'] > 30 else 'Normal'
                }
            
            # Market breadth indicators
            market_data['market_breadth'] = self._calculate_market_breadth()
            
            logger.info(f"Collected real-time data for {len(market_data)} indicators")
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching market data: {str(e)}")
            return {}
    
    def _calculate_market_breadth(self) -> Dict:
        """Calculate market breadth indicators"""
        try:
            # Get advance/decline data for major indices
           spy_data = yf.Ticker('SPY').history(period="5d")
            qqq_data = yf.Ticker('QQQ').history(period="5d")
            
            # Calculate if market is trending up or down
            spy_trend = "up" if spy_data['Close'].iloc[-1] > spy_data['Close'].iloc[0] else "down"
            qqq_trend = "up" if qqq_data['Close'].iloc[-1] > qqq_data['Close'].iloc[0] else "down"
            
            # Volume analysis
            avg_volume_spy = spy_data['Volume'].mean()
            recent_volume_spy = spy_data['Volume'].iloc[-1]
            
            return {
                'spy_trend': spy_trend,
                'qqq_trend': qqq_trend,
                'volume_ratio': float(recent_volume_spy / avg_volume_spy),
                'breadth_signal': 'bullish' if spy_trend == 'up' and qqq_trend == 'up' else 'bearish' if spy_trend == 'down' and qqq_trend == 'down' else 'mixed'
            }
            
        except Exception as e:
            logger.error(f"Error calculating market breadth: {str(e)}")
            return {}
    
    def get_key_stocks_data(self) -> Dict:
        """Get data for key individual stocks"""
        try:
            stocks_data = {}
            
            # Fetch data for key stocks in batches to avoid rate limits
            batch_size = 5
            for i in range(0, len(self.key_stocks), batch_size):
                batch = self.key_stocks[i:i+batch_size]
                
                for symbol in batch:
                    try:
                        ticker = yf.Ticker(symbol)
                        info = ticker.history(period="2d")
                        
                        if not info.empty:
                            current = info['Close'].iloc[-1]
                            previous = info['Close'].iloc[-2] if len(info) > 1 else current
                            change = current - previous
                            change_percent = (change / previous) * 100
                            
                            stocks_data[symbol] = {
                                'price': float(current),
                                'change': float(change),
                                'change_percent': float(change_percent),
                                'volume': int(info['Volume'].iloc[-1])
                            }
                            
                    except Exception as e:
                        logger.warning(f"Error fetching data for {symbol}: {str(e)}")
                        continue
                
                # Small delay between batches
                import time
                time.sleep(0.5)
            
            logger.info(f"Collected data for {len(stocks_data)} key stocks")
            return stocks_data
            
        except Exception as e:
            logger.error(f"Error fetching key stocks data: {str(e)}")
            return {}
    
    def save_market_data(self, market_data: Dict, stocks_data: Dict):
        """Save market data to database for historical analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create market_data table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    price REAL,
                    change REAL,
                    change_percent REAL,
                    volume INTEGER,
                    data_type TEXT
                )
            ''')
            
            # Insert market index data
            for symbol, data in market_data.items():
                if symbol != 'market_breadth':
                    cursor.execute('''
                        INSERT INTO market_data 
                        (timestamp, symbol, price, change, change_percent, volume, data_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        datetime.now().isoformat(),
                        symbol,
                        data.get('price'),
                        data.get('change'),
                        data.get('change_percent'),
                        data.get('volume'),
                        'index'
                    ))
            
            # Insert key stocks data
            for symbol, data in stocks_data.items():
                cursor.execute('''
                    INSERT INTO market_data 
                    (timestamp, symbol, price, change, change_percent, volume, data_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    symbol,
                    data.get('price'),
                    data.get('change'),
                    data.get('change_percent'),
                    data.get('volume'),
                    'stock'
                ))
            
            # Insert market breadth data
            if 'market_breadth' in market_data:
                breadth_data = market_data['market_breadth']
                cursor.execute('''
                    INSERT INTO market_data 
                    (timestamp, symbol, data_type, volume)
                    VALUES (?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    'MARKET_BREADTH',
                    'breadth',
                    json.dumps(breadth_data)
                ))
            
            conn.commit()
            conn.close()
            
            logger.info("Market data saved to database successfully")
            
        except Exception as e:
            logger.error(f"Error saving market data: {str(e)}")
    
    def get_market_summary(self) -> Dict:
        """Get comprehensive market summary with real-time data"""
        # Get real-time data
        market_data = self.get_current_market_data()
        stocks_data = self.get_key_stocks_data()
        
        # Calculate overall market indicators
        summary = {
            'timestamp': datetime.now().isoformat(),
            'overall_sentiment': self._determine_overall_sentiment(market_data, stocks_data),
            'volatility_level': self._determine_volatility_level(market_data),
            'market_momentum': self._determine_market_momentum(market_data),
            'key_metrics': market_data,
            'top_movers': self._get_top_movers(stocks_data),
            'market_indicators': {
                'spy_close': market_data.get('SPY', {}).get('price', 'N/A'),
                'qqq_close': market_data.get('QQQ', {}).get('price', 'N/A'),
                'vix_level': market_data.get('VIX', {}).get('price', 'N/A'),
                'vix_signal': market_data.get('VIX', {}).get('level', 'N/A')
            }
        }
        
        # Save data for historical analysis
        self.save_market_data(market_data, stocks_data)
        
        return summary
    
    def _determine_overall_sentiment(self, market_data: Dict, stocks_data: Dict) -> str:
        """Determine overall market sentiment from price movements"""
        positive_count = 0
        negative_count = 0
        
        # Check major indices
        for symbol, data in market_data.items():
            if isinstance(data, dict) and 'change_percent' in data:
                if data['change_percent'] > 0:
                    positive_count += 2  # Weight indices more heavily
                elif data['change_percent'] < 0:
                    negative_count += 2
        
        # Check individual stocks
        for symbol, data in stocks_data.items():
            if isinstance(data, dict) and 'change_percent' in data:
                if data['change_percent'] > 0:
                    positive_count += 1
                elif data['change_percent'] < 0:
                    negative_count += 1
        
        if positive_count > negative_count * 1.2:
            return 'bullish'
        elif negative_count > positive_count * 1.2:
            return 'bearish'
        else:
            return 'neutral'
    
    def _determine_volatility_level(self, market_data: Dict) -> str:
        """Determine current volatility level"""
        vix_data = market_data.get('VIX', {})
        vix_price = vix_data.get('price', 20)
        
        if vix_price < 15:
            return 'low'
        elif vix_price > 30:
            return 'high'
        else:
            return 'moderate'
    
    def _determine_market_momentum(self, market_data: Dict) -> str:
        """Determine market momentum from price trends"""
        spy_data = market_data.get('SPY', {})
        qqq_data = market_data.get('QQQ', {})
        
        spy_change = spy_data.get('change_percent', 0)
        qqq_change = qqq_data.get('change_percent', 0)
        
        avg_change = (spy_change + qqq_change) / 2
        
        if avg_change > 0.5:
            return 'strong_positive'
        elif avg_change > 0.1:
            return 'positive'
        elif avg_change < -0.5:
            return 'strong_negative'
        elif avg_change < -0.1:
            return 'negative'
        else:
            return 'sideways'
    
    def _get_top_movers(self, stocks_data: Dict, limit: int = 5) -> List[Dict]:
        """Get top gaining and losing stocks"""
        if not stocks_data:
            return []
        
        # Convert to list and sort by change percent
        stocks_list = []
        for symbol, data in stocks_data.items():
            stocks_list.append({
                'symbol': symbol,
                'change_percent': data.get('change_percent', 0),
                'price': data.get('price', 0)
            })
        
        # Sort by change percent
        stocks_list.sort(key=lambda x: x['change_percent'], reverse=True)
        
        return {
            'gainers': stocks_list[:limit],
            'losers': stocks_list[-limit:][::-1]  # Reverse to show biggest losers last
        }

if __name__ == "__main__":
    # Test the real-time market data system
    db_path = "/home/george/projects/clawblogs/news_system/data/rss_aggregator.db"
    market_data = RealTimeMarketData(db_path)
    
    print("🔄 Fetching real-time market data...")
    summary = market_data.get_market_summary()
    
    print(f"\n📊 Market Summary:")
    print(f"Overall Sentiment: {summary['overall_sentiment'].upper()}")
    print(f"Volatility Level: {summary['volatility_level'].upper()}")
    print(f"Market Momentum: {summary['market_momentum'].replace('_', ' ').title()}")
    
    print(f"\n🎯 Key Metrics:")
    for metric, value in summary['key_metrics'].items():
        if isinstance(value, dict) and 'price' in value:
            print(f"  {metric}: ${value['price']:.2f} ({value.get('change_percent', 0):+.2f}%)")
    
    print(f"\n🚀 Top Gainers:")
    for stock in summary['top_movers']['gainers']:
        print(f"  {stock['symbol']}: {stock['change_percent']:+.2f}%")
    
    print(f"\n📉 Top Losers:")
    for stock in summary['top_movers']['losers']:
        print(f"  {stock['symbol']}: {stock['change_percent']:+.2f}%")
