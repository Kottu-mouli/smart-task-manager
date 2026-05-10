"""
database.py - SQLAlchemy Models for User and Task
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """User model - stores registered users."""
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: one user → many tasks
    tasks = db.relationship('Task', backref='owner', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    """Task model - stores tasks belonging to users."""
    __tablename__ = 'tasks'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    # low | medium | high
    priority    = db.Column(db.String(20), default='medium', nullable=False)
    # pending | in_progress | completed
    status      = db.Column(db.String(30), default='pending', nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        """Serialize task to dictionary for JSON responses."""
        return {
            'id':          self.id,
            'title':       self.title,
            'description': self.description,
            'priority':    self.priority,
            'status':      self.status,
            'created_at':  self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id':     self.user_id,
        }

    def __repr__(self):
        return f'<Task {self.title} [{self.status}]>'
