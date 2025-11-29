import os
import json
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import User, Transcript
from services import process_transcription
import io

main_bp = Blueprint('main', __name__)

# --- Helpers ---
def role_required(roles):
    def decorator(f):
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('main.login'))
            if current_user.role not in roles:
                flash('Akses ditolak. Anda tidak memiliki izin.')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

# --- Public Routes ---
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin_i':
            return redirect(url_for('main.transcription'))
        else:
            return redirect(url_for('main.admin_dashboard'))
    return render_template('index.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('main.register'))
        
        # Default role is admin_i (set in model)
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('main.transcription'))
        
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# --- Transcription Routes (Admin I) ---
@main_bp.route('/transcription', methods=['GET'])
@login_required
def transcription():
    return render_template('transcription.html')

@main_bp.route('/api/transcribe', methods=['POST'])
@login_required
def api_transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio provided'}), 400
        
    audio_file = request.files['audio']
    
    # Metadata
    metadata = {
        'participant_code': request.form.get('participant_code'),
        'participant_name': request.form.get('participant_name'),
        'participant_age': request.form.get('participant_age'),
        'participant_education': request.form.get('participant_education')
    }
    
    # Save temp
    filename = secure_filename(f"{current_user.id}_{audio_file.filename}")
    filepath = os.path.join('static', 'uploads', filename)
    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
    audio_file.save(filepath)
    
    # Process
    result = process_transcription(filepath)
    
    # Cleanup
    if os.path.exists(filepath):
        os.remove(filepath)
        
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
        
    # Save to DB
    new_transcript = Transcript(
        user_id=current_user.id,
        filename=audio_file.filename,
        participant_code=metadata['participant_code'],
        participant_name=metadata['participant_name'],
        participant_age=metadata['participant_age'],
        participant_education=metadata['participant_education'],
        content=result['content']
    )
    db.session.add(new_transcript)
    db.session.commit()
    
    return jsonify({'success': True, 'content': result['content']})

# --- Admin Routes (Admin II & III) ---
@main_bp.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role == 'admin_i':
        flash('Akses ditolak.')
        return redirect(url_for('main.transcription'))
        
    # Admin II & III can see transcripts
    transcripts = Transcript.query.order_by(Transcript.created_at.desc()).all()
    
    # Only Admin III can see users
    users = []
    if current_user.role == 'admin_iii':
        users = User.query.all()
        
    return render_template('admin_dashboard.html', transcripts=transcripts, users=users)

@main_bp.route('/admin/upgrade/<int:user_id>', methods=['POST'])
@login_required
def upgrade_user(user_id):
    if current_user.role != 'admin_iii':
        return jsonify({'error': 'Unauthorized'}), 403
        
    user = User.query.get_or_404(user_id)
    if user.role == 'admin_i':
        user.role = 'admin_ii'
        db.session.commit()
        flash(f'User {user.username} upgraded to Admin Boss.')
    
    return redirect(url_for('main.admin_dashboard'))

@main_bp.route('/admin/download/<int:transcript_id>')
@login_required
def download_transcript(transcript_id):
    if current_user.role == 'admin_i':
        # Admin I can only download their own? Or strictly no access?
        # Requirement says Admin Boss can download all. Admin I creates.
        # Let's restrict to Admin II/III for now based on requirement "Admin Boss bisa download transkrip semuanya"
        flash('Akses ditolak.')
        return redirect(url_for('main.transcription'))
        
    transcript = Transcript.query.get_or_404(transcript_id)
    
    # Create text file
    output = f"""TRANSKRIP WAWANCARA
    
Kode Partisipan: {transcript.participant_code}
Nama: {transcript.participant_name}
Usia: {transcript.participant_age}
Pendidikan: {transcript.participant_education}
Waktu: {transcript.created_at}
Oleh: {transcript.user.username}

------------------------------------------------

{transcript.content}
"""
    
    mem = io.BytesIO()
    mem.write(output.encode('utf-8'))
    mem.seek(0)
    
    return send_file(
        mem,
        as_attachment=True,
        download_name=f"transcript_{transcript.participant_code}.txt",
        mimetype='text/plain'
    )

# --- Profile Routes ---
@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        
        if new_username:
            # Check unique
            existing = User.query.filter_by(username=new_username).first()
            if existing and existing.id != current_user.id:
                flash('Username already taken.')
            else:
                current_user.username = new_username
                
        if new_password:
            current_user.set_password(new_password)
            
        db.session.commit()
        flash('Profil berhasil diperbarui.')
        
    return render_template('profile.html')
