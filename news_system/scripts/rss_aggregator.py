#!/usr/bin/env python3
"""
RSS Feed Aggregator for Financial and Tech News
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse
import urllib.request
import urllib.error
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Optional
import os
import sys
import xml.etree.ElementTree as ET

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RSSEntry:
    title: str
    link: str
    description: str
    published: str
    source: str
    category: str
    content_hash: str
    score: int = 0

class RSSAggregator:
    def __init__(self, db_path: str, config_path: str):
        self.db_path = db_path
        self.config_path = config_path
        self.feeds_config = self.load_feeds_config()
        self.init_database()
        
    def load_feeds_config(self) -> Dict:
        """Load RSS feed configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self.get_default_feeds()
    
    def get_default_feeds(self) -> Dict:
        """Default RSS feed configuration"""
        return {
            "financial": [
                {
                    "name": "Reuters Business",
                    "url": "https://feeds.reuters.com/reuters/businessNews",
                    "category": "financial",
                    "priority": "high",
                    "update_interval": 300  # 5 minutes
                },
                {
                    "name": "Bloomberg Markets",
                    "url": "https://feeds.bloomberg.com/markets/news.rss",
                    "category": "financial",
                    "priority": "high",
                    "update_interval": 300
                },
                {
                    "name": "Yahoo Finance",
                    "url": "https://feeds.finance.yahoo.com/rss/2.0/headline",
                    "category": "financial",
                    "priority": "medium",
                    "update_interval": 600
                },
                {
                    "name": "MarketWatch",
                    "url": "https://feeds.marketwatch.com/marketwatch/topstories/",
                    "category": "financial",
                    "priority": "medium",
                    "update_interval": 600
                },
                {
                    "name": "SEC Filings",
                    "url": "https://www.sec.gov/rss/news/press.xml",
                    "category": "financial",
                    "priority": "critical",
                    "update_interval": 1800
                }
            ],
            "technology": [
                {
                    "name": "TechCrunch",
                    "url": "https://techcrunch.com/feed/",
                    "category": "technology",
                    "priority": "high",
                    "update_interval": 600
                },
                {
                    "name": "VentureBeat",
                    "url": "https://venturebeat.com/feed/",
                    "category": "technology",
                    "priority": "high",
                    "update_interval": 600
                },
                {
                    "name": "MacRumors",
                    "url": "https://www.macrumors.com/macrumors.xml",
                    "category": "technology",
                    "priority": "medium",
                    "update_interval": 1200
                }
            ]
        }
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                description TEXT,
                published TEXT,
                source TEXT,
                category TEXT,
                content_hash TEXT UNIQUE,
                score INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE,
                keywords TEXT,
                sentiment REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feed_sources (
                name TEXT PRIMARY KEY,
                url TEXT UNIQUE NOT NULL,
                category TEXT,
                priority TEXT,
                last_updated TIMESTAMP,
                status TEXT DEFAULT 'active',
                error_count INTEGER DEFAULT 0,
                last_error TEXT
            )
        ''')
        
        # Insert feed sources
        for category, feeds in self.feeds_config.items():
            for feed in feeds:
                cursor.execute('''
                    INSERT OR IGNORE INTO feed_sources 
                    (name, url, category, priority) VALUES (?, ?, ?, ?)
                ''', (feed['name'], feed['url'], category, feed['priority']))
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def generate_content_hash(self, title: str, link: str) -> str:
        """Generate unique hash for content"""
        content = f"{title}{link}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def calculate_content_score(self, entry: RSSEntry) -> int:
        """Calculate relevance score for content"""
        score = 0
        
        # High-impact keywords
        high_impact = ['market crash', 'federal reserve', 'earnings', 'merger', 'acquisition', 
                      'ipo', 'bitcoin', 'inflation', 'recession', 'interest rate']
        
        # Medium-impact keywords  
        medium_impact = ['stock', 'investment', 'funding', 'startup', 'tech', 'ai',
                        'earnings call', 'guidance', 'revenue', 'profit']
        
        title_lower = entry.title.lower()
        desc_lower = entry.description.lower()
        combined_text = f"{title_lower} {desc_lower}"
        
        # Score based on keywords
        for keyword in high_impact:
            if keyword in combined_text:
                score += 10
        
        for keyword in medium_impact:
            if keyword in combined_text:
                score += 5
        
        # Priority boost
        if 'critical' in entry.source.lower():
            score += 15
        elif 'high' in entry.source.lower():
            score += 10
        
        # Recency boost (if published within last hour)
        try:
            pub_time = datetime.fromisoformat(entry.published.replace('Z', '+00:00'))
            if datetime.now(pub_time.tzinfo) - pub_time < timedelta(hours=1):
                score += 5
        except:
            pass
        
        return score
    
    def fetch_feed(self, feed_config: Dict) -> List[RSSEntry]:
        """Fetch and parse a single RSS feed"""
        try:
            logger.info(f"Fetching feed: {feed_config['name']}")
            
            # Create request with user agent
            req = urllib.request.Request(feed_config['url'])
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Fetch the feed
            with urllib.request.urlopen(req, timeout=30) as response:
                xml_content = response.read().decode('utf-8')
            
            entries = self.parse_rss_xml(xml_content, feed_config)
            
            # Update feed status
            self.update_feed_status(feed_config['name'], 'active', None)
            logger.info(f"Successfully fetched {len(entries)} entries from {feed_config['name']}")
            
            return entries
            
        except Exception as e:
            error_msg = f"Error fetching {feed_config['name']}: {str(e)}"
            logger.error(error_msg)
            self.update_feed_status(feed_config['name'], 'error', error_msg)
            return []
    
    def parse_rss_xml(self, xml_content: str, feed_config: Dict) -> List[RSSEntry]:
        """Parse RSS XML content using ElementTree"""
        entries = []
        try:
            root = ET.fromstring(xml_content)
            
            # Handle both RSS 2.0 and Atom feeds
            if root.tag.endswith('rss') or root.tag == 'rss':
                # RSS 2.0 format
                channel = root.find('channel')
                if channel is not None:
                    for item in channel.findall('item'):
                        entry = self.parse_rss_item(item, feed_config)
                        if entry:
                            entries.append(entry)
            elif root.tag.endswith('feed') or root.tag == 'feed':
                # Atom format
                for entry_elem in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                    entry = self.parse_atom_item(entry_elem, feed_config)
                    if entry:
                        entries.append(entry)
            
            return entries
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error for {feed_config['name']}: {e}")
            return []
    
    def parse_rss_item(self, item: ET.Element, feed_config: Dict) -> Optional[RSSEntry]:
        """Parse a single RSS item"""
        try:
            # Extract common fields
            title_elem = item.find('title')
            link_elem = item.find('link')
            desc_elem = item.find('description')
            pub_elem = item.find('pubDate')
            
            title = title_elem.text if title_elem is not None else 'No title'
            link = link_elem.text if link_elem is not None else ''
            description = desc_elem.text if desc_elem is not None else ''
            published = pub_elem.text if pub_elem is not None else 'Unknown'
            
            # Convert pubDate to ISO format if possible
            try:
                if published != 'Unknown':
                    # Simple date parsing for common formats
                    if ',' in published:  # RFC 2822 format
                        published = datetime.strptime(published.split(',')[1].strip(), '%d %b %Y %H:%M:%S %Z').isoformat()
            except:
                pass
            
            rss_entry = RSSEntry(
                title=title.strip(),
                link=link.strip(),
                description=description.strip()[:500],  # Limit description length
                published=published,
                source=feed_config['name'],
                category=feed_config['category'],
                content_hash=self.generate_content_hash(title, link)
            )
            
            rss_entry.score = self.calculate_content_score(rss_entry)
            return rss_entry
            
        except Exception as e:
            logger.error(f"Error parsing RSS item: {e}")
            return None
    
    def parse_atom_item(self, item: ET.Element, feed_config: Dict) -> Optional[RSSEntry]:
        """Parse a single Atom entry"""
        try:
            # Atom namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            title_elem = item.find('atom:title', ns)
            link_elem = item.find('atom:link[@rel="alternate"]', ns)
            summary_elem = item.find('atom:summary', ns)
            pub_elem = item.find('atom:published', ns)
            
            title = title_elem.text if title_elem is not None else 'No title'
            link = link_elem.get('href', '') if link_elem is not None else ''
            description = summary_elem.text if summary_elem is not None else ''
            published = pub_elem.text if pub_elem is not None else 'Unknown'
            
            rss_entry = RSSEntry(
                title=title.strip(),
                link=link.strip(),
                description=description.strip()[:500],
                published=published,
                source=feed_config['name'],
                category=feed_config['category'],
                content_hash=self.generate_content_hash(title, link)
            )
            
            rss_entry.score = self.calculate_content_score(rss_entry)
            return rss_entry
            
        except Exception as e:
            logger.error(f"Error parsing Atom item: {e}")
            return None
    
    def update_feed_status(self, feed_name: str, status: str, error: Optional[str]):
        """Update feed source status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        error_count = 1 if status == 'error' else 0
        
        cursor.execute('''
            UPDATE feed_sources 
            SET last_updated = CURRENT_TIMESTAMP, 
                status = ?, 
                error_count = error_count + ?,
                last_error = ?
            WHERE name = ?
        ''', (status, error_count, error, feed_name))
        
        conn.commit()
        conn.close()
    
    def save_entries(self, entries: List[RSSEntry]):
        """Save RSS entries to database"""
        if not entries:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for entry in entries:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO articles 
                    (title, link, description, published, source, category, content_hash, score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.title, entry.link, entry.description, 
                    entry.published, entry.source, entry.category, 
                    entry.content_hash, entry.score
                ))
                if cursor.rowcount > 0:
                    saved_count += 1
            except sqlite3.IntegrityError:
                # Article already exists
                continue
            except Exception as e:
                logger.error(f"Error saving article: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved {saved_count} new articles to database")
    
    def get_recent_articles(self, hours: int = 24, category: str = None, limit: int = 50) -> List[Dict]:
        """Retrieve recent articles from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT title, link, description, published, source, category, score
            FROM articles 
            WHERE created_at >= datetime('now', '-{} hours')
        '''.format(hours)
        
        if category:
            query += ' AND category = ?'
            cursor.execute(query, (category,))
        else:
            cursor.execute(query)
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'title': row[0],
                'link': row[1], 
                'description': row[2],
                'published': row[3],
                'source': row[4],
                'category': row[5],
                'score': row[6]
            })
        
        conn.close()
        
        # Sort by score (highest first) and limit
        articles.sort(key=lambda x: x['score'], reverse=True)
        return articles[:limit]
    
    def run_aggregation(self):
        """Main aggregation function"""
        logger.info("Starting RSS aggregation cycle")
        
        total_fetched = 0
        total_saved = 0
        
        for category, feeds in self.feeds_config.items():
            logger.info(f"Processing {category} feeds")
            
            for feed_config in feeds:
                entries = self.fetch_feed(feed_config)
                total_fetched += len(entries)
                
                if entries:
                    self.save_entries(entries)
                    total_saved += len(entries)
        
        logger.info(f"Aggregation complete: {total_fetched} fetched, {total_saved} saved")
        
        # Return summary for reporting
        return {
            'total_fetched': total_fetched,
            'total_saved': total_saved,
            'feeds_processed': sum(len(feeds) for feeds in self.feeds_config.values()),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Setup paths
    base_dir = "/home/george/projects/clawblogs/news_system"
    db_path = f"{base_dir}/data/rss_aggregator.db"
    config_path = f"{base_dir}/config/feeds_config.json"
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Initialize and run aggregator
    aggregator = RSSAggregator(db_path, config_path)
    result = aggregator.run_aggregation()
    
    print(json.dumps(result, indent=2))
