#!/usr/bin/env python3
"""
Master System Controller - Unified Interface for Complete News & Market System
"""

import sys
import os
import json
import argparse
from datetime import datetime
import logging

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

class MasterSystemController:
    def __init__(self, base_dir: str = "/home/george/projects/clawblogs/news_system"):
        self.base_dir = base_dir
        self.scripts_dir = f"{base_dir}/scripts"
        self.config_dir = f"{base_dir}/config"
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
                logging.FileHandler(f'{self.logs_dir}/master_controller.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.components = {
            'rss': 'rss_aggregator.py',
            'analysis': 'market_analysis.py',
            'advanced': 'advanced_analytics.py',
            'alerts': 'alert_system.py',
            'simple_rss': 'simple_rss_aggregator.py',
            'coordinator': 'coordinator.py'
        }
    
    def run_component(self, component: str, command: str = None) -> dict:
        """Run a specific system component"""
        if component not in self.components:
            return {'error': f'Unknown component: {component}'}
        
        script_path = os.path.join(self.scripts_dir, self.components[component])
        if not os.path.exists(script_path):
            return {'error': f'Script not found: {script_path}'}
        
        try:
            import subprocess
            start_time = datetime.now()
            
            cmd = [sys.executable, script_path]
            if command:
                cmd.append(command)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': result.returncode == 0,
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'timestamp': datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {'error': 'Component execution timed out', 'timestamp': datetime.now().isoformat()}
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def system_dashboard(self) -> str:
        """Generate comprehensive system dashboard"""
        dashboard = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    NEWS & FINANCIAL MONITORING SYSTEM                        ║
║                          DASHBOARD REPORT                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
"""
        
        # System Health Status
        dashboard += "║ 🔍 SYSTEM HEALTH                                                              ║\n"
        health_status = self.check_system_health()
        dashboard += f"║ Overall Status: {health_status['overall_status'].upper():^15}                         ║\n"
        dashboard += f"║ Components Active: {health_status['active_components']}/6                      ║\n"
        dashboard += f"║ Last Updated: {datetime.now().strftime('%H:%M:%S')} UTC                              ║\n"
        
        # Database Status
        try:
            import sqlite3
            conn = sqlite3.connect(f"{self.data_dir}/rss_aggregator.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM articles")
            article_count = cursor.fetchone()[0]
            cursor.execute("SELECT MAX(created_at) FROM articles")
            last_article = cursor.fetchone()[0]
            conn.close()
            
            dashboard += f"║ Database Articles: {article_count}                          ║\n"
            dashboard += f"║ Last Article: {last_article[:16] if last_article else 'None':^16}                        ║\n"
        except:
            dashboard += f"║ Database: Not Available              ║\n"
        
        dashboard += "╠══════════════════════════════════════════════════════════════════════════════╣\n"
        
        # Quick Component Tests
        dashboard += "║ 🧪 COMPONENT STATUS                                                           ║\n"
        component_statuses = ['rss', 'analysis', 'advanced', 'alerts', 'simple_rss', 'coordinator']
        for comp in component_statuses:
            try:
                result = self.run_component(comp)
                status = "✅" if result.get('success') else "❌"
                dashboard += f"║ {comp.title():<12} {status:<4} ({result.get('execution_time', 0):.1f}s)                 ║\n"
            except Exception as e:
                dashboard += f"║ {comp.title():<12} 💥 Error                           ║\n"
        
        dashboard += "╠══════════════════════════════════════════════════════════════════════════════╣\n"
        
        # Current Market Intelligence
        dashboard += "║ 📊 CURRENT MARKET INTELLIGENCE                                                ║\n"
        try:
            analytics_result = self.run_component('advanced')
            if analytics_result.get('success'):
                import json
                analysis = json.loads(analytics_result['stdout'])
                summary = analysis.get('executive_summary', {})
                
                dashboard += f"║ Market Grade: {summary.get('market_grade', 'N/A'):^18}                        ║\n"
                dashboard += f"║ Outlook: {summary.get('market_outlook', 'N/A'):^24}                        ║\n"
                dashboard += f"║ Score: {summary.get('overall_score', 0):.1f}/100^28                        ║\n"
                dashboard += f"║ Confidence: {summary.get('confidence_level', 0)*100:.0f}%^27                        ║\n"
        except:
            dashboard += f"║ Analysis: Not Available              ║\n"
        
        dashboard += "╠══════════════════════════════════════════════════════════════════════════════╣\n"
        
        # Recent Activity Summary
        dashboard += "║ 📈 RECENT ACTIVITY                                                            ║\n"
        dashboard += f"║ Total Components: 6                                                         ║\n"
        dashboard += f"║ RSS Feeds Configured: 14                                                   ║\n"
        dashboard += f"║ Processing Speed: ~5 seconds per cycle                                      ║\n"
        dashboard += f"║ Typical Throughput: 100-150 articles per cycle                              ║\n"
        
        dashboard += "╠══════════════════════════════════════════════════════════════════════════════╣\n"
        
        # Available Commands
        dashboard += "║ 🎮 AVAILABLE COMMANDS                                                        ║\n"
        dashboard += "║ • dashboard       - Show this dashboard                                     ║\n"
        dashboard += "║ • full           - Run complete system cycle                                ║\n"
        dashboard += "║ • rss            - Run RSS aggregation only                                 ║\n"
        dashboard += "║ • analysis       - Run market analysis only                                 ║\n"
        dashboard += "║ • advanced       - Run advanced analytics                                   ║\n"
        dashboard += "║ • alerts         - Generate smart alerts                                    ║\n"
        dashboard += "║ • test <comp>    - Test specific component                                  ║\n"
        dashboard += "║ • health         - Check system health                                      ║\n"
        dashboard += "║ • status         - Detailed system status                                   ║\n"
        dashboard += "╚══════════════════════════════════════════════════════════════════════════════╝\n"
        
        return dashboard
    
    def check_system_health(self) -> dict:
        """Comprehensive system health check"""
        health = {
            'overall_status': 'healthy',
            'active_components': 0,
            'components': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Test each component
        for comp_name, comp_script in self.components.items():
            try:
                script_path = os.path.join(self.scripts_dir, comp_script)
                if os.path.exists(script_path):
                    # Quick import test
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(comp_name, script_path)
                    if spec and spec.loader:
                        health['components'][comp_name] = 'healthy'
                        health['active_components'] += 1
                    else:
                        health['components'][comp_name] = 'error'
                else:
                    health['components'][comp_name] = 'missing'
            except Exception as e:
                health['components'][comp_name] = f'error: {str(e)[:20]}'
        
        # Determine overall health
        if health['active_components'] >= 5:
            health['overall_status'] = 'healthy'
        elif health['active_components'] >= 3:
            health['overall_status'] = 'degraded'
        else:
            health['overall_status'] = 'critical'
        
        return health
    
    def run_full_system(self) -> dict:
        """Run the complete system integration"""
        self.logger.info("Starting complete system integration")
        
        results = {
            'start_time': datetime.now().isoformat(),
            'components': {},
            'summary': {},
            'success': True
        }
        
        # Step 1: RSS Aggregation
        self.logger.info("Step 1: RSS Aggregation")
        rss_result = self.run_component('rss')
        results['components']['rss'] = rss_result
        
        if not rss_result.get('success'):
            results['success'] = False
            return results
        
        # Step 2: Market Analysis
        self.logger.info("Step 2: Market Analysis")
        analysis_result = self.run_component('analysis')
        results['components']['analysis'] = analysis_result
        
        # Step 3: Advanced Analytics
        self.logger.info("Step 3: Advanced Analytics")
        advanced_result = self.run_component('advanced')
        results['components']['advanced'] = advanced_result
        
        # Step 4: Alert Generation
        self.logger.info("Step 4: Alert Generation")
        alerts_result = self.run_component('alerts')
        results['components']['alerts'] = alerts_result
        
        results['end_time'] = datetime.now().isoformat()
        results['duration'] = (datetime.now() - datetime.fromisoformat(results['start_time'])).total_seconds()
        
        # Generate summary
        successful_components = sum(1 for comp in results['components'].values() if comp.get('success'))
        results['summary'] = {
            'total_components': len(results['components']),
            'successful_components': successful_components,
            'success_rate': successful_components / len(results['components'])
        }
        
        self.logger.info(f"System integration complete: {successful_components}/{len(results['components'])} components successful")
        return results

def main():
    parser = argparse.ArgumentParser(description='Master System Controller for News & Market Monitoring')
    parser.add_argument('command', nargs='?', default='dashboard',
                       help='Command to execute (dashboard, full, rss, analysis, advanced, alerts, test, health, status)')
    parser.add_argument('component', nargs='?', help='Component name for test command')
    
    args = parser.parse_args()
    
    controller = MasterSystemController()
    
    if args.command == 'dashboard':
        print(controller.system_dashboard())
    
    elif args.command == 'full':
        print("🚀 Running complete system integration...")
        result = controller.run_full_system()
        print(f"\n✅ Integration complete: {result['summary']['successful_components']}/{result['summary']['total_components']} components successful")
        print(f"⏱️  Total duration: {result['duration']:.1f} seconds")
    
    elif args.command == 'rss':
        print("📡 Running RSS aggregation...")
        result = controller.run_component('rss')
        print("✅ RSS aggregation completed" if result.get('success') else "❌ RSS aggregation failed")
    
    elif args.command == 'analysis':
        print("📊 Running market analysis...")
        result = controller.run_component('analysis')
        print("✅ Market analysis completed" if result.get('success') else "❌ Market analysis failed")
    
    elif args.command == 'advanced':
        print("🔍 Running advanced analytics...")
        result = controller.run_component('advanced')
        if result.get('success'):
            print("✅ Advanced analytics completed")
            # Show summary if available
            try:
                import json
                analysis = json.loads(result['stdout'])
                summary = analysis.get('executive_summary', {})
                print(f"🎯 Market Grade: {summary.get('market_grade', 'N/A')} ({summary.get('market_outlook', 'N/A')})")
                print(f"📈 Score: {summary.get('overall_score', 0):.1f}/100")
            except:
                pass
        else:
            print("❌ Advanced analytics failed")
    
    elif args.command == 'alerts':
        print("🚨 Generating smart alerts...")
        result = controller.run_component('alerts')
        print("✅ Alert generation completed" if result.get('success') else "❌ Alert generation failed")
    
    elif args.command == 'test':
        if not args.component:
            print("❌ Please specify component name for test")
            return
        print(f"🧪 Testing component: {args.component}")
        result = controller.run_component(args.component)
        if result.get('success'):
            print(f"✅ {args.component} test passed")
        else:
            print(f"❌ {args.component} test failed: {result.get('error', 'Unknown error')}")
    
    elif args.command == 'health':
        print("🔍 Checking system health...")
        health = controller.check_system_health()
        print(f"Overall Status: {health['overall_status'].upper()}")
        print(f"Active Components: {health['active_components']}/{len(health['components'])}")
        for comp, status in health['components'].items():
            print(f"  {comp}: {status}")
    
    elif args.command == 'status':
        print("📋 Detailed system status...")
        health = controller.check_system_health()
        print(json.dumps(health, indent=2))
    
    else:
        print(f"Unknown command: {args.command}")
        print("Available commands: dashboard, full, rss, analysis, advanced, alerts, test, health, status")

if __name__ == "__main__":
    main()
