# 🎫 EventFlow

<div align="center">

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-EventFlow-blue?style=for-the-badge)](https://eventflow-g2h5.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-red?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?style=for-the-badge&logo=sqlite)](https://sqlite.org)

**A comprehensive event management platform built with Flask**

*Organize events, manage venues, sell tickets, and track attendance - all in one place*

[🌟 Try Live Demo](https://eventflow-g2h5.onrender.com) • [📖 Documentation](#getting-started)

</div>

## ✨ Features

<table>
<tr>
<td width="50%">

### 👥 For Attendees
- 🔐 **Secure Authentication** - Safe signup and login system
- 🔍 **Event Discovery** - Browse events with detailed information
- 🎟️ **Ticket Booking** - Book tickets with multiple pricing tiers
- 📱 **Ticket Management** - View and manage your bookings
- ❌ **Easy Cancellation** - Cancel tickets with automatic refunds

</td>
<td width="50%">

### 🎯 For Organizers
- 📊 **Dashboard** - Comprehensive event statistics and management
- 📅 **Event Management** - Create, edit, and delete events
- 🏢 **Venue Management** - Add and manage event venues
- 🎤 **Speaker Management** - Add speakers with detailed profiles
- 🎫 **Ticket Control** - Create ticket types with custom pricing
- 📈 **Sales Overview** - Track orders and ticket sales

</td>
</tr>
</table>

## 🏗️ Project Structure
```
EventFlow/
├── 🐍 app.py              # Main application file
├── 🚀 start.py            # Production startup script
├── ⚙️  config.py           # Configuration settings
├── 📦 requirements.txt    # Python dependencies
├── 🗄️  schema_sqlite.sql   # SQLite database schema
├── 👤 create_admin_users.py  # Admin user creation script
├── 🧹 clean_data.py       # Database cleanup utility
├── 🎨 static/            # Static assets (CSS, JS, images)
├── 📄 templates/         # HTML templates
└── 🔐 .env               # Environment variables
```

## 🚀 Getting Started

### 📋 Prerequisites
- 🐍 **Python 3.8+** - Programming language
- 📦 **pip** - Python package manager  
- 🔧 **Git** - Version control

### 💻 Local Development

1. **📥 Clone the repository**
   ```bash
   git clone https://github.com/tanishpoddar/EventFlow.git
   cd EventFlow
   ```

2. **🐍 Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Unix/MacOS
   source venv/bin/activate
   ```

3. **📦 Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **⚙️ Configure environment**
   Create a `.env` file:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   DATABASE_URL=sqlite:///eventhub.db
   SECRET_KEY=your-secret-key-here
   PORT=5000
   ```

5. **🚀 Launch application**
   ```bash
   python create_admin_users.py  # Create test accounts (optional)
   python app.py
   ```
   
   🌐 **Access at**: `http://127.0.0.1:5000`

## 🔑 Test Credentials

<div align="center">

### 🧪 Ready-to-Use Demo Accounts

<table>
<tr>
<th>👑 Administrator</th>
<th>🎯 Organizer</th>
<th>🛒 Buyer/Attendee</th>
</tr>
<tr>
<td align="center">
<strong>Email:</strong><br>
<code>admin@eventhub.com</code><br>
<strong>Password:</strong><br>
<code>Admin@123</code><br>
<em>Full system access</em>
</td>
<td align="center">
<strong>Email:</strong><br>
<code>organizer@eventhub.com</code><br>
<strong>Password:</strong><br>
<code>Organizer@123</code><br>
<em>Event management</em>
</td>
<td align="center">
<strong>Email:</strong><br>
<code>buyer@eventhub.com</code><br>
<strong>Password:</strong><br>
<code>Buyer@123</code><br>
<em>Ticket purchasing</em>
</td>
</tr>
</table>

💡 **These credentials are displayed on the login page with convenient "Use These" buttons**

🎮 **[Try Live Demo →](https://eventflow-g2h5.onrender.com)**

</div>

## 🛠️ Development

### 🗄️ Database Management
- **Migrations**: Use Flask-SQLAlchemy for database operations
  ```bash
  python -c "from app import app, db; app.app_context().push(); db.create_all()"
  ```

### 📝 Code Style
- 📏 Uses `.hintrc` for code style guidelines
- 🐍 Follows PEP 8 standards for Python code

## 🗄️ Database Schema

EventFlow uses **SQLite** with these main tables:

| Table | Description |
|-------|-------------|
| 👤 **User** | User information and roles |
| 📅 **Event** | Event details, dates, and venues |
| 🏢 **Venue** | Venue information and capacity |
| 🎤 **Speaker** | Speaker details linked to events |
| 🎫 **TicketType** | Different ticket types for events |
| 🎟️ **Ticket** | Individual tickets booked by users |
| 📦 **Order** | Groups tickets purchased by a user |
| 💳 **Payment** | Payment information for orders |

📋 **For detailed schema**: See `schema_sqlite.sql`

## ⚙️ Configuration

Configure the application through:

1. 🔐 **Environment Variables** - Set in `.env` file for local development
2. 📝 **config.py** - Contains default configuration values  
3. 🌐 **Render Environment Variables** - Set in Render dashboard for production

## 📄 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by [Tanish Poddar](https://github.com/tanishpoddar)**

⭐ **Star this repo if you found it helpful!**

</div>
