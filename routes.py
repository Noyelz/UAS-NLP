import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import User, HealthRecord
from services import process_audio_with_gemini

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('main.register'))
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('main.dashboard'))
        
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.created_at.desc()).all()
    return render_template('dashboard.html', records=records)

@main_bp.route('/api/process_audio', methods=['POST'])
@login_required
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    # Save temporarily
    filename = secure_filename(f"temp_{current_user.id}_{audio_file.filename}")
    filepath = os.path.join('static', 'uploads', filename)
    
    # Ensure uploads dir exists
    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
    
    audio_file.save(filepath)
    
    # Debug: Check file size
    file_size = os.path.getsize(filepath)
    print(f"Uploaded file: {filepath}, Size: {file_size} bytes")
    
    if file_size < 100: # If file is too small (e.g. empty)
        return jsonify({'error': 'Audio file is too short or empty'}), 400
    
    # Process with Gemini
    result = process_audio_with_gemini(filepath)
    
    # Clean up temp file
    if os.path.exists(filepath):
        os.remove(filepath)
        
    # Save record
    # Note: result is expected to be a string or JSON string from Gemini
    new_record = HealthRecord(user_id=current_user.id, raw_text="Audio processed", summary=str(result))
    db.session.add(new_record)
    db.session.commit()
    
    return jsonify({'success': True, 'data': result})
