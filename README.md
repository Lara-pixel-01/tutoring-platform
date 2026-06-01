# 📚 Tutoring Platform

**A web platform connecting tutors and students for booking 1-on-1 sessions.**

🔗 **Live Demo:** *Coming soon*  
📅 **Status:** Active development

---

## ✨ Features

- **Authentication** — Email/password + OAuth (Google, GitHub)
- **Real-time Chat** — WebSocket messaging (Socket.IO)
- **Smart Scheduling** — Timezone-aware calendar for sessions
- **Reviews & Ratings** — Students rate tutors, tutors build reputation
- **Portfolio** — Tutors can upload work samples
- **Notifications** — Real-time alerts for booking requests
- **Session Management** — Create, accept, decline, and track sessions
- **Testing** — pytest with session-scoped fixtures

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | Python, Flask, SQLAlchemy, Flask-SocketIO |
| **Database** | PostgreSQL |
| **Frontend** | HTML, CSS, Jinja2 templates |
| **Auth** | Flask-Login, Authlib (OAuth) |
| **DevOps** | Docker, Docker Compose |
| **Testing** | pytest |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- PostgreSQL (or use Docker)

### Run with Docker Compose

```bash
# Clone the repository
git clone https://github.com/Lara-pixel-01/tutoring-platform.git
cd tutoring-platform

# Start services
docker-compose up --build
