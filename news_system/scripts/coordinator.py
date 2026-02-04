#!/usr/bin/env python3
"""
News System Coordinator - Main orchestrator for all components
"""

import sys
import os
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, Optional

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/george/projects/clawblogs/news_system/logs/coordinator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsSystemCoordinator:
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or "/home/george/projects/clawblogs/news_system"
        self.scripts_dir = os.path.join(self.base_dir, "scripts")
        self.config_dir = os.path.join(self.base_dir, "config")
        self.data_dir = os.path.join(self.base_dir, "data")
        self.logs_dir = os.path.join(self.base_dir, "logs")
        
        # Ensure directories exist
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Component paths
        self.rss_db_path = os.path.join(self.data_dir, "rss_aggregator.db")
        self.feeds_config_path = os.path.join(self.config_dir, "feeds_config.json")
        self.alert_config_path = os.path.join(self.config_dir, "alert_config.json")
        
        logger.info("News System Coordinator initialized")
    
    def run_rss_aggregation(self) -> Dict:
        """Run RSS feed aggregation"""
        try:
            logger.info("Starting RSS aggregation cycle")
            from rss_aggregator import RSSAggregator
            
            aggregator = RSSAggregator(self.rss_db_path, self.feeds_config_path)
            result = aggregator.run_aggregation()
            
            logger.info(f"RSS aggregation completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"RSS aggregation failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def run_market_analysis(self) -> Dict:
        """Run market analysis on aggregated data"""
        try:
            logger.info("Starting market analysis")
            from market_analysis import MarketAnalysisEngine
            
            engine = MarketAnalysisEngine(self.rss_db_path)
            advice = engine.get_investment_advice()
            
            logger.info(f"Market analysis completed with {advice.get('timing_recommendation', {}).get('action', 'unknown')} recommendation")
            return advice
            
        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def run_alert_system(self) -> Dict:
        """Run smart alert system"""
        try:
            logger.info("Starting alert system processing")
            from alert_system import SmartAlertSystem
            
            alert_system = SmartAlertSystem(self.rss_db_path, self.alert_config_path)
            result = alert_system.process_alerts()
            
            logger.info(f"Alert system processed {result.get('alerts_delivered', 0)} alerts")
            return result
            
        except Exception as e:
            logger.error(f"Alert system failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def run_full_cycle(self) -> Dict:
        """Run complete news system cycle"""
        logger.info("="*80)
        logger.info("STARTING FULL NEWS SYSTEM CYCLE")
        logger.info("="*80)
        
        cycle_start = datetime.now()
        results = {
            "cycle_start": cycle_start.isoformat(),
            "components": {}
        }
        
        # Step 1: RSS Aggregation
        logger.info("Step 1: RSS Feed Aggregation")
        rss_result = self.run_rss_aggregation()
        results["components"]["rss_aggregation"] = rss_result
        
        # Step 2: Market Analysis
        logger.info("Step 2: Market Analysis")
        analysis_result = self.run_market_analysis()
        results["components"]["market_analysis"] = analysis_result
        
        # Step 3: Alert Generation
        logger.info("Step 3: Smart Alert System")
        alert_result = self.run_alert_system()
        results["components"]["alert_system"] = alert_result
        
        # Calculate cycle statistics
        cycle_end = datetime.now()
        cycle_duration = (cycle_end - cycle_start).total_seconds()
        
        results["cycle_end"] = cycle_end.isoformat()
        results["duration_seconds"] = cycle_duration
        results["status"] = "completed"
        
        # Summary statistics
        total_articles = rss_result.get("total_saved", 0)
        alerts_sent = alert_result.get("alerts_delivered", 0)
        sentiment = analysis_result.get("sentiment_analysis", {}).get("sentiment", "unknown")
        
        logger.info("="*80)
        logger.info("CYCLE COMPLETED SUCCESSFULLY")
        logger.info(f"Duration: {cycle_duration:.1f} seconds")
        logger.info(f"Articles processed: {total_articles}")
        logger.info(f"Alerts generated: {alerts_sent}")
        logger.info(f"Market sentiment: {sentiment}")
        logger.info("="*80)
        
        return results
    
    def get_system_status(self) -> Dict:
        """Get current system status and health"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "directories": {
                "base_dir": self.base_dir,
                "scripts_dir": self.scripts_dir,
                "config_dir": self.config_dir,
                "data_dir": self.data_dir,
                "logs_dir": self.logs_dir
            },
            "files": {
                "rss_db": os.path.exists(self.rss_db_path),
                "feeds_config": os.path.exists(self.feeds_config_path),
                "alert_config": os.path.exists(self.alert_config_path)
            },
            "components": {}
        }
        
        # Check component availability
        try:
            from rss_aggregator import RSSAggregator
            status["components"]["rss_aggregator"] = "available"
        except ImportError:
            status["components"]["rss_aggregator"] = "unavailable"
        
        try:
            from market_analysis import MarketAnalysisEngine
            status["components"]["market_analysis"] = "available"
        except ImportError:
            status["components"]["market_analysis"] = "unavailable"
        
        try:
            from alert_system import SmartAlertSystem
            status["components"]["alert_system"] = "available"
        except ImportError:
            status["components"]["alert_system"] = "unavailable"
        
        # Database connectivity
        try:
            import sqlite3
            conn = sqlite3.connect(self.rss_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM articles")
            article_count = cursor.fetchone()[0]
            conn.close()
            status["database"] = {"connected": True, "articles": article_count}
        except Exception as e:
            status["database"] = {"connected": False, "error": str(e)}
        
        return status
    
    def get_recent_summary(self, hours: int = 24) -> Dict:
        """Get summary of recent system activity"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "period_hours": hours,
            "data": {}
        }
        
        try:
            # Get recent articles
            conn = sqlite3.connect(self.rss_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN category = 'financial' THEN 1 ELSE 0 END) as financial,
                       SUM(CASE WHEN category = 'technology' THEN 1 ELSE 0 END) as technology,
                       AVG(score) as avg_score,
                       MAX(score) as max_score
                FROM articles 
                WHERE created_at >= datetime('now', '-{} hours')
            '''.format(hours))
            
            row = cursor.fetchone()
            if row:
                summary["data"]["articles"] = {
                    "total": row[0],
                    "financial": row[1],
                    "technology": row[2],
                    "average_score": round(row[3], 2),
                    "max_score": row[4]
                }
            
            # Get top sources
            cursor.execute('''
                SELECT source, COUNT(*) as count, AVG(score) as avg_score
                FROM articles 
                WHERE created_at >= datetime('now', '-{} hours')
                GROUP BY source
                ORDER BY count DESC
                LIMIT 5
            '''.format(hours))
            
            sources = []
            for row in cursor.fetchall():
                sources.append({
                    "source": row[0],
                    "count": row[1],
                    "avg_score": round(row[2], 2)
                })
            summary["data"]["top_sources"] = sources
            
            conn.close()
            
        except Exception as e:
            summary["error"] = str(e)
        
        return summary
    
    def save_cycle_result(self, result: Dict, filename: str = None) -> str:
        """Save cycle result to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cycle_result_{timestamp}.json"
        
        filepath = os.path.join(self.logs_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Cycle result saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save cycle result: {e}")
            return ""

def main():
    parser = argparse.ArgumentParser(description='News System Coordinator')
    parser.add_argument('action', choices=[
        'full', 'rss', 'analysis', 'alerts', 'status', 'summary'
    ], help='Action to perform')
    parser.add_argument('--hours', type=int, default=24, help='Hours back for analysis')
    parser.add_argument('--save', action='store_true', help='Save results to file')
    
    args = parser.parse_args()
    
    coordinator = NewsSystemCoordinator()
    
    if args.action == 'full':
        result = coordinator.run_full_cycle()
        if args.save:
            coordinator.save_cycle_result(result)
        print(json.dumps(result, indent=2))
    
    elif args.action == 'rss':
        result = coordinator.run_rss_aggregation()
        print(json.dumps(result, indent=2))
    
    elif args.action == 'analysis':
        result = coordinator.run_market_analysis()
        print(json.dumps(result, indent=2))
    
    elif args.action == 'alerts':
        result = coordinator.run_alert_system()
        print(json.dumps(result, indent=2))
    
    elif args.action == 'status':
        result = coordinator.get_system_status()
        print(json.dumps(result, indent=2))
    
    elif args.action == 'summary':
        result = coordinator.get_recent_summary(args.hours)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
