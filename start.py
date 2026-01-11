#!/usr/bin/env python3
"""
Simple startup script for Render deployment.
This ensures the database is initialized and test users are created before starting the app.
"""
import os
from app import app, db
from create_admin_users import create_admin_users

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Create test users for demo purposes
        create_admin_users()
    
    # Start the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)