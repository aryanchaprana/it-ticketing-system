# IT Helpdesk Ticketing System

> A full-featured internal IT support portal built with Python & Flask — designed for companies that need a structured, trackable way to handle employee IT issues.

---

## 🧩 The Problem It Solves

Most small and mid-sized companies handle IT issues over WhatsApp, email, or verbal requests. There's no tracking, no accountability, and no record of what was fixed and when. This system replaces that chaos with a structured helpdesk workflow.

---

## ✅ Key Features

### For Employees
- Raise tickets from any device — no login required for public submission
- Choose category: Hardware, Software, Network, CCTV, or Application (SAP, MES, etc.)
- Set priority: Low, Medium, High
- Attach screenshots or files to describe the issue
- Receive email notifications when ticket is assigned and resolved
- Track ticket status in real-time

### For IT Staff
- Personal dashboard showing all assigned tickets
- Update ticket status: Assigned → In Progress → Solved
- Add resolution remarks and estimated resolution time
- View full ticket history

### For Admins
- Full visibility across all tickets and departments
- Create and manage staff/employee accounts
- Assign tickets to specific IT staff members
- View solved ticket history and performance
- Auto-generated ticket reference numbers (TKT-00001, TKT-00002...)

---

## 🔐 Role-Based Access Control

| Role | Access |
|---|---|
| **Admin** | Full system access, user management, all tickets |
| **IT Staff** | Own assigned tickets, status updates |
| **Employee** | Submit tickets, track own submissions |

---

## 📬 Email Notifications

Automatic email alerts are sent when:
- A ticket is raised (to IT team)
- A ticket is solved (to the employee who raised it)

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Database:** SQLite (easily swappable to PostgreSQL)
- **Auth:** Flask-Login with PBKDF2 password hashing
- **Email:** Flask-Mail
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templates)
- **Deployment-ready:** Gunicorn + Nginx config included

---

## 📸 Screenshots

> *(Add screenshots here — login page, employee dashboard, admin ticket view)*

---

## 🚀 Getting Started

```bash
git clone https://github.com/aryanchaprana/it-ticketing-system
cd it-ticketing-system
pip install -r requirements.txt
cp .env.example .env   # add your email credentials
flask db upgrade
flask run
```

---

## 💡 Built For

This system was built for a manufacturing company's IT department. It is general enough to be adapted for any company that needs an internal helpdesk — clinics, logistics companies, schools, and offices of any size.

---

## 📫 Want This For Your Business?

I build and customize systems like this for companies. Reach out: **aryanchaprana4321@gmail.com**
