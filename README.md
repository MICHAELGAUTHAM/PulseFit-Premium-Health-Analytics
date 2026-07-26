# PulseFit - Full-Stack Premium Health Dashboard

PulseFit is a premium health and habit tracking web application upgraded into a complete full-stack system built using FastAPI, SQLAlchemy, SQLite/PostgreSQL, and pure HTML/CSS/JavaScript with Chart.js.

---

## Features

1. **Dynamic Authentication System**:
   - Secure Login with "Remember Me" and Password visibility toggles.
   - User registration capturing physical parameters (age, height, weight, gender).
   - Multi-step Forgot Password recovery using 6-Digit OTP security codes.
   - REVOCATION/revoking active sessions upon logout.

2. **Interactive Biometric Bento Grid**:
   - Live synchronization of daily steps, calorie outputs, hydration, and circadian sleep metrics.
   - Quick-add hydration levels utilizing a rising liquid wave and bubble percentage gauge.
   - Interactive BMI gauge calculator with sliders that autosaves metrics on slider release.

3. **Gamified Milestones & Alerts**:
   - Real-time achievements checker that unlocks 6 custom badges (e.g. Hydro Master, 7-Day Streak, Goal Crusher) and saves them in the database.
   - Dynamic notification dispatcher storing warning alerts, reminders, and unlock notifications.

4. **Aggregate History Analytics**:
   - Multi-tab history page drawing 6 graphs (heart rate, calories, steps, water, sleep, weight) using Chart.js based on Weekly, Monthly, and Yearly aggregates.
   - Tabular record logs details list supporting single-log deletion.

---

## Directory Structure

```text
frontend/
  index.html            (Main Page: Public Landing or Authenticated Bento Dashboard)
  login.html            (Auth Login)
  register.html         (Auth Register)
  forgot-password.html  (OTP & Password Reset)
  profile.html          (Biometrics, Avatar Upload, Password Settings)
  settings.html         (Toggles, Language, JSON Data Exports, Account Deletion)
  history.html          (6 Chart.js Analytics & Logs Table)
  notifications.html    (Read/Unread Reminders Timeline)
  achievements.html     (Unlocked Badges Grid)
  about.html, contact.html, faq.html, privacy.html, terms.html (Public marketing pages)
  assets/
    css/
      style.css         (Existing design variables & bento layout stylesheet)
      pages.css         (New modular forms, tables, badges, and notifications styles)
    js/
      auth.js           (Global Session Validation, Toasts, API fetch wrappers)
      script.js         (Bento grid dynamic logging triggers & live chart handlers)

backend/
  app/
    models/             (SQLAlchemy models: users, health, goals, badges, sessions)
    schemas/            (Pydantic validation schemas)
    routers/            (FastAPI routing: auth, health, goals, achievements, analytics)
    services/           (Services: auth encrypt, achievement checkers)
    database.py         (SQLAlchemy engine setup supporting PostgreSQL & SQLite)
    main.py             (FastAPI startup, CORS registry, static asset mount pathways)
  requirements.txt      (Python packages)
```

---

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript ES6, Chart.js, Lucide Icons, Canvas Confetti.
- **Backend**: Python 3.8+, FastAPI, SQLAlchemy, SQLite (Default zero-config local run) or PostgreSQL (configured via environment), python-jose (JWT), passlib[bcrypt] (Password hashing), python-multipart.

---

## Getting Started (Local Run)

### 1. Initialize Virtual Environment and Dependencies
Open a terminal in the root workspace folder:

```powershell
# Create environment
python -m venv .venv

# Activate environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Configure Database (Optional)
By default, PulseFit auto-generates a local SQLite file `pulsefit.db` in your root folder. If you wish to connect to a PostgreSQL instance instead, configure your connection string in the environment:

```powershell
$env:DATABASE_URL="postgresql://username:password@localhost:5432/pulsefit"
```

### 3. Start the Server
Run the Uvicorn local hosting server:

```powershell
.venv\Scripts\uvicorn backend.app.main:app --reload
```

The application will launch on: **`http://localhost:8000`**

- **Public Landing Page**: Navigate to `http://localhost:8000` (when logged out).
- **Interactive Dashboard**: Automatically renders at `http://localhost:8000` once you register and sign in!
- **API Docs**: Open `http://localhost:8000/docs` to view the Swagger API catalog.
