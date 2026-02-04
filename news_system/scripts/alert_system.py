#!/usr/bin/env python3
"""
Smart Alert System for Financial News and Investment Timing
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Alert:
    alert_id: str
    alert_type: str  # 'timing', 'news', 'signal', 'summary'
    priority: str    # 'low', 'medium', 'high', 'critical'
    title: str
    message: str
    timestamp: str
    confidence: float
    actionable: bool
    data: Dict

class SmartAlertSystem:
    def __init__(self, db_path: str, config_path: str):
        self.db_path = db_path
        self.config_path = config_path
        self.config = self.load_config()
        self.alert_history = []
        
    def load_config(self) -> Dict:
        """Load alert system configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Default configuration for alert system"""
        return {
            "alert_thresholds": {
                "min_news_score": 15,      # Minimum score for news alerts
                "min_confidence": 0.7,     # Minimum confidence for timing alerts
                "critical_score": 25,      # Score threshold for critical alerts
                "volatility_threshold": 0.8
            },
            "timing_alerts": {
                "enabled": True,
                "check_interval_minutes": 60,
                "optimal_windows": ["open", "mid_morning", "afternoon"],
                "avoid_windows": ["lunch"]
            },
            "news_alerts": {
                "enabled": True,
                "immediate_keywords": ["federal reserve", "earnings", "market crash"],
                "digest_frequency": "daily",
                "max_daily_alerts": 10
            },
            "signal_alerts": {
                "enabled": True,
                "min_signal_strength": 6,
                "max_signal_age_hours": 6
            },
            "delivery": {
                "method": "console",  # 'console', 'email', 'webhook'
                "webhook_url": None,
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": None,
                    "password": None,
                    "to_addresses": []
                }
            }
        }
    
    def generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import hashlib
        return f"alert_{timestamp}_{hash(timestamp) % 10000}"
    
    def get_recent_market_advice(self) -> Dict:
        """Get recent market analysis for alert generation"""
        try:
            from market_analysis import MarketAnalysisEngine
            engine = MarketAnalysisEngine(self.db_path)
            return engine.get_investment_advice(hours_back=24)
        except ImportError:
            logger.error("MarketAnalysisEngine not available")
            return {}
    
    def get_recent_high_impact_news(self, hours_back: int = 6) -> List[Dict]:
        """Get recent high-impact news for alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, link, description, source, score, published, category
            FROM articles 
            WHERE score >= ? 
            AND created_at >= datetime('now', '-{} hours')
            ORDER BY score DESC, created_at DESC
            LIMIT 20
        '''.format(hours_back), (self.config["alert_thresholds"]["min_news_score"],))
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'title': row[0],
                'link': row[1],
                'description': row[2] or '',
                'source': row[3],
                'score': row[4],
                'published': row[5],
                'category': row[6]
            })
        
        conn.close()
        return articles
    
    def check_timing_opportunity(self, market_advice: Dict) -> Optional[Alert]:
        """Check for optimal investment timing opportunities"""
        if not market_advice or 'timing_recommendation' not in market_advice:
            return None
        
        timing = market_advice['timing_recommendation']
        confidence = timing.get('confidence', 0)
        action = timing.get('action', 'hold')
        
        # Check if confidence meets threshold and action is actionable
        if (confidence >= self.config["alert_thresholds"]["min_confidence"] and 
            action in ['buy', 'sell']):
            
            # Get current hour (simplified - in real system would use proper timezone)
            current_hour = datetime.now().hour
            
            # Map current time to market window (simplified)
            market_windows = {
                'open': (9, 11),
                'mid_morning': (10, 12),
                'afternoon': (13, 15),
                'close': (15, 16),
                'lunch': (12, 13)
            }
            
            # Check if current time is in optimal window
            in_optimal_window = False
            for window, (start, end) in market_windows.items():
                if window in timing.get('optimal_windows', []):
                    if start <= current_hour < end:
                        in_optimal_window = True
                        break
            
            if in_optimal_window:
                priority = 'high' if confidence > 0.8 else 'medium'
                
                return Alert(
                    alert_id=self.generate_alert_id(),
                    alert_type='timing',
                    priority=priority,
                    title=f"Investment Timing Alert: {action.upper()}",
                    message=f"Market analysis indicates {action.upper()} opportunity with {confidence:.1%} confidence. "
                           f"Optimal windows: {', '.join(timing.get('optimal_windows', []))}. "
                           f"Risk level: {timing.get('risk_level', 'unknown')}. "
                           f"Reasoning: {timing.get('reasoning', 'No additional context')}",
                    timestamp=datetime.now().isoformat(),
                    confidence=confidence,
                    actionable=True,
                    data=timing
                )
        
        return None
    
    def check_critical_news_alerts(self, news_articles: List[Dict]) -> List[Alert]:
        """Check for critical news that requires immediate attention"""
        alerts = []
        immediate_keywords = self.config["news_alerts"]["immediate_keywords"]
        
        for article in news_articles:
            title_lower = article['title'].lower()
            desc_lower = article['description'].lower()
            combined_text = f"{title_lower} {desc_lower}"
            
            # Check for immediate alert keywords
            for keyword in immediate_keywords:
                if keyword in combined_text and article['score'] >= self.config["alert_thresholds"]["critical_score"]:
                    priority = 'critical'
                    alert_type = 'news'
                    
                    if 'federal reserve' in keyword or 'fed' in keyword:
                        alert_type = 'fed_alert'
                        priority = 'critical'
                    elif 'earnings' in keyword:
                        alert_type = 'earnings_alert'
                        priority = 'high'
                    elif 'market crash' in keyword:
                        alert_type = 'market_crash'
                        priority = 'critical'
                    
                    alert = Alert(
                        alert_id=self.generate_alert_id(),
                        alert_type=alert_type,
                        priority=priority,
                        title=f"CRITICAL: {article['title'][:80]}...",
                        message=f"High-impact {article['category']} news detected: {article['title']}. "
                               f"Source: {article['source']}. "
                               f"Impact Score: {article['score']}. "
                               f"Action required: Review immediately. "
                               f"Link: {article['link']}",
                        timestamp=datetime.now().isoformat(),
                        confidence=0.9,
                        actionable=True,
                        data=article
                    )
                    alerts.append(alert)
                    break  # Only one alert per article
        
        return alerts
    
    def check_market_signals_alerts(self, market_advice: Dict) -> List[Alert]:
        """Check for significant market signals"""
        alerts = []
        if not market_advice or 'detected_signals' not in market_advice:
            return alerts
        
        signals = market_advice['detected_signals']
        min_strength = self.config["signal_alerts"]["min_signal_strength"]
        
        for signal in signals:
            if (signal['strength'] >= min_strength and 
                signal['confidence'] >= self.config["alert_thresholds"]["min_confidence"]):
                
                priority = 'high' if signal['strength'] >= 8 else 'medium'
                
                alert = Alert(
                    alert_id=self.generate_alert_id(),
                    alert_type='signal',
                    priority=priority,
                    title=f"Market Signal: {signal['type'].replace('_', ' ').title()}",
                    message=f"Market signal detected: {signal['description']}. "
                           f"Strength: {signal['strength']}/10. "
                           f"Confidence: {signal['confidence']:.1%}. "
                           f"Action: Consider adjusting position based on signal strength.",
                    timestamp=datetime.now().isoformat(),
                    confidence=signal['confidence'],
                    actionable=True,
                    data=signal
                )
                alerts.append(alert)
        
        return alerts
    
    def generate_daily_summary(self) -> Alert:
        """Generate daily market summary alert"""
        market_advice = self.get_recent_market_advice()
        news_articles = self.get_recent_high_impact_news(hours_back=24)
        
        # Create summary content
        sentiment = market_advice.get('sentiment_analysis', {}).get('sentiment', 'unknown')
        confidence = market_advice.get('sentiment_analysis', {}).get('confidence', 0)
        timing_action = market_advice.get('timing_recommendation', {}).get('action', 'hold')
        
        summary_text = f"""DAILY MARKET SUMMARY - {datetime.now().strftime('%Y-%m-%d')}

MARKET SENTIMENT: {sentiment.upper()} (Confidence: {confidence:.1%})
RECOMMENDED ACTION: {timing_action.upper()}
NEWS HIGHLIGHTS: {len(news_articles)} high-impact articles today

TOP NEWS:
"""
        
        # Add top 3 news items
        for i, article in enumerate(news_articles[:3], 1):
            summary_text += f"{i}. {article['title']} (Score: {article['score']})\n"
        
        summary_text += f"""
SIGNALS DETECTED: {len(market_advice.get('detected_signals', []))}
CONFIDENCE LEVEL: {confidence:.1%}

Full analysis available in market system dashboard.
"""
        
        return Alert(
            alert_id=self.generate_alert_id(),
            alert_type='summary',
            priority='medium',
            title=f"Daily Market Summary - {datetime.now().strftime('%Y-%m-%d')}",
            message=summary_text,
            timestamp=datetime.now().isoformat(),
            confidence=confidence,
            actionable=False,
            data={
                'sentiment': sentiment,
                'confidence': confidence,
                'article_count': len(news_articles),
                'signals_count': len(market_advice.get('detected_signals', []))
            }
        )
    
    def should_send_alert(self, alert: Alert, last_alert_time: Dict) -> bool:
        """Determine if alert should be sent based on rate limiting"""
        # Get last alert time for this type
        last_time = last_alert_time.get(alert.alert_type)
        if not last_time:
            return True
        
        # Check rate limits
        now = datetime.now()
        last = datetime.fromisoformat(last_time)
        
        time_diff = (now - last).total_seconds()
        
        # Rate limits by alert type (in seconds)
        rate_limits = {
            'timing': 3600,      # 1 hour
            'news': 1800,        # 30 minutes for critical news
            'signal': 7200,      # 2 hours
            'summary': 86400,    # 24 hours
            'fed_alert': 3600,   # 1 hour
            'earnings_alert': 7200,  # 2 hours
            'market_crash': 300  # 5 minutes for extreme events
        }
        
        limit = rate_limits.get(alert.alert_type, 3600)
        return time_diff >= limit
    
    def deliver_alert(self, alert: Alert) -> bool:
        """Deliver alert to user via configured method"""
        try:
            method = self.config["delivery"]["method"]
            
            if method == "console":
                self.deliver_to_console(alert)
            elif method == "email":
                self.deliver_to_email(alert)
            elif method == "webhook":
                self.deliver_to_webhook(alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deliver alert {alert.alert_id}: {e}")
            return False
    
    def deliver_to_console(self, alert: Alert):
        """Deliver alert to console with formatting"""
        print(f"\n{'='*80}")
        print(f"🚨 {alert.alert_type.upper()} ALERT - {alert.priority.upper()}")
        print(f"{'='*80}")
        print(f"Title: {alert.title}")
        print(f"Time: {alert.timestamp}")
        print(f"Confidence: {alert.confidence:.1%}")
        print(f"Actionable: {'Yes' if alert.actionable else 'No'}")
        print(f"\nMessage:")
        print(f"{alert.message}")
        print(f"{'='*80}\n")
        
        # Also log to file
        logger.info(f"ALERT: {alert.title} - {alert.message}")
    
    def deliver_to_email(self, alert: Alert):
        """Deliver alert via email (placeholder)"""
        # Email implementation would go here
        logger.info(f"Email delivery for alert {alert.alert_id} - feature to be implemented")
    
    def deliver_to_webhook(self, alert: Alert):
        """Deliver alert via webhook (placeholder)"""
        # Webhook implementation would go here
        logger.info(f"Webhook delivery for alert {alert.alert_id} - feature to be implemented")
    
    def process_alerts(self) -> Dict:
        """Main alert processing function"""
        logger.info("Starting alert processing cycle")
        
        # Get market analysis and news
        market_advice = self.get_recent_market_advice()
        news_articles = self.get_recent_high_impact_news()
        
        alerts_generated = []
        
        # Check for timing opportunities
        timing_alert = self.check_timing_opportunity(market_advice)
        if timing_alert:
            alerts_generated.append(timing_alert)
        
        # Check for critical news
        critical_news = self.check_critical_news_alerts(news_articles)
        alerts_generated.extend(critical_news)
        
        # Check for market signals
        signal_alerts = self.check_market_signals_alerts(market_advice)
        alerts_generated.extend(signal_alerts)
        
        # Generate daily summary if it's a new day or manual trigger
        current_hour = datetime.now().hour
        if current_hour == 9:  # 9 AM daily summary
            daily_summary = self.generate_daily_summary()
            alerts_generated.append(daily_summary)
        
        # Deliver alerts
        delivered_count = 0
        failed_count = 0
        
        # Load last alert times (in real system, this would be from database)
        last_alert_times = {}
        
        for alert in alerts_generated:
            if self.should_send_alert(alert, last_alert_times):
                if self.deliver_alert(alert):
                    delivered_count += 1
                    last_alert_times[alert.alert_type] = alert.timestamp
                else:
                    failed_count += 1
            else:
                logger.info(f"Alert {alert.alert_id} skipped due to rate limiting")
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'alerts_generated': len(alerts_generated),
            'alerts_delivered': delivered_count,
            'alerts_failed': failed_count,
            'market_sentiment': market_advice.get('sentiment_analysis', {}),
            'top_articles': len(news_articles)
        }
        
        logger.info(f"Alert processing complete: {delivered_count} delivered, {failed_count} failed")
        return result

if __name__ == "__main__":
    # Setup paths
    base_dir = "/home/george/projects/clawblogs/news_system"
    db_path = f"{base_dir}/data/rss_aggregator.db"
    config_path = f"{base_dir}/config/alert_config.json"
    
    # Initialize and run alert system
    alert_system = SmartAlertSystem(db_path, config_path)
    result = alert_system.process_alerts()
    
    print(json.dumps(result, indent=2))
