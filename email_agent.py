"""
AI Email Classification Agent
Classifies emails into categories using keyword matching + AI fallback
Author: SK (Sai Krishna Vaka)
"""

import imaplib
import email
import json
import time
import re
import os
from email.header import decode_header
from datetime import datetime
import anthropic

# ─────────────────────────────────────────────
# GMAIL CREDENTIALS (set via environment vars)
# ─────────────────────────────────────────────
GMAIL_USER     = os.environ.get("GMAIL_USER", "your_email@gmail.com")
GMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "your_app_password")  # Gmail App Password

# ─────────────────────────────────────────────
# CATEGORY DEFINITIONS WITH KEYWORD RULES
# ─────────────────────────────────────────────

CATEGORIES = {

    # ── BANKING & TRANSACTIONS ──────────────────────────────────────────────
    "Banking_Transactions": {
        "label": "📂 Banking & Transactions",
        "gmail_label": "_Banking_Transactions",
        "senders": [
            # Public Sector Banks
            "sbi", "statebank", "onlinesbi",
            "bankofbaroda", "bob",
            "pnb", "punjabnationalbank",
            "bankofmaha", "bankofmaharashtra",
            "canarabank", "canara",
            "unionbankofindia", "unionbank",
            "indianbank", "indian-bank",
            "centralbankofindia", "centralbankofin",
            "bankofindia", "boi",
            "ucoindia", "ucobank",
            "syndicatebank",
            "allahabadbank",
            "andhrbank", "andhrabank",
            "vijayabank",
            "denabank",
            "corporationbank",
            # Private Sector Banks
            "hdfcbank", "hdfc",
            "icicibank", "icici",
            "axisbank", "axis",
            "kotakbank", "kotak",
            "yesbank", "yes-bank",
            "indusind", "indusindbank",
            "idfcfirstbank", "idfc",
            "federalbank", "federal-bank",
            "rblbank", "rbl",
            "bandhanbank", "bandhan",
            "southindianbank", "sib",
            "karnatakabank",
            "kvb", "karurvsyabank",
            "cityunionbank", "cub",
            "lakshmivillas", "lvb",
            "tamilnadbank", "tnb",
            "dcbbank", "dcb",
            "nainitalbank",
            "jkbank",
            # Small Finance & Payments Banks
            "aubank", "au-sf-bank",
            "equitasbank", "equitas",
            "ujjivanbank", "ujjivan",
            "suryodaybank",
            "utkarshbank",
            "fincarefinance",
            "paytmbank", "paytm",
            "airtelbank", "airtel",
            "finobank",
            "jiobank", "jiopayments",
            # NBFCs & Fintech
            "bajajfinserv", "bajajfinance",
            "hdfcsec", "hdfcsecurities",
            "icicidirect",
            "sbicards",
            "axissecurities",
            "muthootfin", "muthoot",
            "shriramfinance",
            "mahindrafinance",
            "tatafinance", "tatacapital",
            "lntfinance",
            "cholafin", "cholamandalam",
            # Payment Networks
            "nsdl", "cdsl",
            "npci", "upi",
            "razorpay",
            "cashfree",
            "billdesk",
            "payu",
            "ccavenue",
            "instamojo",
            "phonepe",
            "googlepay", "gpay",
            "amazonpay",
        ],
        "keywords": [
            "transaction", "credited", "debited", "debit", "credit",
            "account balance", "balance is", "withdrawn", "deposit",
            "neft", "rtgs", "imps", "upi", "transfer",
            "statement", "mini statement", "account statement",
            "atm withdrawal", "pos transaction", "online transaction",
            "swift", "wire transfer", "fd matured", "emi due",
            "loan disbursed", "loan repayment", "cheque",
            "passbook", "net banking", "mobile banking",
            "otp for", "bank alert", "transaction alert",
            "insufficient funds", "available balance",
            "your account", "dear customer",
        ],
    },

    # ── CREDIT CARDS ────────────────────────────────────────────────────────
    "Credit_Cards": {
        "label": "💳 Credit Cards",
        "gmail_label": "_Credit_Cards",
        "senders": [
            "hdfcbank", "sbicard", "sbicards",
            "icicibank", "axisbank", "kotakbank",
            "citibank", "citi",
            "amexindia", "americanexpress",
            "indusind", "yesbank",
            "rblbank", "idfcfirstbank",
            "standardchartered", "sc",
            "hsbc",
            "bajajfinserv",
            "onecard",
            "sliceit", "slice",
            "kreditbee",
            "lazypay",
            "simpl",
            "uni.club", "unicards",
        ],
        "keywords": [
            "credit card", "card statement", "outstanding amount",
            "minimum due", "total due", "payment due",
            "card bill", "card ending", "reward points",
            "cashback", "card limit", "available credit",
            "emi", "equated monthly", "card transaction",
            "card blocked", "card activated", "card upgrade",
            "spend summary", "billing cycle", "auto debit",
            "card application", "card approved",
        ],
    },

    # ── MEDICAL / HOSPITAL ───────────────────────────────────────────────────
    "Medical_Hospital": {
        "label": "🏥 Medical & Hospital",
        "gmail_label": "_Medical_Hospital",
        "senders": [
            # Major Hospital Chains
            "apollohospitals", "apollo",
            "fortishealthcare", "fortis",
            "manipalhospitals", "manipal",
            "maxhealthcare", "max",
            "narayanahealth", "narayana",
            "medanta",
            "aster", "asterhospitals",
            "nhh", "narayanahealth",
            "columbia-asia",
            "gleneagles",
            "artemishospitals",
            "bljc", "bljhospital",
            "jaslok",
            "kokilaben",
            "lilavati",
            "hinduja",
            "seventhills",
            "cloudninecare", "cloudnine",
            "motherhoodchd",
            # Pharmacy
            "netmeds", "1mg", "tata1mg",
            "pharmeasy", "medplusmart",
            "apollopharmacy", "apollolife",
            "healthkart",
            "mfine",
            "practo",
            "lybrate",
            "portea",
            # Insurance
            "starhealth",
            "niacl", "newindia",
            "niaclao",
            "carehealth",
            "bajajallianz",
            "hdfcergo",
            "icicilombard",
            "godigit",
            "acko",
            "reliancehealth",
        ],
        "keywords": [
            "appointment", "doctor", "hospital", "clinic",
            "prescription", "medicine", "tablet", "dosage",
            "blood test", "lab report", "pathology", "radiology",
            "health insurance", "mediclaim", "claim approved",
            "discharge summary", "patient", "diagnosis",
            "health checkup", "vaccination", "vaccine",
            "consultation", "opd", "ipd", "emergency",
            "surgery", "operation", "treatment",
            "pharmacy", "medical store", "health report",
        ],
    },

    # ── JOB & RECRUITMENT ───────────────────────────────────────────────────
    "Job_Recruitment": {
        "label": "💼 Job & Recruitment",
        "gmail_label": "_Job_Recruitment",
        "senders": [
            "naukri", "info.naukri",
            "linkedin", "jobalerts.linkedin",
            "indeed", "indeedemail",
            "shine", "shinelearning",
            "monster", "monsterindia",
            "foundit", "timesjobs",
            "hirist",
            "instahyre",
            "iimjobs",
            "cutshort",
            "apna",
            "freshteam",
            "greenhouse",
            "lever",
            "workday",
            "taleo",
            "smartrecruiters",
            "bamboohr",
            "keka",
            "darwinbox",
            "zohorecruit",
            "tcs", "tata consultancy",
            "infosys",
            "wipro",
            "hcltech",
            "accenture",
            "cognizant",
            "capgemini",
            "ibm",
            "fractal",
            "mu sigma", "musigma",
            "tiger analytics",
            "deloitte",
            "ey", "ernst",
            "pwc",
            "kpmg",
        ],
        "keywords": [
            "job alert", "new job", "job opening", "vacancy",
            "hiring", "recruitment", "recruiter",
            "interview", "interview scheduled", "interview invite",
            "application received", "application status",
            "shortlisted", "selected", "rejected",
            "offer letter", "joining date", "onboarding",
            "resume", "profile viewed", "profile matches",
            "salary", "ctc", "package",
            "jd", "job description", "apply now",
            "career opportunity", "we are hiring",
            "your application", "position of",
        ],
    },

    # ── SUBSCRIPTIONS ────────────────────────────────────────────────────────
    "Subscriptions": {
        "label": "📺 Subscriptions",
        "gmail_label": "_Subscriptions",
        "senders": [
            # Streaming
            "netflix", "hotstar", "primevideo", "amazon",
            "sonyliv", "zee5", "voot",
            "jiocinema", "jio",
            "mxplayer",
            "spotify", "gaana", "jiosaavn",
            "wynk",
            # Software & Cloud
            "microsoft", "office365",
            "google", "googleplay",
            "apple", "icloud",
            "adobe",
            "canva",
            "notion",
            "slack",
            "zoom",
            "dropbox",
            "github",
            "chatgpt", "openai",
            "anthropic",
            # News & Learning
            "medium",
            "substack",
            "coursera",
            "udemy",
            "edx",
            "linkedin learning",
            "skillshare",
        ],
        "keywords": [
            "subscription", "subscribed", "renew", "renewal",
            "plan expires", "auto-renew", "auto renewal",
            "your plan", "premium plan", "billing",
            "invoice", "receipt", "payment successful",
            "monthly plan", "annual plan", "upgrade plan",
            "cancel subscription", "free trial",
            "your membership", "membership renewed",
        ],
    },

    # ── SHOPPING / E-COMMERCE ────────────────────────────────────────────────
    "Shopping_Ecommerce": {
        "label": "🛍️ Shopping & E-Commerce",
        "gmail_label": "_Shopping_Ecommerce",
        "senders": [
            "amazon", "flipkart", "myntra",
            "snapdeal", "ajio", "nykaa",
            "meesho", "glowroad",
            "bigbasket", "blinkit", "zepto",
            "swiggy", "zomato",
            "dunzo", "jiomart",
            "tatacliq", "croma",
            "reliance digital",
            "vijay sales",
            "shopclues",
            "paytmmall",
            "firstcry",
            "pepperfry",
            "urban ladder",
            "boat", "noise",
        ],
        "keywords": [
            "order confirmed", "order placed", "order shipped",
            "out for delivery", "delivered", "order cancelled",
            "return initiated", "refund", "exchange",
            "track your order", "invoice", "purchase",
            "payment confirmed", "payment received",
            "your order #", "order id",
            "estimated delivery", "dispatch",
        ],
    },

    # ── GOVERNMENT / OFFICIAL ────────────────────────────────────────────────
    "Government_Official": {
        "label": "🏛️ Government & Official",
        "gmail_label": "_Government_Official",
        "senders": [
            "incometax", "incometaxindia",
            "traces", "cbdt",
            "gst", "gstn",
            "epfindia", "epfo",
            "mca21", "mca",
            "uidai", "aadhaar",
            "passport", "passportindia",
            "digilocker",
            "nsdl",
            "gov.in", ".nic.in",
            "rbi", "reservebank",
            "sebi",
            "irctc", "indianrailways",
            "aaiclas", "aai",
            "eci", "election",
        ],
        "keywords": [
            "income tax", "itr", "tax return", "tds",
            "pan card", "aadhaar", "gst",
            "epf", "provident fund", "pf",
            "passport", "visa",
            "government notice", "official notice",
            "digilocker", "e-kyc",
            "election", "voter id",
            "challan", "fine",
        ],
    },

    # ── TRAVEL ──────────────────────────────────────────────────────────────
    "Travel": {
        "label": "✈️ Travel",
        "gmail_label": "_Travel",
        "senders": [
            "irctc", "indianrailways",
            "makemytrip", "goibibo",
            "cleartrip", "yatra",
            "ixigo",
            "indigo", "airindia",
            "spicejet", "akasaair",
            "vistara",
            "airbnb", "oyo",
            "treebo", "fabhotels",
            "redbus",
            "abhibus",
            "uber", "ola",
            "rapido",
        ],
        "keywords": [
            "booking confirmed", "ticket booked", "pnr",
            "flight", "train", "bus", "cab",
            "hotel booking", "check-in", "check-out",
            "boarding pass", "e-ticket",
            "cancellation", "refund initiated",
            "travel itinerary", "reservation",
        ],
    },

    # ── IMMIGRATION & VISA ───────────────────────────────────────────────────
    "Immigration_Visa": {
        "label": "🛂 Immigration & Visa",
        "gmail_label": "_Immigration_Visa",
        "senders": [
            # US Government
            "uscis.gov", "uscis",
            "travel.state.gov", "state.gov",
            "dhs.gov",
            "ice.gov",
            "cbp.gov",
            "ustraveldocs",
            "usembassy.gov",
            "nvc.state.gov", "nvc",
            "ceac.state.gov",
            # US Consulates in India
            "in.usembassy.gov",
            "usvisa-info",
            "ais.usvisa-info",
            # SEVIS / DHS
            "sevp.ice.gov", "sevp",
            "fmjfee", "fmjfee.com",
            "ice",
            # Immigration attorneys / portals
            "boundless",
            "immihelp",
            "immigration",
            "visajourney",
            "murthy",
            "fragomen",
            "envoy",
            "envoyintl",
            "ogletree",
            "berry",
            "fragomen",
            # Universities / DSOs (common)
            "international.student",
            "isss", "isso", "iss",
            "oiss", "ois",
            "internationalaffairs",
            "globalaffairs",
        ],
        "keywords": [
            # Visa types
            "f-1 visa", "f1 visa", "f-1", "f1",
            "h-1b", "h1b", "h1-b",
            "h4 visa", "h-4",
            "b1 visa", "b2 visa", "b1/b2",
            "j-1 visa", "j1",
            "l-1 visa", "l1",
            "o-1 visa", "o1",
            "eb-1", "eb-2", "eb-3", "eb1", "eb2", "eb3",
            "green card", "permanent resident", "lawful permanent",
            # Visa process
            "visa stamping", "visa stamp",
            "visa interview", "consular interview",
            "visa appointment", "appointment confirmed",
            "ds-160", "ds160",
            "221g", "221(g)", "administrative processing",
            "visa approved", "visa denied", "visa refused",
            "visa refusal", "visa rejection",
            "passport returned", "passport submitted",
            "dropbox appointment", "dropbox eligible",
            # Student visa
            "i-20", "i20", "form i-20",
            "sevis", "sevis fee", "sevis id",
            "cpt", "curricular practical training",
            "opt", "optional practical training",
            "stem opt", "stem extension",
            "ead", "employment authorization",
            "dso", "designated school official",
            "f-1 status", "student status",
            "out of status", "maintain status",
            # H1B
            "h1b lottery", "h-1b lottery",
            "h1b petition", "h-1b petition",
            "h1b transfer", "h-1b transfer",
            "h1b cap", "cap-subject",
            "cap-exempt",
            "lca", "labor condition",
            "prevailing wage",
            "rfe", "request for evidence",
            "noid", "notice of intent to deny",
            # Green Card / USCIS
            "priority date", "priority dates",
            "visa bulletin", "cut-off date",
            "i-140", "i140",
            "i-485", "i485", "adjustment of status",
            "i-130", "i130",
            "i-539", "i539",
            "i-765", "i765",
            "i-131", "i131", "advance parole",
            "uscis receipt", "receipt notice",
            "case status", "case update",
            "biometrics", "biometric appointment",
            "interview notice",
            "approval notice", "approval order",
            "nvc case", "national visa center",
            # Port of Entry / Travel
            "port of entry", "poe",
            "i-94", "i94", "arrival departure",
            "cbp", "customs and border",
            "travel history",
            "entry to the us", "admitted until",
            # Embassy & Consulates
            "us embassy", "us consulate",
            "hyderabad consulate", "chennai consulate",
            "mumbai consulate", "delhi embassy",
            "new delhi embassy",
            "consular section",
            "visa unit",
            "passport collection",
            "vac appointment", "visa application center",
            # General immigration
            "immigration", "immigrant",
            "nonimmigrant", "non-immigrant",
            "work authorization", "work permit",
            "travel document",
            "naturalization", "citizenship",
            "asylum",
        ],
    },
}

# ─────────────────────────────────────────────
# KEYWORD CLASSIFIER (No AI needed for clear matches)
# ─────────────────────────────────────────────

def classify_by_rules(sender: str, subject: str, body_snippet: str) -> str | None:
    """
    Returns category name if a strong keyword/sender match is found.
    Returns None if uncertain → will use AI fallback.
    """
    sender_lower  = sender.lower()
    subject_lower = subject.lower()
    text_lower    = (subject + " " + body_snippet).lower()

    for category, config in CATEGORIES.items():
        # 1. Check sender domain
        for s in config["senders"]:
            if s in sender_lower:
                return category

        # 2. Check keywords in subject + body
        matched_keywords = sum(1 for kw in config["keywords"] if kw in text_lower)
        if matched_keywords >= 2:
            return category

    return None  # Not enough confidence → use AI


# ─────────────────────────────────────────────
# AI FALLBACK CLASSIFIER
# ─────────────────────────────────────────────

def classify_with_ai(sender: str, subject: str, body_snippet: str) -> str:
    """Uses Claude API to classify ambiguous emails."""
    client = anthropic.Anthropic()

    category_list = "\n".join(
        [f"- {cat}: {', '.join(cfg['keywords'][:5])}" for cat, cfg in CATEGORIES.items()]
    )

    prompt = f"""You are an email classifier. Classify this email into EXACTLY ONE of these categories:
{category_list}
- Other: does not fit any above category

Email details:
From: {sender}
Subject: {subject}
Snippet: {body_snippet[:300]}

Reply with ONLY the category name, nothing else. Example: Banking_Transactions"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}]
    )

    result = message.content[0].text.strip()
    if result in CATEGORIES:
        return result
    return "Other"


# ─────────────────────────────────────────────
# GMAIL LABEL MANAGEMENT
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# CLEANUP OLD LABELS
# ─────────────────────────────────────────────

def remove_old_labels(mail: imaplib.IMAP4_SSL):
    """
    Removes the 3 old labels: _AgentProcessed, URGENT, IMPORTANT.
    Run this ONCE to clean up your Gmail.
    """
    old_labels = ["_AgentProcessed", "URGENT", "IMPORTANT"]
    print("\n🗑️  Removing old labels...")
    for label in old_labels:
        result = mail.delete(f'"{label}"')
        if result[0] == "OK":
            print(f"   ✅ Deleted: {label}")
        else:
            # Try without quotes
            result2 = mail.delete(label)
            if result2[0] == "OK":
                print(f"   ✅ Deleted: {label}")
            else:
                print(f"   ℹ️  Not found or already deleted: {label}")


def ensure_labels_exist(mail: imaplib.IMAP4_SSL):
    """Create all labels. Top-level labels with _ prefix."""
    for category, config in CATEGORIES.items():
        label = config["gmail_label"]
        mail.create(f'"{label}"')
    # Also ensure Tomorrow_Events exists at top
    mail.create('"__Tomorrow_Events"')
    print("✅ All labels verified/created in Gmail")




def move_email_to_label(mail: imaplib.IMAP4_SSL, uid: str, category: str):
    """Copies email to category folder and marks original as read."""
    if category == "Other":
        return

    label = CATEGORIES[category]["gmail_label"]

    # Copy to category label
    result = mail.uid("COPY", uid, f'"{label}"')
    if result[0] == "OK":
        # Mark original as processed (add a flag)
        mail.uid("STORE", uid, "+FLAGS", "\\Seen")
        print(f"   ✅ Moved to: {label}")
    else:
        print(f"   ❌ Failed to move: {result}")


# ─────────────────────────────────────────────
# EMAIL FETCHING & PROCESSING
# ─────────────────────────────────────────────

def decode_str(s):
    """Decode email header strings."""
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
    """Extract plain text body from email."""
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
    return body[:500]  # First 500 chars is enough for classification


def process_inbox(max_emails: int = 50, use_ai_fallback: bool = True):
    """
    Main function: connects to Gmail, fetches unread emails,
    classifies them, and moves to appropriate labels.
    """
    print("\n" + "="*60)
    print("🤖 AI Email Agent Starting...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Connect to Gmail
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        print(f"✅ Connected as: {GMAIL_USER}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # Ensure labels exist
    mail.select("inbox")
    ensure_labels_exist(mail)

    # Fetch unread emails
    status, messages = mail.uid("SEARCH", None, "UNSEEN")
    if status != "OK":
        print("❌ Could not fetch emails")
        return

    email_uids = messages[0].split()
    total = len(email_uids)
    print(f"\n📬 Found {total} unread emails. Processing up to {max_emails}...\n")

    # Stats tracker
    stats = {cat: 0 for cat in CATEGORIES}
    stats["Other"] = 0
    stats["ai_used"] = 0

    for i, uid in enumerate(email_uids[-max_emails:]):  # Process latest N
        try:
            # Fetch email
            status, data = mail.uid("FETCH", uid, "(RFC822)")
            if status != "OK":
                continue

            raw = data[0][1]
            msg = email.message_from_bytes(raw)

            sender  = decode_str(msg.get("From", ""))
            subject = decode_str(msg.get("Subject", ""))
            body    = get_email_body(msg)

            print(f"[{i+1}/{min(total, max_emails)}] 📧 {subject[:60]}")
            print(f"   From: {sender[:50]}")

            # Step 1: Try rule-based classification
            category = classify_by_rules(sender, subject, body)

            # Step 2: AI fallback if rules didn't match
            if category is None and use_ai_fallback:
                print(f"   🤖 Using AI classifier...")
                category = classify_with_ai(sender, subject, body)
                stats["ai_used"] += 1
            elif category is None:
                category = "Other"

            print(f"   📂 Category: {category}")

            # Move email
            move_email_to_label(mail, uid, category)

            stats[category] = stats.get(category, 0) + 1
            print()

        except Exception as e:
            print(f"   ⚠️ Error processing email: {e}\n")
            continue

    # Summary
    print("="*60)
    print("📊 CLASSIFICATION SUMMARY")
    print("="*60)
    for cat, count in stats.items():
        if cat != "ai_used" and count > 0:
            emoji = CATEGORIES.get(cat, {}).get("label", cat)
            print(f"  {emoji}: {count} emails")
    print(f"\n  🤖 AI fallback used: {stats['ai_used']} times")
    print(f"  ✅ Done at {datetime.now().strftime('%H:%M:%S')}")

    mail.logout()
    return stats


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    process_inbox(max_emails=100, use_ai_fallback=True)
