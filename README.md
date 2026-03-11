# Smart File Organizer Pro 🚀

A production-ready, advanced file organization system that intelligently manages your cluttered directories. Built with a robust Python/Flask backend and a modern, high-performance web dashboard.

## 🌟 Key Features

-   **Intelligence-Driven Scanning**: Recursively indexes directories and categorizes files (Images, Documents, Videos, etc.) using a zero-lag background engine.
-   **Terminal Visibility**: Real-time processing logs in your console to monitor active organization and scanning tasks.
-   **Architecture Stability**: Centralized extension management to prevent circular dependencies and ensure high availability.
-   **Duplicate Detection**: Byte-perfect duplicate identification using SHA-256 hashing.
-   **Smart Rules Engine**: Move files automatically based on file extensions or custom routing rules.
-   **Responsive Dashboard**: Beautiful charts (Chart.js) and metrics tracking your storage health and wasted space.
-   **Activity Audit**: Complete historical log of every move, rename, or deletion performed.

## 🏗️ Technical Architecture

-   **Backend**: Python (Flask) with REST API architecture.
-   **Database**: PostgreSQL (via Neon) using SQLAlchemy ORM.
-   **Auth**: JWT (JSON Web Tokens) for API security & Flask-Login for session management.
-   **Scheduling**: APScheduler for hands-free, recurring background organization.
-   **Frontend**: TailwindCSS + Vanilla JS + Chart.js for a premium, glassmorphism UI.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9 or higher.
- A PostgreSQL database (Recommended: [Neon.tech](https://neon.tech) for instant cloud DB).

### 2. Installation
```bash
# Clone the repository (or navigate to folder)
cd "Smart File Organizer"

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://user:password@host/dbname
SECRET_KEY=your_secure_random_key_here
```

### 4. Running the Application
```bash
# Start the server (runs on http://127.0.0.1:5000)
python backend/app.py
```

## 📁 Project Structure

```text
├── backend/
│   ├── models/        # Database models (User, File, Duplicate, etc.)
│   ├── routes/        # API Blueprints (Auth, Scanner, Organizer)
│   ├── services/      # Core logic (Scanning, Organizing, Hashing)
│   ├── extensions.py  # Shared Flask extensions (DB, Login, JWT)
│   └── app.py         # Application factory and entry point
├── frontend/
│   ├── static/        # CSS (Tailwind), JS (API, Main), and Assets
│   └── templates/     # HTML pages (Dashboard, Scanner, etc.)
└── requirements.txt   # Backend dependencies
```

## 🔐 Security & Safety
- **JWT Protection**: All core API endpoints are secured.
- **Transactional Moves**: Files are moved using standard `shutil` with error handling.
- **Undo Support**: Maintain a record of previous file paths to allow for organization reversals.

---
Built with ❤️ for better digital organization.
