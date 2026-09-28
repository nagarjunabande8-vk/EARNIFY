from functools import wraps

import pymysql
from flask import Flask, flash, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config

app = Flask(__name__)
app.config.from_object(Config)


def get_db():
    """New MySQL connection per request-scoped call."""
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


mongo_client = MongoClient(app.config['MONGO_URI'])
mongo_db = mongo_client.get_default_database()
profiles_collection = mongo_db.profiles


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get('role') != role:
                flash('You do not have access to that page.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapper
    return decorator


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role')

        if role not in ('client', 'freelancer'):
            flash('Choose whether you are hiring or freelancing.', 'error')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('signup', role=role))

        db = get_db()
        with db.cursor() as cur:
            cur.execute('SELECT id FROM users WHERE email = %s', (email,))
            if cur.fetchone():
                flash('An account with that email already exists.', 'error')
                return redirect(url_for('signup', role=role))

            cur.execute(
                'INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)',
                (name, email, generate_password_hash(password), role),
            )
            user_id = cur.lastrowid

        if role == 'freelancer':
            profiles_collection.insert_one({
                'user_id': user_id,
                'bio': '',
                'skills': [],
                'portfolio_links': [],
                'hourly_rate': None,
            })

        session['user_id'] = user_id
        session['name'] = name
        session['role'] = role
        return redirect(url_for('dashboard'))

    preselected_role = request.args.get('role', 'freelancer')
    if preselected_role not in ('client', 'freelancer'):
        preselected_role = 'freelancer'
    return render_template('signup.html', preselected_role=preselected_role)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        db = get_db()
        with db.cursor() as cur:
            cur.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cur.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))

        flash('Incorrect email or password.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ---------------------------------------------------------------------------
# Dashboards
# ---------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    if session['role'] == 'client':
        return redirect(url_for('client_dashboard'))
    return redirect(url_for('freelancer_dashboard'))


@app.route('/dashboard/client')
@login_required
@role_required('client')
def client_dashboard():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            'SELECT * FROM jobs WHERE client_id = %s ORDER BY created_at DESC',
            (session['user_id'],),
        )
        jobs = cur.fetchall()
    return render_template('dashboard_client.html', jobs=jobs)


@app.route('/dashboard/freelancer')
@login_required
@role_required('freelancer')
def freelancer_dashboard():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            '''SELECT a.*, j.title, j.budget FROM applications a
               JOIN jobs j ON a.job_id = j.id
               WHERE a.freelancer_id = %s
               ORDER BY a.applied_at DESC''',
            (session['user_id'],),
        )
        applications = cur.fetchall()
    return render_template('dashboard_freelancer.html', applications=applications)



@app.route('/jobs')
@login_required
def jobs():
    category = request.args.get('category', '')
    search = request.args.get('q', '')

    query = (
        "SELECT j.*, u.name AS client_name FROM jobs j "
        "JOIN users u ON j.client_id = u.id WHERE j.status = 'open'"
    )
    params = []
    if category:
        query += ' AND j.category = %s'
        params.append(category)
    if search:
        query += ' AND (j.title LIKE %s OR j.description LIKE %s)'
        params.extend([f'%{search}%', f'%{search}%'])
    query += ' ORDER BY j.created_at DESC'

    db = get_db()
    with db.cursor() as cur:
        cur.execute(query, params)
        job_list = cur.fetchall()
    return render_template('jobs.html', jobs=job_list, category=category, search=search)


@app.route('/jobs/new', methods=['GET', 'POST'])
@login_required
@role_required('client')
def new_job():
    if request.method == 'POST':
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                '''INSERT INTO jobs
                   (client_id, title, description, budget, category, skills_required, deadline)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (
                    session['user_id'],
                    request.form['title'],
                    request.form['description'],
                    request.form['budget'],
                    request.form['category'],
                    request.form.get('skills_required', ''),
                    request.form.get('deadline') or None,
                ),
            )
        flash('Job posted.', 'success')
        return redirect(url_for('client_dashboard'))
    return render_template('post_job.html')


@app.route('/jobs/<int:job_id>')
@login_required
def job_detail(job_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            '''SELECT j.*, u.name AS client_name FROM jobs j
               JOIN users u ON j.client_id = u.id
               WHERE j.id = %s''',
            (job_id,),
        )
        job = cur.fetchone()

        already_applied = False
        if job and session.get('role') == 'freelancer':
            cur.execute(
                'SELECT id FROM applications WHERE job_id = %s AND freelancer_id = %s',
                (job_id, session['user_id']),
            )
            already_applied = cur.fetchone() is not None

    if not job:
        flash('That job could not be found.', 'error')
        return redirect(url_for('jobs'))

    return render_template('job_detail.html', job=job, already_applied=already_applied)


@app.route('/jobs/<int:job_id>/apply', methods=['POST'])
@login_required
@role_required('freelancer')
def apply_to_job(job_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            'SELECT id FROM applications WHERE job_id = %s AND freelancer_id = %s',
            (job_id, session['user_id']),
        )
        if cur.fetchone():
            flash('You already applied to this job.', 'error')
            return redirect(url_for('job_detail', job_id=job_id))

        cur.execute(
            '''INSERT INTO applications (job_id, freelancer_id, cover_letter, proposed_rate)
               VALUES (%s, %s, %s, %s)''',
            (
                job_id,
                session['user_id'],
                request.form['cover_letter'],
                request.form['proposed_rate'],
            ),
        )
    flash('Application submitted.', 'success')
    return redirect(url_for('job_detail', job_id=job_id))


@app.route('/jobs/<int:job_id>/applicants')
@login_required
@role_required('client')
def view_applicants(job_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            'SELECT * FROM jobs WHERE id = %s AND client_id = %s',
            (job_id, session['user_id']),
        )
        job = cur.fetchone()
        if not job:
            flash('That job could not be found.', 'error')
            return redirect(url_for('client_dashboard'))

        cur.execute(
            '''SELECT a.*, u.name AS freelancer_name, u.email AS freelancer_email
               FROM applications a JOIN users u ON a.freelancer_id = u.id
               WHERE a.job_id = %s ORDER BY a.applied_at DESC''',
            (job_id,),
        )
        applicants = cur.fetchall()

    return render_template('applicants.html', job=job, applicants=applicants)


@app.route('/applications/<int:app_id>/status', methods=['POST'])
@login_required
@role_required('client')
def update_application_status(app_id):
    new_status = request.form['status']
    if new_status not in ('accepted', 'rejected'):
        flash('Invalid status.', 'error')
        return redirect(request.referrer or url_for('client_dashboard'))

    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            '''UPDATE applications a
               JOIN jobs j ON a.job_id = j.id
               SET a.status = %s
               WHERE a.id = %s AND j.client_id = %s''',
            (new_status, app_id, session['user_id']),
        )

    flash(f'Application {new_status}.', 'success')
    return redirect(request.referrer or url_for('client_dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
