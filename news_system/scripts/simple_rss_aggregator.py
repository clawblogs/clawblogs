#!/usr/bin/env python3
"""
Simplified Financial RSS Feed Aggregator
Uses only Python standard library - no external dependencies
"""

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
import os
import re
from typing import List, Dict, Optional

class SimplifiedFinancialAggregator:
    def __init__(self, data_dir: str = "/home/george/projects/clawblogs/news_system/data"):
        self.data_dir = data_dir
        self.feeds = {
            'reuters_business': 'https://feeds.reuters.com/reuters/businessNews',
            'yahoo_finance': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            # Note: Some feeds may be limited due to CORS/anti-bot measures
        }
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def fetch_url_content(self, url: str) -> Optional[str]:
        """Fetch content from URL using standard library"""
        try:
            # Create request with headers
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            req.add_header('Accept', 'application/rss+xml, application/xml, text/xml')
            
            # Fetch content
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    return response.read().decode('utf-8', errors='ignore')
                else:
                    self.logger.warning(f"HTTP {response.status} for {url}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def parse_rss_xml(self, xml_content: str) -> List[Dict]:
        """Parse RSS XML content using ElementTree"""
        try:
            root = ET.fromstring(xml_content)
            articles = []
            
            # Handle different RSS formats
            if root.tag.endswith('rss') or 'rss' in root.tag:
                # Standard RSS format
                for item in root.findall('.//item'):
                    article = self.extract_article_data(item, 'rss')
                    if article:
                        articles.append(article)
            elif root.tag.endswith('feed') or 'feed' in root.tag:
                # Atom feed format
                for entry in root.findall('.//entry'):
                    article = self.extract_article_data(entry, 'atom')
                    if article:
                        articles.append(article)
            
            return articles[:20]  # Limit to 20 articles
            
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing RSS content: {str(e)}")
            return []
    
    def extract_article_data(self, item_elem, feed_format: str) -> Optional[Dict]:
        """Extract article data from RSS/Atom item"""
        try:
            article = {}
            
            if feed_format == 'rss':
                # RSS format
                title_elem = item_elem.find('title')
                link_elem = item_elem.find('link')
                desc_elem = item_elem.find('description')
                pub_elem = item_elem.find('pubDate')
                guid_elem = item_elem.find('guid')
                
                article['title'] = self.clean_text(title_elem.text if title_elem is not None else '')
                article['link'] = link_elem.text if link_elem is not None else ''
                article['summary'] = self.clean_text(desc_elem.text if desc_elem is not None else '')
                article['published'] = pub_elem.text if pub_elem is not None else ''
                article['id'] = guid_elem.text if guid_elem is not None else article.get('link', '')
                
            elif feed_format == 'atom':
                # Atom format
                title_elem = item_elem.find('title')
                link_elem = item_elem.find('.//link[@rel="alternate"]')
                summary_elem = item_elem.find('summary')
                pub_elem = item_elem.find('published')
                id_elem = item_elem.find('id')
                
                article['title'] = self.clean_text(title_elem.text if title_elem is not None else '')
                article['link'] = link_elem.get('href') if link_elem is not None else ''
                article['summary'] = self.clean_text(summary_elem.text if summary_elem is not None else '')
                article['published'] = pub_elem.text if pub_elem is not None else ''
                article['id'] = id_elem.text if id_elem is not None else article.get('link', '')
            
            # Add metadata
            article['fetched_at'] = datetime.now().isoformat()
            article['keywords'] = self.extract_market_keywords(article.get('title', '') + ' ' + article.get('summary', ''))
            article['impact_score'] = self.calculate_impact_score(article)
            
            return article if article.get('title') else None
            
        except Exception as e:
            self.logger.error(f"Error extracting article data: {str(e)}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove special characters
        text = re.sub(r'[^\w\s\-\.\,\:\;\!\?]', '', text)
        
        return text
    
    def extract_market_keywords(self, text: str) -> List[str]:
        """Extract market-related keywords"""
        keywords = [
            'stock', 'market', 'trading', 'investment', 'earnings', 'revenue',
            'profit', 'loss', 'IPO', 'merger', 'acquisition', 'dividend',
            'volatility', 'rally', 'crash', 'bear', 'bull', 'index', 'ETF',
            'Federal Reserve', 'Fed', 'interest rate', 'inflation', 'GDP',
            'unemployment', 'quarterly', 'analyst', 'upgrade', 'downgrade'
        ]
        
        text_lower = text.lower()
        found_keywords = [keyword for keyword in keywords if keyword.lower() in text_lower]
        return found_keywords
    
    def calculate_impact_score(self, article: Dict) -> float:
        """Calculate potential market impact score"""
        score = 0.0
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        combined_text = f"{title} {summary}"
        
        # High impact keywords
        high_impact = ['federal reserve', 'fed', 'interest rate', 'inflation', 'gdp', 'crisis']
        medium_impact = ['earnings', 'merger', 'acquisition', 'ipo', 'dividend']
        low_impact = ['analyst', 'upgrade', 'downgrade', 'rating']
        
        for keyword in high_impact:
            if keyword in combined_text:
                score += 3.0
                
        for keyword in medium_impact:
            if keyword in combined_text:
                score += 1.5
                
        for keyword in low_impact:
            if keyword in combined_text:
                score += 0.5
        
        # Check for ticker symbols
        ticker_pattern = r'\b[A-Z]{1,5}\b'
        tickers = re.findall(ticker_pattern, combined_text)
        score += len(tickers) * 0.2
        
        return min(score, 5.0)
    
    def aggregate_feeds(self) -> Dict:
        """Fetch and aggregate all RSS feeds"""
        all_articles = []
        feed_summary = {}
        
        for feed_name, url in self.feeds.items():
            try:
                self.logger.info(f"Fetching {feed_name} from {url}")
                
                xml_content = self.fetch_url_content(url)
                if xml_content:
                    articles = self.parse_rss_xml(xml_content)
                    all_articles.extend(articles)
                    feed_summary[feed_name] = {
                        'url': url,
                        'article_count': len(articles),
                        'success': len(articles) > 0
                    }
                    self.logger.info(f"Successfully fetched {len(articles)} articles from {feed_name}")
                else:
                    feed_summary[feed_name] = {
                        'url': url,
                        'article_count': 0,
                        'success': False
                    }
                
                # Be respectful to servers
                import time
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error processing {feed_name}: {str(e)}")
                feed_summary[feed_name] = {
                    'url': url,
                    'article_count': 0,
                    'success': False,
                    'error': str(e)
                }
        
        # Sort by impact score
        all_articles.sort(key=lambda x: x.get('impact_score', 0), reverse=True)
        
        # Create summary report
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_articles': len(all_articles),
            'feed_summary': feed_summary,
            'high_impact_articles': [a for a in all_articles if a.get('impact_score', 0) >= 2.0],
            'recent_articles': all_articles[:10],
            'keyword_frequency': self._calculate_keyword_frequency(all_articles)
        }
        
        return {
            'report': report,
            'all_articles': all_articles
        }
    
    def _calculate_keyword_frequency(self, articles: List[Dict]) -> Dict[str, int]:
        """Calculate keyword frequency"""
        keyword_count = {}
        for article in articles:
            for keyword in article.get('keywords', []):
                keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
        return dict(sorted(keyword_count.items(), key=lambda x: x[1], reverse=True))
    
    def save_data(self, data: Dict, filename_prefix: str = "financial_news") -> str:
        """Save aggregated data to JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save full data
        full_filename = f"{self.data_dir}/{filename_prefix}_{timestamp}.json"
        with open(full_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save summary for quick access
        summary_filename = f"{self.data_dir}/{filename_prefix}_latest.json"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump(data['report'], f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Data saved to {full_filename}")
        return full_filename

def main():
    """Main execution function"""
    aggregator = SimplifiedFinancialAggregator()
    
    print("🔄 Starting Simplified Financial RSS Feed Aggregation...")
    data = aggregator.aggregate_feeds()
    
    if data['report']['total_articles'] > 0:
        filename = aggregator.save_data(data)
        print(f"✅ Successfully aggregated {data['report']['total_articles']} articles")
        print(f"📁 Data saved to: {filename}")
        
        # Print summary
        print(f"\n📊 Summary:")
        for feed_name, summary in data['report']['feed_summary'].items():
            status = "✅" if summary['success'] else "❌"
            print(f"  {status} {feed_name}: {summary['article_count']} articles")
            
        print(f"\n🔥 High Impact Articles: {len(data['report']['high_impact_articles'])}")
        if data['report']['keyword_frequency']:
            print(f"🔑 Top Keywords: {list(data['report']['keyword_frequency'].keys())[:5]}")
        
        # Show top articles
        print(f"\n📰 Top Articles by Impact:")
        for i, article in enumerate(data['report']['recent_articles'][:3], 1):
            print(f"{i}. {article.get('title', 'N/A')[:80]}... (Score: {article.get('impact_score', 0):.1f})")
        
    else:
        print("❌ No articles fetched. This may be due to:")
        print("  • Network connectivity issues")
        print("  • RSS feeds temporarily unavailable")
        print("  • CORS/anti-bot restrictions")
        print("  • XML parsing issues")

if __name__ == "__main__":
    main()