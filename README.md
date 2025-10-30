Digital Certificate & Record Authentication System

📜 Project Overview

This project simulates a foundational concept of blockchain-based digital authentication for tamper-proof record-keeping, such as workshop participation certificates. The core idea is to leverage cryptographic hashing and the immutability of a ledger (simulated by a SQLite database) to verify that a digital record has not been altered since its issuance.

It serves as an excellent demonstration of immutability in practice: any change to the original certificate data results in a different hash, causing the verification check against the stored "ledger hash" to fail instantly.
<img width="1908" height="1002" alt="image" src="https://github.com/user-attachments/assets/3f742b82-39b6-4088-8080-9a229d1f39ad" />


Cryptography: Using SHA-256 hashing to create unique, fixed-length fingerprints of data.

Backend Development: Building a RESTful API using Python Flask.

Database Management: Utilizing SQLite and SQLAlchemy to manage a persistent, immutable ledger.

Frontend Interaction: Using vanilla JavaScript to interact with the API and visually present verification results.

💻 Technologies Used

Category

Technology

Purpose

Backend

Python 3

Core application logic.

Web Framework

Flask

Provides routing and web server capabilities.

API

Flask-RESTful

Simplifies the creation of RESTful API endpoints.

Database

SQLAlchemy + SQLite

Object-Relational Mapper (ORM) for managing the certificate ledger.

Frontend

HTML5, JavaScript

Single-page user interface for issuance and verification.

Styling

Tailwind CSS

Utility-first CSS framework for a responsive, modern interface.

📁 Installation and Setup

Prerequisites

You need Python 3 installed on your system.

Clone the repository:

git clone [YOUR-REPO-URL]
cd digital-certificate-auth


Install Python dependencies:

pip install Flask Flask-SQLAlchemy Flask-RESTful


Running the Application

Ensure both app.py and certificate_auth.html are in the same directory.

Run the Flask server from your terminal:

python app.py


The application will automatically create the certificate_ledger.db file upon the first run.

Open your web browser and navigate to the address displayed by Flask (usually http://127.0.0.1:5000/).

🚀 How It Works

The system operates in two phases:

1. Issuance (The Smart Contract)

The user enters the recipient name, course name, date, and issuer name.

The backend (app.py) takes these fields, orders them consistently, converts them to lowercase, and generates a SHA-256 hash.

This unique data hash is stored permanently on the CertificateHash table (the simulated ledger) along with a newly generated certificate_id.

The user is given the certificate_id and the original data.

2. Verification (The Immutability Check)

The verifier provides the certificate_id and the current certificate data (which might have been tampered with).

The backend retrieves the original hash from the ledger using the certificate_id.

The backend re-hashes the provided current data using the exact same hashing function.

The two hashes are compared:

If New Hash == Ledger Hash, the certificate is Authentic.

If New Hash != Ledger Hash, the certificate is Tampered or Invalid.

The frontend includes a "Simulate Tampering" button to demonstrate this process: clicking it changes the recipient's name in the verification form, which is enough to completely change the hash, thus failing the verification check.

🛠️ Project Files

app.py: The Flask backend, containing database configuration, SQLAlchemy model definition, the generate_certificate_hash utility, and the RESTful resources (/api/issue and /api/verify).

certificate_auth.html: The single-file frontend with Tailwind CSS and JavaScript for API interaction.

certificate_ledger.db: (Auto-generated) The SQLite database file serving as the immutable certificate ledger.

🌐 Deployed Smart Contract
Network: Celo Sepolia Testnet
Contract Address: 0x6b4640a625afde062f8af818dd2d353589599c39

You can view all transactions, balances, and events on Blockscout using the link above.
