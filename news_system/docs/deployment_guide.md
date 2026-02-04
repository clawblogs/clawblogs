# News & Financial Monitoring System - Deployment Guide

## Quick Start

### 1. Run Complete System Cycle
```bash
cd /home/george/projects/clawblogs/news_system/scripts
python3 coordinator.py full
```

### 2. Check System Health
```bash
python3 master_controller.py health
```

### 3. Generate System Report
```bash
python3 master_controller.py report
```

## Individual Component Testing

### RSS Aggregation Only
```bash
python3 rss_aggregator.py
```

### Market Analysis Only
```bash
python3 market_analysis.py
```

### Alert System Only
```bash
python3 alert_system.py
```

### Quick Feed Test
```bash
python3 simple_rss_aggregator.py
```

## Automated Operation

### Cron Setup (Recommended)
Add to crontab for automated operation:
```bash
# Every 15 minutes - Full cycle
*/15 * * * * cd /home/george/projects/clawblogs/news_system/scripts && python3 coordinator.py full

# Every hour - Health check
0 * * * * cd /home/george/projects/clawblogs/news_system/scripts && python3 master_controller.py health

# Daily report at 9 AM
0 9 * * * cd /home/george/projects/clawblogs/news_system/scripts && python3 master_controller.py report
```

## System Architecture

```
News System Architecture:
├── RSS Aggregation (rss_aggregator.py)
│   ├── 14 configured feeds
│   ├── SQLite database storage
│   └── Content scoring & deduplication
│
├── Market Analysis (market_analysis.py)
│   ├── Sentiment analysis
│   ├── Signal detection
│   └── Investment timing recommendations
│
├── Smart Alerts (alert_system.py)
│   ├── Multiple alert types
│   ├── Rate limiting
│   └── Priority-based delivery
│
└── System Coordination (coordinator.py)
    ├── Process orchestration
    ├── Health monitoring
    └── Comprehensive reporting
```

## Data Storage

- **Database**: `/home/george/projects/clawblogs/news_system/data/rss_aggregator.db`
- **Configuration**: `/home/george/projects/clawblogs/news_system/config/`
- **Logs**: `/home/george/projects/clawblogs/news_system/logs/`
- **Generated Reports**: Automatically saved with timestamps

## Configuration Files

### feeds_config.json - RSS Feed Sources
- Financial: Reuters, Bloomberg, Yahoo Finance, MarketWatch, SEC, CNBC, FT
- Technology: TechCrunch, VentureBeat, MacRumors, The Verge, Ars Technica
- Business: Harvard Business Review, McKinsey Insights

### alert_config.json - Alert System Settings
- Thresholds and confidence levels
- Keyword triggers for immediate alerts
- Delivery methods (console, email, webhook)
- Rate limiting by alert type

## System Health Monitoring

### Health Check Components:
- [x] RSS Aggregator Status
- [x] Database Connectivity  
- [x] Feed Source Availability
- [x] Alert System Configuration
- [x] Market Analysis Engine
- [x] Component Integration

### Common Issues:
1. **Network/DNS Issues**: Some feeds may be temporarily unavailable
2. **Database Locks**: Usually resolve automatically
3. **Memory Usage**: Monitor for large article volumes

## Output Interpretation

### Market Analysis Results:
- **Sentiment**: bullish/bearish/neutral with confidence %
- **Action**: buy/sell/hold/avoid
- **Risk Level**: low/medium/high
- **Optimal Windows**: Best times for trading
- **Signals**: Fed decisions, earnings, volatility spikes

### Alert Types:
- **Timing**: Optimal investment opportunities
- **News**: High-impact market news
- **Signal**: Technical and fundamental indicators
- **Summary**: Daily market overview

## Performance Metrics

- **Processing Speed**: ~5 seconds per full cycle
- **Article Throughput**: 100-150 articles per cycle
- **Feed Success Rate**: ~70% (some feeds have access restrictions)
- **Database Size**: Grows by ~50-100 articles per day
- **Memory Usage**: < 100MB typical

## Troubleshooting

### No Articles Fetched:
1. Check internet connectivity
2. Verify DNS resolution
3. Review feed URLs in configuration

### Database Errors:
1. Check file permissions
2. Verify disk space
3. Restart system components

### Alert System Not Working:
1. Verify configuration files exist
2. Check database connectivity
3. Review log files for errors

## Next Development Phases

1. **Enhanced Web Interface** - Expand Flask application
2. **Real-Time Streaming** - WebSocket implementation
3. **Advanced Analytics** - ML-based prediction models
4. **Mobile Integration** - Push notifications
5. **API Development** - RESTful endpoints for external access