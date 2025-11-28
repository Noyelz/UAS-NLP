import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import User, HealthRecord
from services import process_interview_step, generate_final_summary

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


# --- Interview Routes ---

INTERVIEW_QUESTIONS = [
    {
        "id": 1,
        "text": "Berapa suhu badan Anda saat ini? (Sebutkan angkanya jika tahu)",
        "key": "suhu_badan"
    },
    {
        "id": 2,
        "text": "Sudah berapa lama Anda mengalami batuk?",
        "key": "durasi_batuk"
    },
    {
        "id": 3,
        "text": "Apakah batuk Anda disertai dahak atau darah?",
        "key": "jenis_batuk"
    },
    {
        "id": 4,
        "text": "Apakah Anda mengalami penurunan berat badan yang drastis belakangan ini?",
        "key": "berat_badan"
    },
    {
        "id": 5,
        "text": "Apakah Anda sering berkeringat di malam hari meskipun tidak beraktivitas?",
        "key": "keringat_malam"
    }
]

@main_bp.route('/interview')
@login_required
def interview():
    return render_template('interview.html')



@main_bp.route('/api/interview/start', methods=['POST'])
@login_required
def start_interview():
    session['interview_answers'] = {}
    session['current_step'] = 1
    return jsonify({
        'step': 1,
        'total_steps': len(INTERVIEW_QUESTIONS),
        'question': INTERVIEW_QUESTIONS[0]
    })

@main_bp.route('/api/interview/step', methods=['POST'])
@login_required
def interview_step():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio provided'}), 400
        
    step_id = int(request.form.get('step_id', 1))
    audio_file = request.files['audio']
    
    # Validate step
    if step_id < 1 or step_id > len(INTERVIEW_QUESTIONS):
        return jsonify({'error': 'Invalid step'}), 400
        
    question_obj = INTERVIEW_QUESTIONS[step_id - 1]
    
    # Save temp
    filename = secure_filename(f"step_{step_id}_{current_user.id}_{audio_file.filename}")
    filepath = os.path.join('static', 'uploads', filename)
    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
    audio_file.save(filepath)
    
    # Process
    result = process_interview_step(filepath, question_obj['text'])
    print(f"Step result: {result}")
    
    # Cleanup
    if os.path.exists(filepath):
        os.remove(filepath)
        
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
        
    # Store answer
    if 'interview_answers' not in session:
        session['interview_answers'] = {}
    
    # We need to re-assign session dict to ensure it saves
    answers = session['interview_answers']
    answers[question_obj['key']] = result['text']
    session['interview_answers'] = answers
    
    # Determine next
    next_step = step_id + 1
    if next_step > len(INTERVIEW_QUESTIONS):
        return jsonify({
            'finished': True,
            'answer_text': result['text']
        })
    else:
        return jsonify({
            'finished': False,
            'next_step': next_step,
            'next_question': INTERVIEW_QUESTIONS[next_step - 1],
            'answer_text': result['text']
        })

@main_bp.route('/api/interview/finish', methods=['POST'])
@login_required
def finish_interview():
    answers = session.get('interview_answers', {})
    if not answers:
        return jsonify({'error': 'No answers found'}), 400
        
    # Generate Summary
    summary_json = generate_final_summary(answers)
    
    # Save Record
    new_record = HealthRecord(
        user_id=current_user.id, 
        raw_text="TB Interview Checkup", 
        summary=str(summary_json) # Store as string representation of JSON
    )
    db.session.add(new_record)
    db.session.commit()
    
    # Clear session
    session.pop('interview_answers', None)
    session.pop('current_step', None)
    
    return jsonify({'success': True, 'data': summary_json})
