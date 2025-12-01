from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin_i') # admin_i, admin_ii, admin_iii
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Transcript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    
    # Metadata fields
    participant_code = db.Column(db.String(50))
    participant_name = db.Column(db.String(100))
    participant_age = db.Column(db.String(20))
    participant_education = db.Column(db.String(50))
    
    content = db.Column(db.Text, nullable=True) # The dialogue
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('transcripts', lazy=True))

class TranscriptionTask(db.Model):
    id = db.Column(db.String(36), primary_key=True) # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='queued') # queued, processing, completed, failed
    progress = db.Column(db.Integer, default=0)
    message = db.Column(db.String(255), default='Menunggu antrian...')
    error = db.Column(db.Text, nullable=True)
    result_id = db.Column(db.Integer, db.ForeignKey('transcript.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))
    transcript = db.relationship('Transcript', backref=db.backref('task', uselist=False))
