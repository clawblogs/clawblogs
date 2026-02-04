#!/usr/bin/env python3
"""
Market Analysis Engine for Investment Timing and Risk Assessment
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
import re
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MarketSignal:
    signal_type: str
    strength: int  # 1-10 scale
    description: str
    confidence: float  # 0-1 scale
    timestamp: str
    source_articles: List[str]

@dataclass 
class TimingRecommendation:
    window_type: str  # 'buy', 'sell', 'hold', 'avoid'
    optimal_times: List[str]
    risk_level: str  # 'low', 'medium', 'high'
    confidence: float
    reasoning: str

class MarketAnalysisEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
        # Investment timing patterns
        self.timing_keywords = {
            'bullish': ['rally', 'surge', 'gain', 'rise', 'up', 'positive', 'strong'],
            'bearish': ['fall', 'drop', 'decline', 'loss', 'down', 'negative', 'weak'],
            'volatile': ['volatility', 'swing', 'fluctuation', 'uncertainty'],
            'earnings': ['earnings', 'revenue', 'profit', 'guidance', 'q1', 'q2', 'q3', 'q4'],
            'fed': ['federal reserve', 'fed', 'interest rate', 'monetary policy', 'inflation'],
            'technical': ['support', 'resistance', 'breakout', 'chart', 'technical analysis']
        }
        
        # Market hours and optimal timing (Eastern Time)
        self.market_hours = {
            'pre_market': (4, 9.5),  # 4:00 AM - 9:30 AM
            'open': (9.5, 10.5),    # 9:30 AM - 10:30 AM (high volatility)
            'mid_morning': (10.5, 12), # 10:30 AM - 12:00 PM
            'lunch': (12, 13),      # 12:00 PM - 1:00 PM (low volume)
            'afternoon': (13, 15),  # 1:00 PM - 3:00 PM
            'close': (15, 16),      # 3:00 PM - 4:00 PM (high activity)
            'after_hours': (16, 20) # 4:00 PM - 8:00 PM
        }
    
    def analyze_market_sentiment(self, hours_back: int = 24) -> Dict:
        """Analyze overall market sentiment from recent articles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent financial articles
        cursor.execute('''
            SELECT title, description, score, source, created_at
            FROM articles 
            WHERE category = 'financial' 
            AND created_at >= datetime('now', '-{} hours')
            ORDER BY score DESC, created_at DESC
        '''.format(hours_back))
        
        articles = cursor.fetchall()
        conn.close()
        
        if not articles:
            return {'sentiment': 'neutral', 'confidence': 0.0, 'article_count': 0}
        
        sentiment_scores = []
        high_impact_count = 0
        
        for title, desc, score, source, created_at in articles:
            text = f"{title} {desc}".lower()
            sentiment_score = 0
            
            # Count bullish vs bearish indicators
            bullish_count = sum(1 for word in self.timing_keywords['bullish'] if word in text)
            bearish_count = sum(1 for word in self.timing_keywords['bearish'] if word in text)
            
            # Calculate sentiment
            sentiment_score = bullish_count - bearish_count
            
            # Boost for high-impact articles
            if score > 20:
                sentiment_score *= 1.5
                high_impact_count += 1
            
            # Boost for recent articles
            try:
                article_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                hours_old = (datetime.now(article_time.tzinfo) - article_time).total_seconds() / 3600
                if hours_old < 6:  # Very recent
                    sentiment_score *= 1.2
            except:
                pass
            
            sentiment_scores.append(sentiment_score)
        
        # Calculate overall sentiment
        avg_sentiment = statistics.mean(sentiment_scores) if sentiment_scores else 0
        
        # Determine sentiment category
        if avg_sentiment > 2:
            sentiment = 'bullish'
            confidence = min(0.9, abs(avg_sentiment) / 5)
        elif avg_sentiment < -2:
            sentiment = 'bearish'
            confidence = min(0.9, abs(avg_sentiment) / 5)
        else:
            sentiment = 'neutral'
            confidence = min(0.7, abs(avg_sentiment) / 4)
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'avg_score': avg_sentiment,
            'article_count': len(articles),
            'high_impact_count': high_impact_count,
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_market_signals(self, hours_back: int = 24) -> List[MarketSignal]:
        """Detect specific market signals from articles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, description, score, source
            FROM articles 
            WHERE category = 'financial' 
            AND created_at >= datetime('now', '-{} hours')
            AND score > 10
            ORDER BY score DESC
        '''.format(hours_back))
        
        articles = cursor.fetchall()
        conn.close()
        
        signals = []
        
        for title, desc, score, source in articles:
            text = f"{title} {desc}".lower()
            
            # Fed/Rate signals
            if any(keyword in text for keyword in self.timing_keywords['fed']):
                signals.append(MarketSignal(
                    signal_type='fed_decision',
                    strength=min(10, score // 3),
                    description='Federal Reserve decision or rate-related news detected',
                    confidence=0.8,
                    timestamp=datetime.now().isoformat(),
                    source_articles=[title]
                ))
            
            # Earnings signals
            elif any(keyword in text for keyword in self.timing_keywords['earnings']):
                signals.append(MarketSignal(
                    signal_type='earnings_impact',
                    strength=min(8, score // 4),
                    description='Earnings or revenue-related news with potential market impact',
                    confidence=0.7,
                    timestamp=datetime.now().isoformat(),
                    source_articles=[title]
                ))
            
            # Volatility signals
            elif any(keyword in text for keyword in self.timing_keywords['volatile']):
                signals.append(MarketSignal(
                    signal_type='volatility_spike',
                    strength=min(9, score // 3),
                    description='Market volatility or uncertainty indicators detected',
                    confidence=0.75,
                    timestamp=datetime.now().isoformat(),
                    source_articles=[title]
                ))
            
            # Technical signals
            elif any(keyword in text for keyword in self.timing_keywords['technical']):
                signals.append(MarketSignal(
                    signal_type='technical_breakout',
                    strength=min(7, score // 4),
                    description='Technical analysis or chart pattern signals detected',
                    confidence=0.6,
                    timestamp=datetime.now().isoformat(),
                    source_articles=[title]
                ))
        
        return signals
    
    def calculate_optimal_timing(self, sentiment_data: Dict, signals: List[MarketSignal]) -> TimingRecommendation:
        """Calculate optimal investment timing based on current market conditions"""
        
        # Base timing recommendations
        if sentiment_data['sentiment'] == 'bullish' and sentiment_data['confidence'] > 0.7:
            optimal_times = ['open', 'mid_morning', 'afternoon']
            window_type = 'buy'
            risk_level = 'medium'
            confidence = sentiment_data['confidence']
            reasoning = "Bullish sentiment with high confidence - favorable for buying"
            
        elif sentiment_data['sentiment'] == 'bearish' and sentiment_data['confidence'] > 0.7:
            optimal_times = ['lunch', 'after_hours']
            window_type = 'hold' if any(s.signal_type == 'volatility_spike' for s in signals) else 'sell'
            risk_level = 'high'
            confidence = sentiment_data['confidence']
            reasoning = "Bearish sentiment detected - consider reducing exposure or holding"
            
        elif any(s.signal_type == 'fed_decision' for s in signals):
            optimal_times = ['after_hours', 'pre_market']
            window_type = 'hold'
            risk_level = 'high'
            confidence = 0.8
            reasoning = "Federal Reserve activity detected - avoid new positions during decision periods"
            
        elif any(s.signal_type == 'volatility_spike' for s in signals):
            optimal_times = ['lunch']
            window_type = 'avoid'
            risk_level = 'high'
            confidence = 0.75
            reasoning = "High volatility detected - avoid new positions until volatility stabilizes"
            
        else:
            optimal_times = ['open', 'afternoon']
            window_type = 'hold'
            risk_level = 'medium'
            confidence = 0.6
            reasoning = "Neutral market conditions - standard trading hours recommended"
        
        # Adjust based on signal strength
        if signals:
            signal_strength = max(s.strength for s in signals) / 10
            confidence = min(0.95, confidence * (1 + signal_strength * 0.2))
            
            if any(s.signal_type == 'earnings_impact' for s in signals):
                reasoning += " (Earnings activity may cause unusual price movements)"
        
        return TimingRecommendation(
            window_type=window_type,
            optimal_times=optimal_times,
            risk_level=risk_level,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def get_investment_advice(self, hours_back: int = 24) -> Dict:
        """Get comprehensive investment timing advice"""
        logger.info("Analyzing market conditions for investment timing")
        
        # Analyze sentiment
        sentiment_data = self.analyze_market_sentiment(hours_back)
        
        # Detect signals
        signals = self.detect_market_signals(hours_back)
        
        # Calculate timing recommendation
        timing = self.calculate_optimal_timing(sentiment_data, signals)
        
        # Build comprehensive advice
        advice = {
            'timestamp': datetime.now().isoformat(),
            'sentiment_analysis': sentiment_data,
            'detected_signals': [
                {
                    'type': s.signal_type,
                    'strength': s.strength,
                    'description': s.description,
                    'confidence': s.confidence
                } for s in signals
            ],
            'timing_recommendation': {
                'action': timing.window_type,
                'optimal_windows': timing.optimal_times,
                'risk_level': timing.risk_level,
                'confidence': timing.confidence,
                'reasoning': timing.reasoning
            },
            'detailed_timing': self.get_detailed_time_windows(timing),
            'market_hours_explanation': self.get_market_hours_explanation()
        }
        
        logger.info(f"Generated investment advice: {timing.window_type} with {timing.confidence:.1%} confidence")
        return advice
    
    def get_detailed_time_windows(self, timing: TimingRecommendation) -> Dict:
        """Get detailed explanation of optimal time windows"""
        explanations = {
            'pre_market': '4:00-9:30 AM ET - Limited liquidity, good for setting orders',
            'open': '9:30-10:30 AM ET - Highest volatility, fastest price discovery',
            'mid_morning': '10:30 AM-12:00 PM ET - More predictable movements',
            'lunch': '12:00-1:00 PM ET - Lowest volume, avoid new positions',
            'afternoon': '1:00-3:00 PM ET - Moderate activity, institutional activity',
            'close': '3:00-4:00 PM ET - High activity, good for momentum trades',
            'after_hours': '4:00-8:00 PM ET - News reactions, earnings announcements'
        }
        
        return {
            window: explanations.get(window, 'Custom timing window') 
            for window in timing.optimal_times
        }
    
    def get_market_hours_explanation(self) -> Dict:
        """Get explanation of market hours and their characteristics"""
        return {
            'high_volatility': ['open', 'close'],
            'low_volume': ['lunch', 'after_hours'],
            'best_for_buying': ['mid_morning', 'afternoon'],
            'best_for_selling': ['open', 'close'],
            'avoid_trading': ['lunch'] if any('avoid' in str(t).lower() for t in []) else ['lunch'],
            'news_reaction_time': ['after_hours', 'pre_market']
        }
    
    def get_top_articles_summary(self, hours_back: int = 24, limit: int = 10) -> List[Dict]:
        """Get summary of top-scoring articles for context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, source, score, category, published
            FROM articles 
            WHERE created_at >= datetime('now', '-{} hours')
            ORDER BY score DESC
            LIMIT ?
        '''.format(hours_back), (limit,))
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'title': row[0],
                'source': row[1],
                'score': row[2],
                'category': row[3],
                'published': row[4]
            })
        
        conn.close()
        return articles

if __name__ == "__main__":
    # Setup paths
    db_path = "/home/george/projects/clawblogs/news_system/data/rss_aggregator.db"
    
    # Initialize and run analysis
    engine = MarketAnalysisEngine(db_path)
    advice = engine.get_investment_advice()
    
    print(json.dumps(advice, indent=2))
