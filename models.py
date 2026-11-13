from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'client' or 'freelancer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    jobs = db.relationship('Job', backref='client', lazy='select')
    applications = db.relationship('Application', backref='freelancer', lazy='select')
    profile = db.relationship('Profile', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name}>'


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))
    skills_required = db.Column(db.String(255))
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='open')  # 'open' or 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='job', lazy='select')

    @property
    def skills_list(self):
        if self.skills_required:
            return [s.strip() for s in self.skills_required.split(',') if s.strip()]
        return []

    def __repr__(self):
        return f'<Job {self.title}>'


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cover_letter = db.Column(db.Text)
    proposed_rate = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected'
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('job_id', 'freelancer_id', name='unique_application'),
    )

    def __repr__(self):
        return f'<Application {self.id}>'


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    bio = db.Column(db.Text, default='')
    skills = db.Column(db.String(500), default='')
    hourly_rate = db.Column(db.Float, nullable=True)
    github = db.Column(db.String(200), default='')
    linkedin = db.Column(db.String(200), default='')

    @property
    def skills_list(self):
        if self.skills:
            return [s.strip() for s in self.skills.split(',') if s.strip()]
        return []

    def __repr__(self):
        return f'<Profile user_id={self.user_id}>'
