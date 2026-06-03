# 📬 Gmail AI Email Classification Agent

> **Autonomous email triage agent — built in Python AND Google Apps Script**
> Inspired by Harvard CS50's Introduction to Artificial Intelligence with Python

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/Google_Apps_Script-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Gmail](https://img.shields.io/badge/Gmail_API-EA4335?style=for-the-badge&logo=gmail&logoColor=white)
![AI Agent](https://img.shields.io/badge/AI_Agent-Autonomous-brightgreen?style=for-the-badge)
![CS50](https://img.shields.io/badge/Harvard-CS50_AI-A51C30?style=for-the-badge&logo=harvard&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

---

## 🤖 What This Agent Does

A **fully autonomous AI agent** that reads your Gmail inbox, classifies every email into smart categories, and surfaces urgent deadlines into a daily action dashboard — automatically, every hour, for free.

Built in **two versions**:
- 🐍 **Python version** — runs on your local machine or any server
- ☁️ **Google Apps Script version** — runs directly inside Gmail, zero installation

---

## 🧠 AI Concepts Applied (CS50 AI — Harvard University)

This project directly applies concepts from **CS50's Introduction to Artificial Intelligence with Python** (Harvard University, May 2026):

| CS50 AI Concept | Applied In This Project |
|---|---|
| **Search Algorithms** | Priority-based email triage logic |
| **Knowledge Representation** | Rule-based sender + keyword classification engine |
| **Uncertainty & Probability** | Confidence scoring — 2+ keyword matches required before classification |
| **Machine Learning Thinking** | Pattern recognition across 220+ keywords, 275+ sender domains |
| **AI Agents** | Full autonomous perception → reasoning → action loop |
| **Natural Language Processing** | Email body parsing, date extraction, urgency detection |

> *"CS50 AI gave me the framework to think about agents — systems that perceive their environment, make decisions, and act autonomously. This project is that framework applied to a real-world problem I face every day."*
> — Sai Krishna Vaka

---

## 📁 Repository Structure

```
gmail-ai-agent/
│
├── 📂 python_version/
│   ├── email_agent.py        ← Main classifier (Python + IMAP)
│   ├── scheduler.py          ← Runs every hour automatically
│   ├── tomorrow_events.py    ← Today Events engine (Claude AI)
│   └── requirements.txt      ← Dependencies
│
├── 📂 google_apps_script/
│   └── email_agent.gs        ← Complete agent (JavaScript, zero install)
│
├── README.md
└── LICENSE
```

---

## 📂 Label Structure (10 Labels)

```
Gmail Sidebar
├── 📅 __Today_Events          ← Daily action dashboard (TOP)
├── 📂 _Banking_Transactions   ← 60+ Indian banks, UPI, NEFT, RTGS
├── 💳 _Credit_Cards           ← HDFC, SBI, ICICI, Axis, Amex
├── 🏥 _Medical_Hospital       ← Apollo, Fortis, Practo, insurance
├── 💼 _Job_Recruitment        ← Naukri, LinkedIn, interviews, offers
├── 📺 _Subscriptions          ← Netflix, Spotify, Adobe, SaaS
├── 🛍️ _Shopping_Ecommerce     ← Amazon, Flipkart, Swiggy, Zomato
├── 🏛️ _Government_Official    ← Income Tax, GST, EPFO, UIDAI
├── ✈️  _Travel                ← IRCTC, flights, hotels, Uber/Ola
├── 🛂 _Immigration_Visa       ← F-1, H1B, USCIS, 221G, DS-160
└── 📁 _Other                  ← Everything else
```

---

## ⚙️ How Classification Works

```
New Email Arrives
       │
       ▼
┌─────────────────────────┐
│  Step 1: Sender Domain  │ → hdfcbank.com = _Banking ✅
│  Matching (275+ domains)│   (instant, no API needed)
└─────────────────────────┘
       │ No match
       ▼
┌─────────────────────────┐
│  Step 2: Keyword        │ → 2+ keywords match = category ✅
│  Detection (220+ words) │   (fast, free)
└─────────────────────────┘
       │ No match
       ▼
┌─────────────────────────┐
│  Step 3: Claude AI      │ → (Python version only)
│  Fallback Classifier    │   reads subject + body → decides
└─────────────────────────┘
       │
       ▼
   Gmail Label Applied ✅
```

---

## 📅 Today_Events — Daily Action Dashboard

Every morning at **6:00 AM** the agent scans all 9 labels and checks:

1. Does the email mention **tomorrow's date** in any format?
   - `27 June 2026` / `27/06/2026` / `June 27` / `tomorrow`
2. Does it contain **urgent action keywords**?
   - `deadline`, `last date`, `payment due`, `action required`, `expires today`...

If YES → email copied to `__Today_Events`

At **midnight** → label clears and resets for the new day.

**Result:** Every morning you see exactly what needs your attention today.

---

## 🚀 Setup — Python Version

### Prerequisites
- Python 3.8+
- Gmail account with IMAP enabled
- Gmail App Password
- Anthropic API key (for AI fallback)

### Installation
```bash
# Clone the repo
git clone https://github.com/saikrishnaGT/gmail-ai-agent.git
cd gmail-ai-agent/python_version

# Install dependencies
pip install -r requirements.txt

# Set environment variables (Mac/Linux)
export GMAIL_USER="your_email@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
export ANTHROPIC_API_KEY="sk-ant-..."

# Run once
python email_agent.py

# Run on auto schedule (every hour)
python scheduler.py
```

---

## 🚀 Setup — Google Apps Script Version (Zero Installation)

1. Go to → `https://script.google.com`
2. New Project → paste `email_agent.gs`
3. Select `setup` → click ▶️ Run → Allow permissions
4. Select `createTriggers` → click ▶️ Run
5. **Done — runs forever automatically, completely free**

---

## ⏰ Automation Schedule

| Function | Schedule | What it does |
|---|---|---|
| `classifyEmails` | Every 1 hour | Sorts all unread emails |
| `runTodayEvents` | Daily 6:00 AM | Fills Today_Events |
| `clearTodayEvents` | Daily 12:00 AM | Resets Today_Events |

---

## 📊 Classification Coverage

| Category | Senders | Keywords |
|---|---|---|
| Banking & Transactions | 60+ | 30+ |
| Credit Cards | 20+ | 20+ |
| Medical & Hospital | 35+ | 25+ |
| Job & Recruitment | 40+ | 25+ |
| Subscriptions | 30+ | 15+ |
| Shopping & E-Commerce | 25+ | 15+ |
| Government & Official | 20+ | 20+ |
| Travel | 20+ | 15+ |
| Immigration & Visa | 25+ | 50+ |
| **Total** | **275+** | **220+** |

---

## 🏦 Indian Banks Covered (60+)

**Public Sector:** SBI, PNB, Bank of Baroda, Canara, Union Bank, Indian Bank, Bank of India, UCO, Central Bank

**Private Sector:** HDFC, ICICI, Axis, Kotak, Yes Bank, IndusInd, IDFC First, Federal, RBL, Bandhan, South Indian, Karnataka, KVB, City Union

**Small Finance & Payments:** AU, Equitas, Ujjivan, Paytm Bank, Airtel Payments, Fino, Jio Payments

**Fintech:** Razorpay, PhonePe, Google Pay, Amazon Pay, Cashfree, PayU, BillDesk

---

## 🛂 Immigration & Visa (Built for Indian Professionals)

Covers the complete US visa journey:
- **Student:** F-1, I-20, SEVIS, CPT, OPT, STEM OPT, EAD
- **Work:** H-1B lottery, petition, transfer, RFE, NOID
- **Green Card:** I-140, I-485, priority dates, visa bulletin
- **Consulates:** Hyderabad, Chennai, Mumbai, Delhi
- **Process:** DS-160, 221G, administrative processing, biometrics, I-94

---

## 🧑‍💻 About the Author

**Sai Krishna Vaka** — Data Engineer

- 🎓 MSIS — Central Michigan University, USA
- 🏆 Harvard CS50 AI with Python — May 2026
- 💼 5+ years — TCS (Biogen Healthcare) + CredX USA
- 🚀 Founder — Quick Wash (WMaaS Startup, Bangalore)
- 🔗 [LinkedIn](https://linkedin.com/in/sai-krishna-vaka-31062a205)
- 🐙 [GitHub](https://github.com/saikrishnaGT)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

⭐ **If this project helped you, give it a star!**

*Built as CS50 AI capstone — demonstrating real-world autonomous agent design using Knowledge Representation, NLP, and AI Agent principles.*
