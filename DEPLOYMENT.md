# Render Deployment Guide

## Quick Deployment Steps

1. **Fork this repository** to your GitHub account

2. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Sign up/login with your GitHub account
   - Click "New +" → "Web Service"
   - Connect your forked repository

3. **Configure the service**:
   - **Name**: `eventhub-app` (or your preferred name)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start.py`
   - **Environment**: `Python 3`

4. **Set Environment Variables**:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secure-random-secret-key-here`
   - `DATABASE_URL=sqlite:///eventhub.db` (optional, will use default)

5. **Deploy**: Click "Create Web Service"

## Automatic Test Account Creation

The app automatically creates test accounts on deployment for easy testing:

### 🔑 Test Login Credentials

**Administrator Account:**
- Email: `admin@eventhub.com`
- Password: `Admin@123`
- Access: Full system administration

**Organizer Account:**
- Email: `organizer@eventhub.com`
- Password: `Organizer@123`
- Access: Create/manage events, venues, speakers

**Buyer/Attendee Account:**
- Email: `buyer@eventhub.com`
- Password: `Buyer@123`
- Access: Browse events, book tickets

These credentials are displayed on the login page with convenient "Use These" buttons for quick testing.

## Important Notes

- The app uses SQLite database which will be created automatically on first run
- Test accounts are created automatically during deployment
- Database file is stored in the `/opt/render/project/src/instance/` directory on Render
- **⚠️ Change these passwords immediately in production!**

## Post-Deployment Testing

1. Visit your deployed app URL
2. Click on any "Use These" button on the login page
3. Test different user roles:
   - **Admin**: Manage all users and system settings
   - **Organizer**: Create events, manage venues and speakers
   - **Buyer**: Browse events and book tickets

## Local Development

To run locally with test accounts:
```bash
pip install -r requirements.txt
python create_admin_users.py  # Creates test accounts
python app.py
```

The app will be available at `http://localhost:5000`

## Troubleshooting

- Check Render logs if deployment fails
- Ensure all environment variables are set correctly
- Verify the start command is `python start.py`
- Make sure the build command is `pip install -r requirements.txt`
- Test accounts are created automatically - no manual setup needed