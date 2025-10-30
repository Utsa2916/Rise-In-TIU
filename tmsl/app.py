import os
import hashlib
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

# --- Configuration ---
# Use a simple relative path for SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'certificate_ledger.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a_secure_random_key_for_session_management'

db = SQLAlchemy(app)
api = Api(app)

# --- Database Model (The Immutable Ledger/Blockchain) ---
# This model represents a 'block' on our ledger, storing the unique, tamper-proof hash.
class CertificateHash(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # The unique ID of the certificate, public to the recipient
    certificate_id = db.Column(db.String(36), unique=True, nullable=False)
    # The SHA-256 hash of the certificate data (the proof of authenticity)
    data_hash = db.Column(db.String(64), nullable=False)
    issuer_name = db.Column(db.String(100), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Cert {self.certificate_id}>'

# --- Utility Function ---
def generate_certificate_hash(data):
    """
    Generates a SHA-256 hash from ordered, core certificate data.
    The data must be ordered and consistent to produce the same hash every time.
    This simulates how a smart contract would hash the data before storing it.
    """
    # Keys must be consistent: recipient, course, date, issuer
    # We strip whitespace and convert to lower to ensure consistent hashing
    data_string = f"{data.get('recipient', '').strip().lower()}|" \
                  f"{data.get('course', '').strip().lower()}|" \
                  f"{data.get('date', '').strip()}|" \
                  f"{data.get('issuer', '').strip().lower()}"

    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

# --- API Resources (The Smart Contract Functions) ---

class IssueCertificate(Resource):
    """Handles issuing a new certificate and storing its hash on the ledger."""
    def post(self):
        try:
            data = request.get_json()
            if not all(k in data for k in ('recipient', 'course', 'date', 'issuer')):
                return {'message': 'Missing required fields: recipient, course, date, issuer'}, 400

            # 1. HASHING: Generate the unique, tamper-proof hash of the certificate data
            new_hash = generate_certificate_hash(data)
            
            # 2. LEDGER STORAGE (Simulation of Blockchain Immutability)
            # Generate a globally unique ID for the certificate
            cert_uuid = str(uuid.uuid4())

            new_record = CertificateHash(
                certificate_id=cert_uuid,
                data_hash=new_hash,
                issuer_name=data['issuer']
            )
            
            db.session.add(new_record)
            db.session.commit()
            
            return {
                'message': 'Certificate hash successfully issued and recorded on the ledger.',
                'certificate_id': cert_uuid,
                'recorded_hash': new_hash,
                'issued_to': data['recipient']
            }, 201
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'An error occurred during issuance: {str(e)}'}, 500

class VerifyCertificate(Resource):
    """Handles verifying a certificate hash against the ledger."""
    def post(self):
        try:
            data = request.get_json()
            cert_id = data.get('certificate_id')
            cert_data = data.get('certificate_data')

            if not cert_id or not cert_data:
                return {'message': 'Missing certificate_id or certificate_data.'}, 400
            
            if not all(k in cert_data for k in ('recipient', 'course', 'date', 'issuer')):
                return {'message': 'Certificate data provided is incomplete.'}, 400

            # 1. RETRIEVE LEDGER RECORD (Smart Contract Retrieval)
            ledger_record = CertificateHash.query.filter_by(certificate_id=cert_id).first()

            if not ledger_record:
                return {
                    'message': 'Certificate ID not found on the ledger.',
                    'authentic': False
                }, 404

            # 2. RE-HASHING (Verifier's side)
            # The verifier calculates the hash of the certificate they possess
            verifier_hash = generate_certificate_hash(cert_data)
            
            # 3. COMPARISON (The Immutability Check)
            stored_hash = ledger_record.data_hash

            if verifier_hash == stored_hash:
                return {
                    'message': 'VERIFIED: The certificate is authentic and has not been tampered with.',
                    'authentic': True,
                    'recorded_hash': stored_hash,
                    'verified_hash': verifier_hash,
                    'issued_at': ledger_record.issued_at.strftime("%Y-%m-%d %H:%M:%S")
                }, 200
            else:
                return {
                    'message': 'FAILED: The certificate data has been altered since issuance.',
                    'authentic': False,
                    'recorded_hash': stored_hash,
                    'verified_hash': verifier_hash
                }, 200

        except Exception as e:
            return {'message': f'An error occurred during verification: {str(e)}'}, 500

# --- API Route Setup ---
api.add_resource(IssueCertificate, '/api/issue')
api.add_resource(VerifyCertificate, '/api/verify')

# --- Frontend Route ---
@app.route('/')
def index():
    """Serves the main web interface (single HTML file)."""
    # NOTE: This assumes certificate_auth.html is in the same directory.
    try:
        # FIX: Explicitly specify 'utf-8' encoding to prevent UnicodeDecodeError
        with open(os.path.join(basedir, 'certificate_auth.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
        return render_template_string(html_content)
    except FileNotFoundError:
        return "Error: 'certificate_auth.html' not found. Please ensure it is in the same directory as 'app.py'.", 500


# --- Initialization ---
if __name__ == '__main__':
    # Create the database tables before running the app
    with app.app_context():
        db.create_all()
    print("Database tables created/checked.")
    
    # Run the application
    app.run(debug=True)