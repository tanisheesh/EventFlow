-- SQLite Schema for EventHub Application

-- Drop existing tables in reverse order of dependency (if re-creating)
DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Ticket;
DROP TABLE IF EXISTS "Order"; -- Use quotes for reserved keyword in SQLite
DROP TABLE IF EXISTS Speaker;
DROP TABLE IF EXISTS TicketType;
DROP TABLE IF EXISTS Event;
DROP TABLE IF EXISTS Venue;
DROP TABLE IF EXISTS User;

-- Create User table
CREATE TABLE User (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL, -- Store hashed passwords
  user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('organizer', 'attendee', 'administrator'))
);

-- Create Venue table
CREATE TABLE Venue (
  venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(255) NOT NULL,
  address TEXT,
  capacity INTEGER,
  city VARCHAR(255),
  state VARCHAR(255),
  zip_code VARCHAR(255)
);

-- Create Event table
CREATE TABLE Event (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  date DATE NOT NULL,
  time TIME,
  location_id INTEGER NOT NULL,
  FOREIGN KEY (location_id) REFERENCES Venue(venue_id)
);

-- Create Order table
CREATE TABLE "Order" (
  order_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  date DATETIME NOT NULL,
  total_price DECIMAL(10,2) NOT NULL,
  payment_id INTEGER,
  FOREIGN KEY (user_id) REFERENCES User(user_id),
  FOREIGN KEY (payment_id) REFERENCES Payment(payment_id)
);

-- Create Payment table
CREATE TABLE Payment (
  payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL UNIQUE,
  payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('credit card', 'paypal', 'other')),
  transaction_id VARCHAR(255),
  FOREIGN KEY (order_id) REFERENCES "Order"(order_id)
);

-- Create Ticket table
CREATE TABLE Ticket (
  ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id INTEGER NOT NULL,
  order_id INTEGER NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  type VARCHAR(50) NOT NULL,
  seat_number INTEGER,
  FOREIGN KEY (event_id) REFERENCES Event(event_id),
  FOREIGN KEY (order_id) REFERENCES "Order"(order_id)
);

-- Create Speaker table
CREATE TABLE Speaker (
  speaker_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(255) NOT NULL,
  bio TEXT,
  event_id INTEGER NOT NULL,
  FOREIGN KEY (event_id) REFERENCES Event(event_id)
);

-- Create TicketType table
CREATE TABLE TicketType (
  ticket_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id INTEGER NOT NULL,
  type VARCHAR(50) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  quantity INTEGER NOT NULL,
  FOREIGN KEY (event_id) REFERENCES Event(event_id)
);

-- Create indexes for better performance
CREATE INDEX idx_user_email ON User(email);
CREATE INDEX idx_event_date ON Event(date);
CREATE INDEX idx_order_user ON "Order"(user_id);
CREATE INDEX idx_ticket_event ON Ticket(event_id);
CREATE INDEX idx_ticket_order ON Ticket(order_id);
CREATE INDEX idx_speaker_event ON Speaker(event_id);
CREATE INDEX idx_tickettype_event ON TicketType(event_id);