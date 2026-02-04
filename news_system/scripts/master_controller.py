#!/usr/bin/env python3
"""
Master News & Market Monitoring System
Orchestrates RSS aggregation, market analysis, and smart alerting
"""

import json
import os
import sys
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class NewsMonitoringSystem:
    def __init__(self, base_dir: str = "/home/george/projects/clawblogs/news_system"):
        self.base_dir = base_dir
        self.scripts_dir = f"{base_dir}/scripts"
        self.data_dir = f"{base_dir}/data"
        self.logs_dir = f"{base_dir}/logs"
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{self.logs_dir}/master_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.rss_script = f"{self.scripts_dir}/rss_aggregator.py"
        self.analysis_script = f"{self.scripts_dir}/market_analysis.py"
        self.alert_script = f"{self.scripts_dir}/alert_system.py"
    
    def run_script(self, script_path: str, description: str) -> Dict:
        """Run a Python script and capture results"""
        try:
            self.logger.info(f"Starting: {description}")
            start_time = time.time()
            
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                self.logger.info(f"✅ {description} completed successfully in {execution_time:.1f}s")
                return {
                    'success': True,
                    'execution_time': execution_time,
                    'output': result.stdout,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                self.logger.error(f"❌ {description} failed with return code {result.returncode}")
                self.logger.error(f"Error output: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr,
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"⏰ {description} timed out after 5 minutes")
            return {
                'success': False,
                'error': 'Script execution timed out',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"💥 {description} failed with exception: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def load_latest_data(self, data_type: str) -> Optional[Dict]:
        """Load latest data from JSON files"""
        try:
            data_file = f"{self.data_dir}/{data_type}_latest.json"
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"Error loading {data_type} data: {str(e)}")
            return None
    
    def check_system_health(self) -> Dict:
        """Check overall system health"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {}
        }
        
        # Check RSS aggregator
        rss_data = self.load_latest_data('financial_news')
        health_status['components']['rss_aggregator'] = {
            'status': 'healthy' if rss_data and rss_data.get('total_articles', 0) > 0 else 'needs_attention',
            'last_update': rss_data.get('generated_at', 'unknown') if rss_data else 'never',
            'article_count': rss_data.get('total_articles', 0) if rss_data else 0
        }
        
        # Check market analysis
        analysis_data = self.load_latest_data('market_analysis')
        health_status['components']['market_analysis'] = {
            'status': 'healthy' if analysis_data and 'error' not in analysis_data else 'needs_attention',
            'last_update': analysis_data.get('analysis_timestamp', 'unknown') if analysis_data else 'never',
            'opportunities_found': len(analysis_data.get('investment_opportunities', [])) if analysis_data else 0
        }
        
        # Check alert system
        alert_config_exists = os.path.exists(f"{self.data_dir}/alert_config.json")
        health_status['components']['alert_system'] = {
            'status': 'healthy' if alert_config_exists else 'needs_setup',
            'config_loaded': alert_config_exists
        }
        
        # Determine overall health
        component_statuses = [comp['status'] for comp in health_status['components'].values()]
        if 'failed' in component_statuses:
            health_status['overall_status'] = 'failed'
        elif 'needs_attention' in component_statuses:
            health_status['overall_status'] = 'needs_attention'
        
        return health_status
    
    def run_full_cycle(self) -> Dict:
        """Run complete monitoring cycle"""
        cycle_start = datetime.now()
        self.logger.info("🚀 Starting full monitoring cycle")
        
        cycle_results = {
            'cycle_start': cycle_start.isoformat(),
            'components': {},
            'summary': {},
            'errors': []
        }
        
        try:
            # Step 1: RSS Aggregation
            rss_result = self.run_script(self.rss_script, "RSS Feed Aggregation")
            cycle_results['components']['rss_aggregation'] = rss_result
            
            if not rss_result['success']:
                cycle_results['errors'].append(f"RSS aggregation failed: {rss_result.get('error', 'Unknown error')}")
                return cycle_results
            
            # Small delay between steps
            time.sleep(2)
            
            # Step 2: Market Analysis
            analysis_result = self.run_script(self.analysis_script, "Market Analysis")
            cycle_results['components']['market_analysis'] = analysis_result
            
            if not analysis_result['success']:
                cycle_results['errors'].append(f"Market analysis failed: {analysis_result.get('error', 'Unknown error')}")
                return cycle_results
            
            # Small delay before alerts
            time.sleep(1)
            
            # Step 3: Smart Alerts
            alert_result = self.run_script(self.alert_script, "Smart Alert Generation")
            cycle_results['components']['alert_generation'] = alert_result
            
            # Generate summary
            cycle_end = datetime.now()
            cycle_results['cycle_end'] = cycle_end.isoformat()
            cycle_results['total_duration'] = (cycle_end - cycle_start).total_seconds()
            
            # Load latest data for summary
            rss_data = self.load_latest_data('financial_news')
            analysis_data = self.load_latest_data('market_analysis')
            
            cycle_results['summary'] = {
                'total_articles_collected': rss_data.get('total_articles', 0) if rss_data else 0,
                'high_impact_articles': len(rss_data.get('high_impact_articles', [])) if rss_data else 0,
                'investment_opportunities': len(analysis_data.get('investment_opportunities', [])) if analysis_data else 0,
                'market_recommendations': len(analysis_data.get('market_recommendations', [])) if analysis_data else 0,
                'market_sentiment': analysis_data.get('market_sentiment', {}).get('overall', 0) if analysis_data else 0,
                'feeds_successfully_processed': len([f for f in rss_data.get('feed_summary', {}).values() if f.get('success', False)]) if rss_data else 0
            }
            
            self.logger.info("✅ Full monitoring cycle completed successfully")
            return cycle_results
            
        except Exception as e:
            self.logger.error(f"💥 Full cycle failed with exception: {str(e)}")
            cycle_results['errors'].append(f"System exception: {str(e)}")
            return cycle_results
    
    def generate_system_report(self) -> str:
        """Generate comprehensive system report"""
        health = self.check_system_health()
        
        report = f"""
📊 FINANCIAL MONITORING SYSTEM REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🔍 SYSTEM HEALTH:
Overall Status: {health['overall_status'].upper()}
Last Check: {health['timestamp']}

RSS Aggregator: {health['components']['rss_aggregator']['status']} ({health['components']['rss_aggregator']['article_count']} articles)
Market Analysis: {health['components']['market_analysis']['status']} ({health['components']['market_analysis']['opportunities_found']} opportunities)
Alert System: {health['components']['alert_system']['status']}

📈 CURRENT MARKET DATA:
"""
        
        # Add latest market insights
        analysis_data = self.load_latest_data('market_analysis')
        if analysis_data and 'error' not in analysis_data:
            sentiment = analysis_data.get('market_sentiment', {})
            report += f"""
Market Sentiment: {sentiment.get('overall', 'N/A')}
Positive Articles: {sentiment.get('positive_count', 0)}
Negative Articles: {sentiment.get('negative_count', 0)}
Neutral Articles: {sentiment.get('neutral_count', 0)}

🎯 ACTIVE OPPORTUNITIES:
"""
            opportunities = analysis_data.get('investment_opportunities', [])
            for i, opp in enumerate(opportunities[:3], 1):
                report += f"{i}. {opp.get('timing', 'N/A')}: {opp.get('description', 'N/A')[:60]}...\n"
        
        report += f"""
🔧 SYSTEM CONFIGURATION:
• Data Directory: {self.data_dir}
• Scripts Location: {self.scripts_dir}
• Log Files: {self.logs_dir}
• Alert System: {'Active' if health['components']['alert_system']['config_loaded'] else 'Not Configured'}

📋 NEXT ACTIONS:
• RSS feeds monitored every 15 minutes
• Market analysis runs after each RSS cycle
• Smart alerts generated automatically
• Daily digest available upon request

---
Automated Financial Monitoring System
        """
        
        return report.strip()
    
    def save_system_report(self, report: str) -> str:
        """Save system report to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"{self.logs_dir}/system_report_{timestamp}.txt"
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # Save latest report for quick access
            latest_report = f"{self.logs_dir}/system_report_latest.txt"
            with open(latest_report, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.logger.info(f"System report saved to {report_filename}")
            return report_filename
            
        except Exception as e:
            self.logger.error(f"Error saving system report: {str(e)}")
            return ""

def main():
    """Main execution function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = "cycle"  # Default to full cycle
    
    system = NewsMonitoringSystem()
    
    if command == "cycle":
        print("🔄 Running full monitoring cycle...")
        results = system.run_full_cycle()
        
        if results['errors']:
            print(f"⚠️  Cycle completed with {len(results['errors'])} errors:")
            for error in results['errors']:
                print(f"  • {error}")
        else:
            print("✅ Full cycle completed successfully!")
        
        # Display summary
        if 'summary' in results:
            summary = results['summary']
            print(f"\n📊 Cycle Summary:")
            print(f"  Articles Collected: {summary.get('total_articles_collected', 0)}")
            print(f"  High Impact Articles: {summary.get('high_impact_articles', 0)}")
            print(f"  Investment Opportunities: {summary.get('investment_opportunities', 0)}")
            print(f"  Market Recommendations: {summary.get('market_recommendations', 0)}")
            print(f"  Market Sentiment: {summary.get('market_sentiment', 0)}")
            print(f"  Duration: {results.get('total_duration', 0):.1f} seconds")
    
    elif command == "health":
        print("🔍 Checking system health...")
        health = system.check_system_health()
        print(f"Overall Status: {health['overall_status'].upper()}")
        for component, status in health['components'].items():
            print(f"  {component}: {status['status']}")
    
    elif command == "report":
        print("📊 Generating system report...")
        report = system.generate_system_report()
        filename = system.save_system_report(report)
        print(f"Report saved to: {filename}")
        print("\n" + report)
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: cycle, health, report")

if __name__ == "__main__":
    main()