# News & Financial Monitoring System Documentation

## Overview
A comprehensive automated system for monitoring financial news, analyzing market sentiment, and generating intelligent investment timing alerts.

## System Architecture

### Components
1. **RSS Feed Aggregator** - Collects news from 14+ sources every 15 minutes
2. **Market Analysis Engine** - Analyzes sentiment and detects market signals every 30 minutes  
3. **Smart Alert System** - Generates actionable alerts every 10 minutes
4. **Automated Scheduling** - Cron jobs manage all automated processes

### Data Flow
```
RSS Sources → Feed Parser → Database → Analysis Engine → Alert Generator → User Notifications
```

## Feed Sources

### Financial News (Priority: High)
- Bloomberg Markets (Real-time market data)
- Reuters Business (Breaking financial news)
- CNBC Markets (Market analysis)
- MarketWatch (Market commentary)

### Technology News (Priority: Medium-High) 
- TechCrunch (Startups & tech trends)
- VentureBeat (Business technology)
- MacRumors (Apple ecosystem)
- The Verge (Consumer tech)
- Ars Technica (In-depth tech analysis)

## Market Analysis Features

### Sentiment Analysis
- **Bullish/Bearish Detection** - Analyzes language patterns in news
- **Confidence Scoring** - Rates reliability of sentiment indicators
- **Historical Tracking** - Maintains sentiment trends over time

### Signal Detection
- **Federal Reserve Activity** - Detects monetary policy news
- **Earnings Impact** - Identifies revenue/earnings announcements  
- **Volatility Indicators** - Spots market uncertainty patterns
- **Technical Breakouts** - Recognizes chart pattern signals

### Investment Timing
- **Optimal Windows** - Identifies best trading times
- **Risk Assessment** - Evaluates market conditions
- **Action Recommendations** - Buy/Sell/Hold/Avoid guidance

## Alert System

### Alert Types
1. **Timing Alerts** - Optimal investment opportunity notifications
2. **Critical News** - High-impact financial events requiring immediate attention
3. **Market Signals** - Technical and fundamental analysis signals
4. **Daily Summaries** - Comprehensive market overview (9 AM daily)

### Alert Prioritization
- **Critical** (Market crash, Fed decisions)
- **High** (Major earnings, significant signals)  
- **Medium** (General market conditions)
- **Low** (Informational updates)

### Rate Limiting
- Critical alerts: 5 minutes minimum
- Timing alerts: 60 minutes minimum
- News alerts: 30 minutes minimum
- Signal alerts: 2 hours minimum

## Automated Scheduling

### Cron Jobs (Active)
1. **news_rss_aggregation** - Every 15 minutes (900,000ms)
2. **news_market_analysis** - Every 30 minutes (1,800,000ms)  
3. **news_alert_system** - Every 10 minutes (600,000ms)
4. **news_daily_summary** - Daily at 9 AM UTC (cron: 0 9 * * *)

## Usage Commands

### Manual Operations
```bash
# Full system cycle
python3 coordinator.py full

# Individual components
python3 coordinator.py rss        # RSS aggregation only
python3 coordinator.py analysis   # Market analysis only  
python3 coordinator.py alerts     # Alert generation only

# System information
python3 coordinator.py status     # System health check
python3 coordinator.py summary    # Recent activity summary
```

## File Structure
```
/home/george/projects/clawblogs/news_system/
├── scripts/
│   ├── coordinator.py           # Main orchestrator
│   ├── rss_aggregator.py        # RSS feed parser
│   ├── market_analysis.py       # Analysis engine
│   └── alert_system.py          # Alert generator
├── config/
│   ├── feeds_config.json        # RSS source configuration
│   ├── alert_config.json        # Alert settings
│   └── system_architecture.md   # Technical documentation
├── data/
│   └── rss_aggregator.db        # SQLite database
└── logs/
    └── coordinator.log          # System logs
```

## Database Schema

### Articles Table
- `id` - Primary key
- `title` - Article headline
- `link` - Source URL
- `description` - Article summary
- `published` - Publication date
- `source` - News source name
- `category` - Financial/Tech/Business
- `content_hash` - Unique content identifier
- `score` - Relevance score (0-50)
- `created_at` - Database insertion timestamp

### Feed Sources Table
- `name` - Source identifier
- `url` - RSS feed URL
- `category` - Content category
- `priority` - Importance level
- `status` - Connection status
- `last_updated` - Last successful fetch
- `error_count` - Failure counter

## Performance Metrics

### Current Status (2026-02-04 05:26 UTC)
- **Articles Processed**: 147 in last cycle
- **Feeds Active**: 14 sources configured
- **System Response Time**: ~5 seconds per full cycle
- **Alert Accuracy**: 70%+ confidence threshold
- **Database Size**: ~143KB with 294+ articles

### Success Rates
- **RSS Feed Reliability**: ~70% (network dependent)
- **Analysis Accuracy**: Backtested patterns
- **Alert Relevance**: High-impact keywords prioritized

## Customization

### Adding New RSS Sources
Edit `/config/feeds_config.json`:
```json
{
  "name": "New Source Name",
  "url": "https://example.com/rss.xml",
  "category": "financial|technology|business",
  "priority": "high|medium|low",
  "update_interval": 300
}
```

### Modifying Alert Thresholds
Edit `/config/alert_config.json`:
- `min_news_score` - Minimum article score for alerts
- `min_confidence` - Confidence threshold for timing alerts
- `immediate_keywords` - Critical news triggers

## Troubleshooting

### Common Issues
1. **Network Failures** - Some RSS feeds may be temporarily unavailable
2. **Import Errors** - Clear Python cache: `rm -rf __pycache__`
3. **Database Locks** - SQLite may lock during concurrent access
4. **Log Analysis** - Check `/logs/coordinator.log` for details

### Health Checks
- Run `python3 coordinator.py status` for system overview
- Check database connectivity and component availability
- Verify cron job execution via logs

## Integration Notes

### WhatsApp Integration
- Alerts delivered to +15877102762
- Message format optimized for mobile viewing
- Rate limiting prevents notification spam

### API Endpoints (Future)
- REST API for programmatic access
- Webhook support for third-party integrations
- Real-time WebSocket connections

## Version History

### v1.0 (2026-02-04)
- Initial system deployment
- 14 RSS feeds configured
- Basic market analysis engine
- Alert generation system
- Automated cron scheduling

---

**System Status**: ✅ **OPERATIONAL**  
**Last Updated**: 2026-02-04 05:27 UTC  
**Next Maintenance**: As needed based on feed availability
