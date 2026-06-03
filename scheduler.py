"""
Email Agent Scheduler
Runs the email classification agent every hour automatically.
Run this once: python scheduler.py
"""

import schedule
import time
import logging
from datetime import datetime
from email_agent import process_inbox

# ── Logging setup ──────────────────────────────────
logging.basicConfig(
    filename="agent_log.txt",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def run_agent():
    print(f"\n🔄 Scheduled run at {datetime.now().strftime('%H:%M:%S')}")
    logging.info("Agent run started")
    try:
        stats = process_inbox(max_emails=100, use_ai_fallback=True)
        logging.info(f"Agent run completed. Stats: {stats}")
    except Exception as e:
        logging.error(f"Agent failed: {e}")
        print(f"❌ Error: {e}")

# ── Schedule: every 1 hour ─────────────────────────
schedule.every(1).hours.do(run_agent)

# ── Also run immediately on start ─────────────────
print("🚀 Email Agent Scheduler Started")
print("📅 Will run every 1 hour automatically")
print("   Press Ctrl+C to stop\n")
run_agent()

while True:
    schedule.run_pending()
    time.sleep(60)
