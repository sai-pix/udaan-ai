# Udaan AI — Barrier-Aware Livelihood Pathways

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask 3.1+](https://img.shields.io/badge/Framework-Flask%203.1-teal.svg)](https://palletsprojects.com/p/flask/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Pilot Ready](https://img.shields.io/badge/Status-AP%20Pilot%20Ready-success.svg)]()

> *"From immediate needs to dignified, sustained livelihoods."*

**Udaan AI** is an open-source, barrier-aware livelihood matching and referral web application designed for adults experiencing homelessness, long-term unemployment, or acute economic insecurity. Targeted at a community pilot in **Andhra Pradesh, India** (Visakhapatnam, Vijayawada, Guntur, Tirupati), the platform bridges support seekers, registered NGOs/shelters, and fair employers.

---

## 🌟 The Core Innovation: Barrier-Aware Matching

Conventional job portals assume the applicant has stable housing, identity cards, regular meals, transportation, and an active bank account. For displaced or homeless individuals, these missing prerequisites prevent entry.

Instead of merely recommending job vacancies, **Udaan AI**:
1. **Identifies Concrete Barriers:** Detects acute hurdles such as lack of safe night shelter, missing Aadhaar cards, no bank passbook, or transportation limitations.
2. **Pairs Barrier-Resolving Support:** Matches the user with verified community resources (night shelters, civic welfare desks, free vocational programs) to resolve prerequisites before or during onboarding.
3. **Generates Personalized 6-Step Pathways:** Constructs a sequential, human-reviewable roadmap from immediate shelter stability to wage retention.
4. **Enables Dual Connection Modes:**
   - **Direct Contact:** Verified phone numbers, addresses, and navigation links.
   - **Consent-Based Referrals:** Generates unique tracking reference codes (`REF-2026-XXXX`) with strict organization data isolation.
5. **Zero-Forced-KYC Principle:** No Aadhaar numbers, biometric scans, photographs, or sensitive histories are ever required to receive a pathway.

---

## 🏗️ Technology Stack

- **Backend:** Python, Flask 3.1, Flask Blueprints, REST API endpoints.
- **Database:** SQLAlchemy 2.0. SQLite for local development; persistent PostgreSQL support via `DATABASE_URL` for hosted environments.
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons, Chart.js for impact analytics.
- **AI Integration:** Google Gemini API (`google-genai` SDK) with structured JSON schemas and a **robust deterministic keyword fallback engine** (supporting English and Telugu) when the API key is unconfigured.
- **Internationalization:** Full native English and Telugu (తెలుగు) interface.

---

## 🚀 Quickstart & Local Installation

### 1. Clone & Enter Project Directory
```powershell
cd C:\Users\kuran\.gemini\antigravity\scratch\udaan-ai
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Initialize & Seed Demo Scenario
```powershell
python scripts\seed_demo.py
```

### 4. Run the Application
```powershell
python run.py
```
Open your browser to: **`http://localhost:5000`**

---

## 🧪 Running Automated Tests

A comprehensive test suite of 27 automated tests validates startup, authentication, RBAC, intake, AI fallback, barrier matching, pathways, referral lifecycles, organization data isolation, right to erasure, and multilingual support:

```powershell
pytest tests -v
```

---

## 👥 Demonstration Mode & Test Accounts

When `DEMO_MODE=true` is enabled, pre-seeded synthetic data for Andhra Pradesh is available with one-click demo login buttons:

| Role | Username / Email | Password | Organization / Context |
| :--- | :--- | :--- | :--- |
| **Support Seeker** | `seeker@udaan.demo` | `DemoSeeker2026!` | Fictional persona (Raju V.) with cleaning experience and shelter barrier |
| **NGO Staff** | `karuna.staff@udaan.demo` | `DemoKaruna2026!` | Karuna Shelter & Livelihood Trust (Visakhapatnam) |
| **Employer** | `coastal.hr@udaan.demo` | `DemoCoastal2026!` | Coastal Logistics & Facility Services (Visakhapatnam) |
| **Administrator** | `admin@udaan.demo` | `DemoAdmin2026!` | System Administrator & Audit Oversight |

*Note: All synthetic demo organizations and jobs are visibly badged `DEMO DATA`. Simulated responses do not send external messages or contact real people.*

---

## 🌐 Deploying to Render

This application is ready for 1-click or Git deployment to [Render](https://render.com) using the included `render.yaml` Blueprint.

### Deploy Steps:
1. Push this repository to GitHub or GitLab.
2. In the Render Dashboard, click **New > Blueprint** and link the repository.
3. Render automatically creates:
   - A **Web Service** running Gunicorn.
   - A **PostgreSQL Database** (`udaan-db`) with automatic connection string binding.
4. Set optional environment variable `GEMINI_API_KEY` in the Render dashboard if live Gemini AI interpretation is desired (otherwise the built-in deterministic rule engine handles all requests gracefully).

### Production Administrator Setup
To initialize the first administrator in production without hardcoded credentials:
1. Go to the login page (`/login`).
2. Expand the **"Initial Admin Bootstrap"** section.
3. Enter the `ADMIN_SETUP_SECRET` configured in your environment variables along with your chosen admin username and password.

---

## 🛡️ Privacy & Security Features

- **Data Minimization:** No government ID numbers, Aadhaar, photographs, or sensitive histories are collected.
- **Strict Organization Isolation:** NGO and Employer accounts can only view referrals explicitly assigned to them. Cross-organization access triggers HTTP 403 Forbidden.
- **Right to Erasure:** A visible **"Erase My Data"** button allows seekers to permanently wipe their session profile and generated pathways at any time.
- **Non-Discrimination:** Algorithmic rules strictly prohibit recording or inferring caste, religion, disability, or criminal record.

---

## 📄 License
Released under the [MIT License](LICENSE). Built for social impact and community empowerment.
