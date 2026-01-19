# CyberSec Daily Brief

A fully autonomous bot that collects, ranks, and emails the top 10 cybersecurity and IT news stories of the last 24 hours.

## Features
- **Aggregates news** from sources like The Hacker News, BleepingComputer, Krebs on Security, etc.
- **Ranks stories** based on keywords (zero-day, breach, critical) and freshness.
- **Deduplicates** content to avoid repetition.
- **Emails a clean briefing** to your inbox every day.
- **GitHub Actions Integration** for 100% automated daily runs.

## Setup

### 1. Prerequisites
- Python 3.8+
- An email account (e.g., Gmail with App Password) to send emails.

### 2. Local Installation
```bash
git clone <repository-url>
cd CyberSecBrief
pip install -r requirements.txt
```

### 3. Configuration
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` with your details:
- `SMTP_USER`: Your email address
- `SMTP_PASSWORD`: **This is NOT your login password.**
    1. Go to your [Google Account Security page](https://myaccount.google.com/security).
    2. Enable **2-Step Verification** if it isn't already.
    3. Search for **"App Passwords"** in the search bar at the top (or look under 2-Step Verification).
    4. Create a new App Password named "CyberSecBrief".
    5. Copy the 16-character code (remove spaces) and paste it here.
- `RECIPIENT_EMAIL`: Where to send the news (e.g., ballzballer53@gmail.com)

### 4. Running Locally
```bash
python src/main.py
```

## Deployment (GitHub Actions)

1. Push this code to a new GitHub repository.
2. Go to **Settings > Secrets and variables > Actions**.
3. Add the following repository secrets:
   - `SMTP_SERVER` (e.g., smtp.gmail.com)
   - `SMTP_PORT` (e.g., 587)
   - `SMTP_USER`
   - `SMTP_PASSWORD`
   - `RECIPIENT_EMAIL`
4. The workflow is scheduled to run daily at 08:00 UTC. You can also trigger it manually from the "Actions" tab.

## Project Structure
- `src/collector.py`: Fetches RSS feeds.
- `src/processor.py`: Cleans, deduplicates, and ranks stories.
- `src/emailer.py`: Generates HTML and sends via SMTP.
- `src/main.py`: Main entry point.
- `.github/workflows/daily_brief.yml`: Automation schedule.
