from app import app, db, User, hash_password
from datetime import datetime

def create_admin_users():
    with app.app_context():
        # Create administrator account
        admin = User(
            name="System Administrator",
            email="admin@eventhub.com",
            password=hash_password("Admin@123"),  # Strong password
            user_type="administrator"
        )

        # Create organizer account
        organizer = User(
            name="Event Organizer",
            email="organizer@eventhub.com",
            password=hash_password("Organizer@123"),  # Strong password
            user_type="organizer"
        )

        # Create attendee/buyer account
        attendee = User(
            name="Event Attendee",
            email="buyer@eventhub.com",
            password=hash_password("Buyer@123"),  # Strong password
            user_type="attendee"
        )

        try:
            # Check if users already exist
            existing_admin = User.query.filter_by(email="admin@eventhub.com").first()
            existing_organizer = User.query.filter_by(email="organizer@eventhub.com").first()
            existing_attendee = User.query.filter_by(email="buyer@eventhub.com").first()

            # Add users to database if they don't exist
            if not existing_admin:
                db.session.add(admin)
            if not existing_organizer:
                db.session.add(organizer)
            if not existing_attendee:
                db.session.add(attendee)
            
            db.session.commit()
            print("Successfully created test accounts!")
            print("\n=== TEST LOGIN CREDENTIALS ===")
            print("Administrator:")
            print("Email: admin@eventhub.com")
            print("Password: Admin@123")
            print("\nOrganizer:")
            print("Email: organizer@eventhub.com")
            print("Password: Organizer@123")
            print("\nBuyer/Attendee:")
            print("Email: buyer@eventhub.com")
            print("Password: Buyer@123")
            print("===============================")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating accounts: {e}")

if __name__ == "__main__":
    create_admin_users() 