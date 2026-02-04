#!/usr/bin/env python3
"""
Advanced News Analytics Engine
Enhanced analysis combining multiple data sources for superior market intelligence
"""

import json
import sqlite3
from datetime import datetime, timedelta
import statistics
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MarketInsight:
    insight_type: str
    confidence: float
    impact_level: str
    description: str
    actionable_recommendation: str
    evidence: List[str]
    timestamp: str

class AdvancedAnalyticsEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
        # Enhanced keyword mapping for better analysis
        self.sentiment_keywords = {
            'very_positive': [
                'surge', 'rocket', 'skyrocket', 'breakthrough', 'record high',
                'strong growth', 'outperform', 'beat expectations', 'exceed'
            ],
            'positive': [
                'rise', 'gain', 'increase', 'growth', 'improve', 'positive',
                'strong', 'robust', 'solid', 'confident', 'optimistic'
            ],
            'neutral': [
                'stable', 'steady', 'unchanged', 'flat', 'sideways',
                'maintain', 'consistent', 'moderate'
            ],
            'negative': [
                'decline', 'fall', 'drop', 'decrease', 'weak', 'concern',
                'worry', 'risk', 'challenge', 'headwind', 'pressure'
            ],
            'very_negative': [
                'crash', 'plunge', 'collapse', 'tumble', 'crisis',
                'severe', 'major decline', 'sharp drop', 'panic', 'tank'
            ]
        }
        
        # Market impact indicators
        self.impact_indicators = {
            'critical': ['federal reserve', 'fed rate', 'market crash', 'recession'],
            'high': ['earnings', 'merger', 'acquisition', 'ipo', 'dividend'],
            'medium': ['analyst', 'upgrade', 'downgrade', 'rating', 'guidance'],
            'low': ['report', 'study', 'survey', 'poll']
        }
        
        # Sector impact mapping
        self.sector_keywords = {
            'technology': ['tech', 'software', 'ai', 'cloud', 'digital', 'cyber', 'data'],
            'financial': ['bank', 'finance', 'credit', 'loan', 'insurance', 'investment'],
            'healthcare': ['health', 'medical', 'pharmaceutical', 'biotech', 'hospital'],
            'energy': ['oil', 'gas', 'renewable', 'solar', 'wind', 'electric'],
            'consumer': ['retail', 'consumer', 'shopping', 'brand', 'luxury'],
            'industrial': ['manufacturing', 'industrial', 'infrastructure', 'construction'],
            'real_estate': ['real estate', 'property', 'housing', 'reit']
        }
    
    def get_comprehensive_analysis(self, hours_back: int = 24) -> Dict:
        """Perform comprehensive market analysis"""
        logger.info("Starting advanced market analysis")
        
        # Get all recent articles
        articles = self._get_recent_articles(hours_back)
        if not articles:
            return {'error': 'No articles found for analysis'}
        
        # Perform multiple analysis layers
        sentiment_analysis = self._analyze_sentiment_advanced(articles)
        impact_analysis = self._analyze_market_impact(articles)
        sector_analysis = self._analyze_sector_trends(articles)
        timing_analysis = self._analyze_investment_timing(articles, sentiment_analysis)
        risk_analysis = self._assess_market_risk(articles, sentiment_analysis)
        
        # Generate insights
        insights = self._generate_market_insights(
            sentiment_analysis, impact_analysis, sector_analysis, timing_analysis, risk_analysis
        )
        
        # Create comprehensive report
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_period_hours': hours_back,
            'article_count': len(articles),
            'sentiment_analysis': sentiment_analysis,
            'market_impact': impact_analysis,
            'sector_analysis': sector_analysis,
            'timing_analysis': timing_analysis,
            'risk_assessment': risk_analysis,
            'key_insights': [self._insight_to_dict(insight) for insight in insights],
            'executive_summary': self._create_executive_summary(
                sentiment_analysis, impact_analysis, insights
            )
        }
        
        logger.info(f"Advanced analysis complete with {len(insights)} key insights")
        return report
    
    def _get_recent_articles(self, hours_back: int) -> List[Dict]:
        """Get recent articles from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, description, source, category, score, published, created_at
            FROM articles 
            WHERE created_at >= datetime('now', '-{} hours')
            ORDER BY score DESC, created_at DESC
        '''.format(hours_back))
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'title': row[0],
                'description': row[1] or '',
                'source': row[2],
                'category': row[3],
                'score': row[4],
                'published': row[5],
                'created_at': row[6]
            })
        
        conn.close()
        return articles
    
    def _analyze_sentiment_advanced(self, articles: List[Dict]) -> Dict:
        """Advanced sentiment analysis with confidence scoring"""
        sentiment_scores = []
        keyword_frequency = {}
        
        for article in articles:
            text = f"{article['title']} {article['description']}".lower()
            
            # Calculate sentiment score
            sentiment_score = 0
            sentiment_strength = 'neutral'
            
            # Count keyword occurrences with weights
            for category, keywords in self.sentiment_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        weight = self._get_sentiment_weight(category)
                        sentiment_score += weight
                        keyword_frequency[keyword] = keyword_frequency.get(keyword, 0) + 1
            
            # Apply article score boost
            if article['score'] > 20:
                sentiment_score *= 1.5
            elif article['score'] > 10:
                sentiment_score *= 1.2
            
            # Normalize sentiment score
            if sentiment_score > 3:
                sentiment_strength = 'very_positive'
            elif sentiment_score > 1:
                sentiment_strength = 'positive'
            elif sentiment_score < -3:
                sentiment_strength = 'very_negative'
            elif sentiment_score < -1:
                sentiment_strength = 'negative'
            
            sentiment_scores.append({
                'score': sentiment_score,
                'strength': sentiment_strength,
                'article': article
            })
        
        # Calculate overall sentiment
        if sentiment_scores:
            avg_score = statistics.mean([s['score'] for s in sentiment_scores])
            sentiment_distribution = {
                'very_positive': len([s for s in sentiment_scores if s['strength'] == 'very_positive']),
                'positive': len([s for s in sentiment_scores if s['strength'] == 'positive']),
                'neutral': len([s for s in sentiment_scores if s['strength'] == 'neutral']),
                'negative': len([s for s in sentiment_scores if s['strength'] == 'negative']),
                'very_negative': len([s for s in sentiment_scores if s['strength'] == 'very_negative'])
            }
            
            # Determine dominant sentiment
            dominant_sentiment = max(sentiment_distribution, key=sentiment_distribution.get)
            confidence = sentiment_distribution[dominant_sentiment] / len(sentiment_scores)
        else:
            avg_score = 0
            dominant_sentiment = 'neutral'
            confidence = 0.5
            sentiment_distribution = {'neutral': 1}
        
        return {
            'overall_sentiment': dominant_sentiment,
            'average_score': round(avg_score, 2),
            'confidence': round(confidence, 2),
            'distribution': sentiment_distribution,
            'top_keywords': dict(sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)[:10]),
            'sentiment_trend': self._calculate_sentiment_trend(sentiment_scores)
        }
    
    def _get_sentiment_weight(self, category: str) -> float:
        """Get weight for sentiment category"""
        weights = {
            'very_positive': 2.0,
            'positive': 1.0,
            'neutral': 0.0,
            'negative': -1.0,
            'very_negative': -2.0
        }
        return weights.get(category, 0.0)
    
    def _calculate_sentiment_trend(self, sentiment_scores: List[Dict]) -> str:
        """Calculate if sentiment is improving or declining"""
        if len(sentiment_scores) < 2:
            return 'stable'
        
        # Sort by creation time (assuming chronological order from query)
        recent_avg = statistics.mean([s['score'] for s in sentiment_scores[:5]])  # Last 5 articles
        older_avg = statistics.mean([s['score'] for s in sentiment_scores[-5:]])  # Older 5 articles
        
        trend_change = recent_avg - older_avg
        
        if trend_change > 0.5:
            return 'improving'
        elif trend_change < -0.5:
            return 'declining'
        else:
            return 'stable'
    
    def _analyze_market_impact(self, articles: List[Dict]) -> Dict:
        """Analyze market impact potential of articles"""
        impact_categories = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        impact_articles = []
        
        for article in articles:
            text = f"{article['title']} {article['description']}".lower()
            max_impact = 'low'
            
            # Check for impact indicators
            for impact_level, keywords in self.impact_indicators.items():
                if any(keyword in text for keyword in keywords):
                    max_impact = impact_level
            
            impact_categories[max_impact] += 1
            
            if max_impact in ['critical', 'high']:
                impact_articles.append({
                    'title': article['title'],
                    'impact_level': max_impact,
                    'score': article['score'],
                    'source': article['source']
                })
        
        # Sort impact articles by score
        impact_articles.sort(key=lambda x: x['score'], reverse=True)
        
        # Calculate impact score
        total_impact_score = (
            impact_categories['critical'] * 4 +
            impact_categories['high'] * 3 +
            impact_categories['medium'] * 2 +
            impact_categories['low'] * 1
        )
        
        return {
            'impact_distribution': impact_categories,
            'total_impact_score': total_impact_score,
            'high_impact_articles': impact_articles[:10],
            'market_stress_indicator': self._calculate_market_stress(impact_categories)
        }
    
    def _calculate_market_stress(self, impact_categories: Dict) -> str:
        """Calculate market stress level"""
        critical_weight = impact_categories['critical']
        high_weight = impact_categories['high']
        
        if critical_weight > 0 or high_weight > 3:
            return 'high_stress'
        elif high_weight > 1:
            return 'moderate_stress'
        else:
            return 'low_stress'
    
    def _analyze_sector_trends(self, articles: List[Dict]) -> Dict:
        """Analyze sector-specific trends"""
        sector_mentions = {sector: 0 for sector in self.sector_keywords}
        sector_sentiment = {sector: [] for sector in self.sector_keywords}
        
        for article in articles:
            text = f"{article['title']} {article['description']}".lower()
            
            for sector, keywords in self.sector_keywords.items():
                if any(keyword in text for keyword in keywords):
                    sector_mentions[sector] += 1
                    # Calculate simple sentiment for sector
                    if any(pos_word in text for pos_word in ['gain', 'rise', 'growth', 'positive']):
                        sector_sentiment[sector].append(1)
                    elif any(neg_word in text for neg_word in ['fall', 'decline', 'drop', 'negative']):
                        sector_sentiment[sector].append(-1)
        
        # Calculate sector metrics
        sector_metrics = {}
        for sector in self.sector_keywords:
            mentions = sector_mentions[sector]
            sentiments = sector_sentiment[sector]
            
            if mentions > 0:
                avg_sentiment = statistics.mean(sentiments) if sentiments else 0
                sector_metrics[sector] = {
                    'mentions': mentions,
                    'sentiment_score': round(avg_sentiment, 2),
                    'momentum': 'positive' if avg_sentiment > 0.1 else 'negative' if avg_sentiment < -0.1 else 'neutral'
                }
            else:
                sector_metrics[sector] = {
                    'mentions': 0,
                    'sentiment_score': 0,
                    'momentum': 'neutral'
                }
        
        # Identify top performing and struggling sectors
        active_sectors = [(sector, data['mentions']) for sector, data in sector_metrics.items() if data['mentions'] > 0]
        active_sectors.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'sector_metrics': sector_metrics,
            'most_active_sectors': active_sectors[:3],
            'sector_sentiment_leader': max(sector_metrics, key=lambda x: sector_metrics[x]['sentiment_score']) if any(data['mentions'] > 0 for data in sector_metrics.values()) else 'none',
            'sector_activity_heat_map': self._create_sector_heat_map(sector_metrics)
        }
    
    def _create_sector_heat_map(self, sector_metrics: Dict) -> Dict:
        """Create a visual representation of sector activity"""
        heat_map = {}
        for sector, metrics in sector_metrics.items():
            if metrics['mentions'] > 0:
                # Combine mentions and sentiment for heat score
                heat_score = metrics['mentions'] * (1 + metrics['sentiment_score'])
                heat_map[sector] = {
                    'heat_level': 'high' if heat_score > 5 else 'medium' if heat_score > 2 else 'low',
                    'heat_score': round(heat_score, 2)
                }
            else:
                heat_map[sector] = {'heat_level': 'none', 'heat_score': 0}
        return heat_map
    
    def _analyze_investment_timing(self, articles: List[Dict], sentiment_analysis: Dict) -> Dict:
        """Advanced investment timing analysis"""
        current_hour = datetime.now().hour
        
        # Market timing windows (Eastern Time)
        timing_windows = {
            'pre_market': (4, 9.5),
            'market_open': (9.5, 10.5),
            'mid_morning': (10.5, 12),
            'lunch_hour': (12, 13),
            'afternoon': (13, 15),
            'market_close': (15, 16),
            'after_hours': (16, 20)
        }
        
        # Determine current market phase
        current_phase = 'after_hours'
        for phase, (start, end) in timing_windows.items():
            if start <= current_hour < end:
                current_phase = phase
                break
        
        # Analyze current opportunity
        overall_sentiment = sentiment_analysis['overall_sentiment']
        confidence = sentiment_analysis['confidence']
        trend = sentiment_analysis['sentiment_trend']
        
        # Timing recommendation logic
        if overall_sentiment in ['very_positive', 'positive'] and confidence > 0.6:
            if trend == 'improving':
                timing_action = 'buy_aggressive'
                risk_level = 'medium'
            else:
                timing_action = 'buy_selective'
                risk_level = 'medium'
        elif overall_sentiment in ['very_negative', 'negative'] and confidence > 0.6:
            timing_action = 'reduce_exposure'
            risk_level = 'high'
        else:
            timing_action = 'hold_wait'
            risk_level = 'low'
        
        # Adjust for current market phase
        if current_phase in ['lunch_hour']:
            risk_level = 'high'  # Avoid trading during lunch
            if timing_action == 'buy_aggressive':
                timing_action = 'buy_conservative'
        
        return {
            'current_phase': current_phase,
            'timing_action': timing_action,
            'risk_level': risk_level,
            'confidence': confidence,
            'optimal_next_phases': self._get_optimal_phases(timing_action),
            'phase_adjustments': self._get_phase_adjustments(current_phase),
            'reasoning': self._generate_timing_reasoning(overall_sentiment, trend, confidence, current_phase)
        }
    
    def _get_optimal_phases(self, timing_action: str) -> List[str]:
        """Get optimal market phases for current timing action"""
        phase_mapping = {
            'buy_aggressive': ['market_open', 'market_close'],
            'buy_selective': ['mid_morning', 'afternoon'],
            'buy_conservative': ['mid_morning'],
            'reduce_exposure': ['market_close', 'after_hours'],
            'hold_wait': ['any']
        }
        return phase_mapping.get(timing_action, ['any'])
    
    def _get_phase_adjustments(self, current_phase: str) -> Dict:
        """Get timing adjustments based on current market phase"""
        adjustments = {
            'lunch_hour': 'Avoid new positions, low liquidity',
            'market_open': 'High volatility, fast execution needed',
            'market_close': 'Good for momentum trades',
            'after_hours': 'Limited liquidity, news-driven moves',
            'pre_market': 'Set limit orders, limited participation'
        }
        return {'current_advice': adjustments.get(current_phase, 'Standard trading conditions')}
    
    def _generate_timing_reasoning(self, sentiment: str, trend: str, confidence: float, phase: str) -> str:
        """Generate reasoning for timing recommendation"""
        reasoning_parts = []
        
        if confidence > 0.7:
            reasoning_parts.append(f"High confidence ({confidence:.0%}) in {sentiment} sentiment")
        elif confidence > 0.5:
            reasoning_parts.append(f"Moderate confidence ({confidence:.0%}) in market assessment")
        
        if trend == 'improving':
            reasoning_parts.append("sentiment is improving")
        elif trend == 'declining':
            reasoning_parts.append("sentiment is declining")
        
        reasoning_parts.append(f"current market phase: {phase.replace('_', ' ')}")
        
        return ". ".join(reasoning_parts) + "."
    
    def _assess_market_risk(self, articles: List[Dict], sentiment_analysis: Dict) -> Dict:
        """Comprehensive market risk assessment"""
        risk_factors = []
        risk_score = 0
        
        # Analyze for specific risk indicators
        risk_keywords = [
            'volatility', 'uncertainty', 'concern', 'risk', 'fear', 'panic',
            'recession', 'crisis', 'correction', 'decline'
        ]
        
        for article in articles:
            text = f"{article['title']} {article['description']}".lower()
            
            for keyword in risk_keywords:
                if keyword in text:
                    risk_factors.append({
                        'keyword': keyword,
                        'article_title': article['title'],
                        'source': article['source'],
                        'weight': article['score']
                    })
                    risk_score += article['score'] * 0.1
        
        # Sentiment-based risk
        sentiment_risk = {
            'very_negative': 3,
            'negative': 2,
            'neutral': 1,
            'positive': 0.5,
            'very_positive': 0.2
        }
        sentiment_risk_score = sentiment_risk.get(sentiment_analysis['overall_sentiment'], 1)
        
        # Combine risk factors
        total_risk_score = risk_score + sentiment_risk_score
        
        # Determine risk level
        if total_risk_score > 5:
            risk_level = 'high'
        elif total_risk_score > 2:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': round(total_risk_score, 2),
            'risk_factors': risk_factors[:10],
            'sentiment_risk_contribution': sentiment_risk_score,
            'risk_outlook': 'elevated' if sentiment_analysis['sentiment_trend'] == 'declining' else 'stable',
            'mitigation_strategies': self._get_risk_mitigation_strategies(risk_level)
        }
    
    def _get_risk_mitigation_strategies(self, risk_level: str) -> List[str]:
        """Get risk mitigation strategies based on risk level"""
        strategies = {
            'low': [
                'Maintain current position sizes',
                'Continue normal investment strategy',
                'Monitor for any sentiment changes'
            ],
            'medium': [
                'Reduce position sizes by 20-30%',
                'Focus on quality over quantity',
                'Increase cash reserves slightly',
                'Diversify across sectors'
            ],
            'high': [
                'Significantly reduce position sizes',
                'Focus on defensive sectors',
                'Increase cash allocation',
                'Avoid new positions until clarity',
                'Consider hedging strategies'
            ]
        }
        return strategies.get(risk_level, strategies['medium'])
    
    def _generate_market_insights(self, sentiment: Dict, impact: Dict, sector: Dict, timing: Dict, risk: Dict) -> List[MarketInsight]:
        """Generate key market insights"""
        insights = []
        
        # Sentiment insight
        if sentiment['confidence'] > 0.6:
            insights.append(MarketInsight(
                insight_type='sentiment',
                confidence=sentiment['confidence'],
                impact_level='high',
                description=f"Market sentiment is {sentiment['overall_sentiment']} with {sentiment['confidence']:.0%} confidence",
                actionable_recommendation=f"Consider {timing['timing_action'].replace('_', ' ')} positions",
                evidence=[f"Based on {sentiment['distribution'][sentiment['overall_sentiment']]} articles"],
                timestamp=datetime.now().isoformat()
            ))
        
        # Risk insight
        if risk['risk_level'] == 'high':
            insights.append(MarketInsight(
                insight_type='risk',
                confidence=0.8,
                impact_level='critical',
                description=f"Market risk is elevated at {risk['risk_level']} level",
                actionable_recommendation="Implement defensive positioning immediately",
                evidence=[f"Risk score: {risk['risk_score']}", f"Risk factors identified: {len(risk['risk_factors'])}"],
                timestamp=datetime.now().isoformat()
            ))
        
        # Sector insight
        if sector['sector_sentiment_leader'] != 'none':
            leading_sector = sector['sector_sentiment_leader']
            sector_sentiment = sector['sector_metrics'][leading_sector]['sentiment_score']
            insights.append(MarketInsight(
                insight_type='sector',
                confidence=0.7,
                impact_level='medium',
                description=f"{leading_sector.title()} sector showing strongest sentiment ({sector_sentiment:+.2f})",
                actionable_recommendation=f"Consider {leading_sector} sector allocation adjustments",
                evidence=[f"{sector['sector_metrics'][leading_sector]['mentions']} relevant articles"],
                timestamp=datetime.now().isoformat()
            ))
        
        # Timing insight
        if timing['confidence'] > 0.6:
            insights.append(MarketInsight(
                insight_type='timing',
                confidence=timing['confidence'],
                impact_level='high',
                description=f"Current market phase ({timing['current_phase'].replace('_', ' ')}) favors {timing['timing_action'].replace('_', ' ')} strategy",
                actionable_recommendation=f"Target optimal phases: {', '.join(timing['optimal_next_phases'])}",
                evidence=[f"Current phase: {timing['current_phase']}", f"Risk level: {timing['risk_level']}"],
                timestamp=datetime.now().isoformat()
            ))
        
        return insights
    
    def _insight_to_dict(self, insight: MarketInsight) -> Dict:
        """Convert insight object to dictionary"""
        return {
            'type': insight.insight_type,
            'confidence': insight.confidence,
            'impact_level': insight.impact_level,
            'description': insight.description,
            'actionable_recommendation': insight.actionable_recommendation,
            'evidence': insight.evidence,
            'timestamp': insight.timestamp
        }
    
    def _create_executive_summary(self, sentiment: Dict, impact: Dict, insights: List[MarketInsight]) -> Dict:
        """Create executive summary of market conditions"""
        
        # Overall market score (0-100)
        sentiment_score = {
            'very_positive': 85,
            'positive': 70,
            'neutral': 50,
            'negative': 30,
            'very_negative': 15
        }.get(sentiment['overall_sentiment'], 50)
        
        # Adjust for confidence
        adjusted_score = sentiment_score * sentiment['confidence']
        
        # Determine market grade
        if adjusted_score >= 75:
            market_grade = 'A'
            outlook = 'Bullish'
        elif adjusted_score >= 60:
            market_grade = 'B'
            outlook = 'Cautiously Optimistic'
        elif adjusted_score >= 45:
            market_grade = 'C'
            outlook = 'Neutral'
        elif adjusted_score >= 30:
            market_grade = 'D'
            outlook = 'Cautiously Pessimistic'
        else:
            market_grade = 'F'
            outlook = 'Bearish'
        
        return {
            'market_grade': market_grade,
            'market_outlook': outlook,
            'overall_score': round(adjusted_score, 1),
            'key_takeaway': self._generate_key_takeaway(sentiment, impact, insights),
            'primary_recommendation': self._get_primary_recommendation(insights),
            'confidence_level': sentiment['confidence'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_key_takeaway(self, sentiment: Dict, impact: Dict, insights: List[MarketInsight]) -> str:
        """Generate key takeaway message"""
        sentiment_text = f"Market sentiment is {sentiment['overall_sentiment']} ({sentiment['confidence']:.0%} confidence)"
        
        if impact['total_impact_score'] > 10:
            impact_text = "with significant market-moving news activity"
        elif impact['total_impact_score'] > 5:
            impact_text = "with moderate news flow"
        else:
            impact_text = "with limited high-impact news"
        
        critical_insights = [i for i in insights if i.impact_level == 'critical']
        if critical_insights:
            critical_text = f" Critical factors: {critical_insights[0].description.lower()}"
        else:
            critical_text = ""
        
        return f"{sentiment_text}, {impact_text}.{critical_text}"
    
    def _get_primary_recommendation(self, insights: List[MarketInsight]) -> str:
        """Get primary actionable recommendation"""
        timing_insights = [i for i in insights if i.insight_type == 'timing']
        risk_insights = [i for i in insights if i.insight_type == 'risk']
        
        if risk_insights and risk_insights[0].impact_level == 'critical':
            return risk_insights[0].actionable_recommendation
        elif timing_insights:
            return timing_insights[0].actionable_recommendation
        else:
            return "Continue monitoring market conditions and maintain current strategy"

if __name__ == "__main__":
    # Test the advanced analytics engine
    db_path = "/home/george/projects/clawblogs/news_system/data/rss_aggregator.db"
    analytics = AdvancedAnalyticsEngine(db_path)
    
    print("🔍 Running advanced market analytics...")
    analysis = analytics.get_comprehensive_analysis(hours_back=24)
    
    print(f"\n📊 EXECUTIVE SUMMARY:")
    summary = analysis['executive_summary']
    print(f"Market Grade: {summary['market_grade']} ({summary['market_outlook']})")
    print(f"Overall Score: {summary['overall_score']}/100")
    print(f"Key Takeaway: {summary['key_takeaway']}")
    print(f"Primary Recommendation: {summary['primary_recommendation']}")
    
    print(f"\n🎯 SENTIMENT ANALYSIS:")
    sentiment = analysis['sentiment_analysis']
    print(f"Overall Sentiment: {sentiment['overall_sentiment'].upper()}")
    print(f"Confidence: {sentiment['confidence']:.0%}")
    print(f"Trend: {sentiment['sentiment_trend']}")
    
    print(f"\n⚠️  RISK ASSESSMENT:")
    risk = analysis['risk_assessment']
    print(f"Risk Level: {risk['risk_level'].upper()}")
    print(f"Risk Score: {risk['risk_score']}")
    print(f"Outlook: {risk['risk_outlook']}")
    
    print(f"\n💡 KEY INSIGHTS ({len(analysis['key_insights'])}):")
    for i, insight in enumerate(analysis['key_insights'], 1):
        print(f"{i}. {insight['description']}")
        print(f"   Action: {insight['actionable_recommendation']}")
        print(f"   Confidence: {insight['confidence']:.0%}")
        print()
