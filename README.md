# Investigator X – Cyber Recon Toolkit

A professional, GUI-based cybersecurity reconnaissance tool built in Python with PyQt5.

## Features

| Module | Capabilities |
|---|---|
| Network Scanner | Ping sweep, port scanning, banner grabbing, multithreaded |
| URL Analyzer | Risk scoring, suspicious keyword detection, HTTPS check |
| Domain Intelligence | WHOIS, DNS (A/MX/NS), IP resolution, subdomain brute-force |
| Email Intelligence | Format validation, MX lookup, domain existence check |
| Reports | JSON/TXT export, timestamped session logs |

## Installation

### Prerequisites
- Python 3.9+
- pip

### Steps

```bash
# 1. Clone or extract the project
cd "InvestigatorX"

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

## Project Structure

```
InvestigatorX/
├── main.py
├── requirements.txt
├── gui/
│   ├── main_window.py
│   ├── styles.py
│   └── widgets/
│       ├── dashboard.py
│       ├── network_scanner.py
│       ├── url_analyzer.py
│       ├── domain_intel.py
│       ├── email_intel.py
│       └── reports.py
├── modules/
│   ├── scanner.py
│   ├── url_checker.py
│   ├── domain_lookup.py
│   └── email_checker.py
└── utils/
    ├── logger.py
    ├── exporter.py
    └── workers.py
```

## Disclaimer

> **For educational and authorized use only.**  
> Scanning networks or systems without explicit permission is illegal.  
> The developers are not responsible for any misuse of this tool.

## Tech Stack

- **GUI**: PyQt5
- **Networking**: socket, requests
- **DNS/WHOIS**: dnspython, python-whois
- **Threading**: QThread (non-blocking GUI)
