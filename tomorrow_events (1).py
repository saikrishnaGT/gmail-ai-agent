"""
Tomorrow Events Engine
─────────────────────────────────────────────
Scans ALL 9 category labels every morning.
Uses Claude AI to decide:
  1. Does this email have a deadline/event/meeting = tomorrow?
  2. Is this email urgent/mandatory enough to act on tomorrow?
If YES to either → copy to AI_Agent/Tomorrow_Events

Runs daily at 6:00 AM automatically.
At midnight, Tomorrow_Events is cleared first.

Author: SK (Sai Krishna Vaka)
"""

import imaplib
import email
import os
import time
import logging
import schedule
from email.header import decode_header
from datetime import datetime, timedelta
import anthropic

# ─────────────────────────────────────────────
# CREDENTIALS
# ─────────────────────────────────────────────
GMAIL_USER     = os.environ.get("GMAIL_USER", "your_email@gmail.com")
GMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "your_app_password")

TOMORROW_LABEL = "__Tomorrow_Events"

# All 9 category labels to scan
ALL_LABELS = [
    "_Banking_Transactions",
    "_Credit_Cards",
    "_Medical_Hospital",
    "_Job_Recruitment",
    "_Subscriptions",
    "_Shopping_Ecommerce",
    "_Government_Official",
    "_Travel",
    "_Immigration_Visa",
]

# Logging
logging.basicConfig(
    filename="tomorrow_events_log.txt",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def decode_str(s) -> str:
    if s is None:
        return ""
    decoded_parts = decode_header(s)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(encoding or "utf-8", errors="replace"))
            except Exception:
                result.append(part.decode("utf-8", errors="replace"))
        else:
            result.append(str(part))
    return " ".join(result)


def get_email_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                    break
                except Exception:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode("utf-8", errors="replace")
        except Exception:
            pass
    return body[:800]


# ─────────────────────────────────────────────
# AI DECISION ENGINE
# ─────────────────────────────────────────────

def ai_check_tomorrow(sender: str, subject: str, body: str, tomorrow_date: datetime) -> dict:
    """
    Asks Claude two questions:
    1. Is there a deadline/event/meeting on tomorrow's date?
    2. Is this email urgent/mandatory enough to action tomorrow?

    Returns:
        {
            "needs_tomorrow": True/False,
            "reason": "short explanation",
            "urgency": "HIGH / MEDIUM / LOW"
        }
    """
    client = anthropic.Anthropic()

    tomorrow_str   = tomorrow_date.strftime("%d %B %Y")   # e.g. "27 June 2026"
    tomorrow_day   = tomorrow_date.strftime("%A")          # e.g. "Saturday"
    tomorrow_short = tomorrow_date.strftime("%d/%m/%Y")    # e.g. "27/06/2026"
    tomorrow_us    = tomorrow_date.strftime("%B %d, %Y")   # e.g. "June 27, 2026"

    prompt = f"""You are an intelligent email urgency detector. Today is {datetime.now().strftime("%d %B %Y")} ({datetime.now().strftime("%A")}).
Tomorrow is {tomorrow_str} ({tomorrow_day}).

Analyze this email and answer TWO questions:

QUESTION 1 — DATE MATCH:
Does this email mention any deadline, due date, meeting, appointment, interview, payment, last date, expiry, or event that falls on tomorrow ({tomorrow_str} / {tomorrow_short} / {tomorrow_us} / {tomorrow_day})?
Also check for phrases like "tomorrow", "next day", "due tomorrow", "expires tomorrow", "last date tomorrow".

QUESTION 2 — URGENCY:
Is this email urgent or mandatory — meaning the person MUST take action tomorrow or face consequences?
Examples of urgent: payment due, visa deadline, interview, bill overdue, account suspension, application last date, meeting scheduled, subscription expiring, flight tomorrow, appointment tomorrow.
Examples of NOT urgent: promotional offers, newsletters, general updates, order delivered, welcome emails.

Respond in EXACTLY this JSON format, nothing else:
{{
  "needs_tomorrow": true or false,
  "reason": "one sentence explaining why",
  "urgency": "HIGH or MEDIUM or LOW"
}}

Email details:
From: {sender}
Subject: {subject}
Body: {body[:600]}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()

        # Clean up JSON
        import json, re
        raw = re.sub(r"```json|```", "", raw).strip()
        result = json.loads(raw)

        # Validate
        return {
            "needs_tomorrow": bool(result.get("needs_tomorrow", False)),
            "reason":  result.get("reason", ""),
            "urgency": result.get("urgency", "LOW")
        }

    except Exception as e:
        logging.warning(f"AI check failed for '{subject}': {e}")
        return {"needs_tomorrow": False, "reason": "AI error", "urgency": "LOW"}


# ─────────────────────────────────────────────
# CLEAR TOMORROW_EVENTS LABEL
# ─────────────────────────────────────────────

def clear_tomorrow_events(mail: imaplib.IMAP4_SSL):
    """Deletes all emails in Tomorrow_Events label at midnight."""
    print("\n🗑️  Clearing Tomorrow_Events label...")
    try:
        status, _ = mail.select(f'"{TOMORROW_LABEL}"')
        if status != "OK":
            print("   ℹ️  Tomorrow_Events label empty or not found — skipping clear")
            return

        # Find all emails in label
        status, data = mail.uid("SEARCH", None, "ALL")
        if status != "OK" or not data[0]:
            print("   ℹ️  No emails to clear")
            return

        uids = data[0].split()
        if not uids:
            print("   ℹ️  Label already empty")
            return

        # Mark all for deletion
        uid_str = b",".join(uids)
        mail.uid("STORE", uid_str, "+FLAGS", "\\Deleted")
        mail.expunge()
        print(f"   ✅ Cleared {len(uids)} emails from Tomorrow_Events")
        logging.info(f"Cleared {len(uids)} emails from Tomorrow_Events")

    except Exception as e:
        print(f"   ⚠️  Error clearing: {e}")
        logging.error(f"Clear failed: {e}")


# ─────────────────────────────────────────────
# ENSURE TOMORROW_EVENTS LABEL EXISTS
# ─────────────────────────────────────────────

def ensure_tomorrow_label(mail: imaplib.IMAP4_SSL):
    # Top-level label — no parent folder, sits above _AgentProcessed in Gmail sidebar
    mail.create(f'"{TOMORROW_LABEL}"')
    print(f"✅ Label ready: {TOMORROW_LABEL}")


# ─────────────────────────────────────────────
# SCAN ALL LABELS FOR TOMORROW EVENTS
# ─────────────────────────────────────────────

def scan_all_labels_for_tomorrow(mail: imaplib.IMAP4_SSL, tomorrow_date: datetime):
    """
    Goes through every category label.
    For each email, asks AI: is this needed tomorrow?
    If yes → copies to Tomorrow_Events.
    """
    tomorrow_str = tomorrow_date.strftime("%d %B %Y")
    print(f"\n🔍 Scanning all labels for tomorrow ({tomorrow_str}) events...")
    print("="*60)

    total_added   = 0
    total_scanned = 0
    results       = []

    for label in ALL_LABELS:
        label_name = label.split("/")[-1].replace("_", " ")
        print(f"\n📂 Scanning: {label_name}")

        try:
            status, _ = mail.select(f'"{label}"', readonly=True)
            if status != "OK":
                print(f"   ⚠️  Could not open label")
                continue

            # Fetch all emails in this label (last 30 days to keep it manageable)
            status, data = mail.uid("SEARCH", None, "ALL")
            if status != "OK" or not data[0]:
                print(f"   ℹ️  No emails found")
                continue

            uids = data[0].split()
            print(f"   Found {len(uids)} emails to check")

            for uid in uids[-100:]:  # Check latest 100 per label
                try:
                    status, msg_data = mail.uid("FETCH", uid, "(RFC822)")
                    if status != "OK":
                        continue

                    raw = msg_data[0][1]
                    msg = email.message_from_bytes(raw)

                    sender  = decode_str(msg.get("From", ""))
                    subject = decode_str(msg.get("Subject", ""))
                    body    = get_email_body(msg)
                    total_scanned += 1

                    # Ask AI
                    decision = ai_check_tomorrow(sender, subject, body, tomorrow_date)

                    if decision["needs_tomorrow"]:
                        # Copy to Tomorrow_Events
                        # Switch back to label first (readonly=False to copy from)
                        mail.select(f'"{label}"', readonly=False)
                        copy_result = mail.uid("COPY", uid, f'"{TOMORROW_LABEL}"')

                        if copy_result[0] == "OK":
                            total_added += 1
                            urgency_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(decision["urgency"], "⚪")
                            print(f"   {urgency_icon} ADDED → [{decision['urgency']}] {subject[:50]}")
                            print(f"      Reason: {decision['reason']}")
                            results.append({
                                "label": label_name,
                                "subject": subject,
                                "urgency": decision["urgency"],
                                "reason": decision["reason"]
                            })
                        else:
                            print(f"   ❌ Copy failed for: {subject[:40]}")

                        # Re-select as readonly for next iterations
                        mail.select(f'"{label}"', readonly=True)

                    # Small delay to avoid API rate limits
                    time.sleep(0.3)

                except Exception as e:
                    print(f"   ⚠️  Error on email: {e}")
                    continue

        except Exception as e:
            print(f"   ⚠️  Error scanning {label}: {e}")
            continue

    # Final summary
    print("\n" + "="*60)
    print(f"📅 TOMORROW EVENTS SUMMARY — {tomorrow_str}")
    print("="*60)
    print(f"   Emails scanned : {total_scanned}")
    print(f"   Added to label : {total_added}")

    if results:
        print("\n   🔴 HIGH PRIORITY:")
        for r in results:
            if r["urgency"] == "HIGH":
                print(f"      • [{r['label']}] {r['subject'][:55]}")
                print(f"        → {r['reason']}")

        print("\n   🟡 MEDIUM PRIORITY:")
        for r in results:
            if r["urgency"] == "MEDIUM":
                print(f"      • [{r['label']}] {r['subject'][:55]}")

    print(f"\n   ✅ Done at {datetime.now().strftime('%H:%M:%S')}")
    logging.info(f"Tomorrow scan done. Scanned: {total_scanned}, Added: {total_added}")
    return results


# ─────────────────────────────────────────────
# DAILY MIDNIGHT CLEAR JOB
# ─────────────────────────────────────────────

def midnight_clear_job():
    """Runs at midnight — clears Tomorrow_Events."""
    print(f"\n🌙 Midnight clear job starting — {datetime.now()}")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        ensure_tomorrow_label(mail)
        clear_tomorrow_events(mail)
        mail.logout()
        print("✅ Midnight clear done")
    except Exception as e:
        print(f"❌ Midnight clear failed: {e}")
        logging.error(f"Midnight clear failed: {e}")


# ─────────────────────────────────────────────
# DAILY MORNING SCAN JOB
# ─────────────────────────────────────────────

def morning_scan_job():
    """Runs at 6:00 AM — scans all labels and fills Tomorrow_Events."""
    tomorrow = datetime.now() + timedelta(days=1)
    print(f"\n☀️  Morning scan job starting — {datetime.now()}")
    print(f"    Looking for events on: {tomorrow.strftime('%d %B %Y')}")

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        ensure_tomorrow_label(mail)
        results = scan_all_labels_for_tomorrow(mail, tomorrow)
        mail.logout()
    except Exception as e:
        print(f"❌ Morning scan failed: {e}")
        logging.error(f"Morning scan failed: {e}")


# ─────────────────────────────────────────────
# SCHEDULER
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Tomorrow Events Engine Started")
    print("   🌙 Clears label at midnight (00:01)")
    print("   ☀️  Scans all labels at 6:00 AM")
    print("   Press Ctrl+C to stop\n")

    # Schedule jobs
    schedule.every().day.at("00:01").do(midnight_clear_job)
    schedule.every().day.at("06:00").do(morning_scan_job)

    # Run morning scan immediately on startup (so you see results right away)
    morning_scan_job()

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(30)
