"""End-to-end smoke test: the main flow of every role, against a throwaway
SQLite database. Runs in CI, so dependency updates that only break at run
time (not at import) are caught before they are merged."""
import os
import tempfile

_db_file = os.path.join(tempfile.mkdtemp(), "smoke.db")
os.environ["DATABASE_URL"] = "sqlite:///" + _db_file.replace(os.sep, "/")
os.environ["SECRET_KEY"] = "test"
os.environ["REQLY_SAMPLE_RATE"] = "0"  # no events sent to a collector

import pytest

from app import Event, Order, Ticket, TicketType, User, Venue, app, db
from create_admin_users import create_admin_users


@pytest.fixture(scope="module")
def client():
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
    create_admin_users()
    return app.test_client()


def login(client, email, password):
    client.get("/logout")
    return client.post("/login", data={"email": email, "password": password})


def test_public_pages(client):
    for path in ("/", "/events", "/login", "/signup"):
        assert client.get(path).status_code == 200


def test_signup_always_creates_an_attendee(client):
    client.get("/logout")
    client.post("/signup", data={"name": "Eve", "email": "eve@example.com", "password": "pw",
                                 "confirm_password": "pw", "user_type": "administrator"})
    with app.app_context():
        assert User.query.filter_by(email="eve@example.com").one().user_type == "attendee"


def test_organizer_creates_event_and_attendee_books_and_cancels(client):
    login(client, "organizer@eventhub.com", "Organizer@123")
    assert client.get("/dashboard").status_code == 200
    client.post("/venues/create", data={"name": "Hall A", "capacity": "100", "city": "Pune"})
    with app.app_context():
        venue_id = Venue.query.filter_by(name="Hall A").one().venue_id
    client.post("/events/create", data={"name": "PyCon", "description": "talks", "date": "2030-01-15",
                                        "start_time": "10:00", "end_time": "17:00",
                                        "location_id": str(venue_id)})
    with app.app_context():
        event_id = Event.query.filter_by(name="PyCon").one().event_id
    client.post(f"/events/{event_id}/tickets/manage", data={"type": "General", "price": "25", "quantity": "10"})
    assert client.get(f"/events/{event_id}/tickets").status_code == 200

    login(client, "buyer@eventhub.com", "Buyer@123")
    assert client.get(f"/events/{event_id}").status_code == 200
    client.post(f"/book_ticket/{event_id}", data={"ticket_type": "General", "quantity": "2"})
    with app.app_context():
        assert TicketType.query.filter_by(event_id=event_id).one().quantity == 8
        ticket_id = Ticket.query.filter_by(event_id=event_id).first().ticket_id
    assert b"PyCon" in client.get("/my-tickets").data

    client.post(f"/tickets/{ticket_id}/cancel")
    with app.app_context():
        assert TicketType.query.filter_by(event_id=event_id).one().quantity == 9
        assert float(Order.query.one().total_price) == 25.0


def test_admin_manages_organizers(client):
    login(client, "admin@eventhub.com", "Admin@123")
    assert client.get("/").status_code == 200  # the admin nav renders
    page = client.get("/admin/organizers").data.decode()
    assert "organizer@eventhub.com" in page and "<td>1</td>" in page  # one event created
    with app.app_context():
        organizer_id = User.query.filter_by(email="organizer@eventhub.com").one().user_id
    client.post(f"/admin/organizers/{organizer_id}/delete")
    with app.app_context():
        assert User.query.get(organizer_id) is None
        assert Event.query.filter_by(name="PyCon").count() == 0


def test_roles_are_enforced(client):
    login(client, "buyer@eventhub.com", "Buyer@123")
    assert client.get("/dashboard").status_code == 302
    client.get("/logout")
    assert client.get("/my-tickets").status_code == 302
