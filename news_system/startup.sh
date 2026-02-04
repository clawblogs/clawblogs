#!/bin/bash
# News System Startup Script

echo "🚀 Starting News & Financial Monitoring System"
echo "=================================================="

# Set up environment
BASE_DIR="/home/george/projects/clawblogs/news_system"
SCRIPTS_DIR="$BASE_DIR/scripts"

# Ensure directories exist
mkdir -p "$BASE_DIR"/{data,logs,config}

# Set Python path
export PYTHONPATH="$SCRIPTS_DIR:$PYTHONPATH"

# Run initial system check
echo "📊 Running system status check..."
cd "$SCRIPTS_DIR"
python3 coordinator.py status

echo ""
echo "🔄 Running initial data aggregation..."
python3 coordinator.py full

echo ""
echo "✅ News System Startup Complete!"
echo ""
echo "📈 System Components:"
echo "  • RSS Feed Aggregation: Active"
echo "  • Market Analysis Engine: Active" 
echo "  • Smart Alert System: Active"
echo ""
echo "🎯 Next Steps:"
echo "  • System will run automated cycles via cron jobs"
echo "  • Check logs in: $BASE_DIR/logs/"
echo "  • Database location: $BASE_DIR/data/rss_aggregator.db"
echo ""
echo "📋 Manual Commands:"
echo "  • Full cycle: python3 coordinator.py full"
echo "  • RSS only: python3 coordinator.py rss"
echo "  • Analysis only: python3 coordinator.py analysis"
echo "  • Alerts only: python3 coordinator.py alerts"
echo "  • System status: python3 coordinator.py status"
echo ""
