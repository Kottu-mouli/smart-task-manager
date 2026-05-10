"""
Smart Task Management System - Main Application
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from database import db, User, Task
from analytics import get_analytics
from datetime import datetime

# ─────────────────────────────────────────────
# App Configuration
# ─────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://taskuser:taskpassword@localhost:5432/taskdb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
# ─────────────────────────────────────────────
# Auth Decorator
# ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Unauthorized. Please login.'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
# Page Routes
# ─────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register')
def register_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=user.username)


# ─────────────────────────────────────────────
# Auth API Routes
# ─────────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email    = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered.'}), 409

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken.'}), 409

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registration successful! Please login.'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email    = data.get('email', '').strip()
    password = data.get('password', '').strip()

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    session['user_id']  = user.id
    session['username'] = user.username
    return jsonify({'message': 'Login successful!', 'username': user.username}), 200


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully.'}), 200


# ─────────────────────────────────────────────
# Task REST API Routes
# ─────────────────────────────────────────────
@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=session['user_id']).order_by(Task.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@app.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    data = request.get_json()
    title       = data.get('title', '').strip()
    description = data.get('description', '').strip()
    priority    = data.get('priority', 'medium')
    status      = data.get('status', 'pending')

    if not title:
        return jsonify({'error': 'Title is required.'}), 400

    if priority not in ('low', 'medium', 'high'):
        return jsonify({'error': 'Priority must be low, medium, or high.'}), 400

    if status not in ('pending', 'in_progress', 'completed'):
        return jsonify({'error': 'Invalid status value.'}), 400

    task = Task(
        title=title,
        description=description,
        priority=priority,
        status=status,
        user_id=session['user_id']
    )
    db.session.add(task)
    db.session.commit()

    # Emit real-time WebSocket event
    socketio.emit('task_added', task.to_dict(), room=None)

    return jsonify({'message': 'Task added!', 'task': task.to_dict()}), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if not task:
        return jsonify({'error': 'Task not found.'}), 404

    data = request.get_json()
    task.title       = data.get('title', task.title).strip()
    task.description = data.get('description', task.description).strip()
    task.priority    = data.get('priority', task.priority)
    task.status      = data.get('status', task.status)
    db.session.commit()

    socketio.emit('task_updated', task.to_dict(), room=None)
    return jsonify({'message': 'Task updated!', 'task': task.to_dict()}), 200


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if not task:
        return jsonify({'error': 'Task not found.'}), 404

    db.session.delete(task)
    db.session.commit()

    socketio.emit('task_deleted', {'id': task_id}, room=None)
    return jsonify({'message': 'Task deleted!'}), 200


# ─────────────────────────────────────────────
# Analytics API Route
# ─────────────────────────────────────────────
@app.route('/api/analytics', methods=['GET'])
@login_required
def analytics():
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    data  = get_analytics([t.to_dict() for t in tasks])
    return jsonify(data), 200


# ─────────────────────────────────────────────
# WebSocket Events
# ─────────────────────────────────────────────
@socketio.on('connect')
def on_connect():
    emit('connected', {'message': 'WebSocket connected!'})

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected')


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database tables created.")
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)