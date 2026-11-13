from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for

from config import Config
from models import Application, Job, Profile, User, db

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    featured_jobs = (
        Job.query
        .filter_by(status='open')
        .order_by(Job.created_at.desc())
        .limit(6)
        .all()
    )
    total_jobs = Job.query.filter_by(status='open').count()
    total_freelancers = User.query.filter_by(role='freelancer').count()
    total_clients = User.query.filter_by(role='client').count()
    stats = {
        'jobs': total_jobs,
        'freelancers': total_freelancers,
        'clients': total_clients,
    }
    return render_template('index.html', featured_jobs=featured_jobs, stats=stats)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

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

        if User.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'error')
            return redirect(url_for('signup', role=role))

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if role == 'freelancer':
            profile = Profile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()

        session['user_id'] = user.id
        session['name'] = user.name
        session['role'] = user.role
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

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['name'] = user.name
            session['role'] = user.role
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
    jobs = (
        Job.query
        .filter_by(client_id=session['user_id'])
        .order_by(Job.created_at.desc())
        .all()
    )

    total_applicants = 0
    accepted_count = 0
    pending_count = 0
    for job in jobs:
        for a in job.applications:
            total_applicants += 1
            if a.status == 'accepted':
                accepted_count += 1
            elif a.status == 'pending':
                pending_count += 1

    stats = {
        'active_jobs': len([j for j in jobs if j.status == 'open']),
        'total_applicants': total_applicants,
        'accepted': accepted_count,
        'pending': pending_count,
    }
    return render_template('dashboard_client.html', jobs=jobs, stats=stats)


@app.route('/dashboard/freelancer')
@login_required
@role_required('freelancer')
def freelancer_dashboard():
    applications = (
        Application.query
        .filter_by(freelancer_id=session['user_id'])
        .order_by(Application.applied_at.desc())
        .all()
    )

    accepted_count = sum(1 for a in applications if a.status == 'accepted')
    pending_count = sum(1 for a in applications if a.status == 'pending')
    rejected_count = sum(1 for a in applications if a.status == 'rejected')

    stats = {
        'total': len(applications),
        'accepted': accepted_count,
        'pending': pending_count,
        'rejected': rejected_count,
    }

    recommended_jobs = (
        Job.query
        .filter_by(status='open')
        .order_by(Job.created_at.desc())
        .limit(3)
        .all()
    )

    return render_template(
        'dashboard_freelancer.html',
        applications=applications,
        stats=stats,
        recommended_jobs=recommended_jobs,
    )


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

@app.route('/jobs')
@login_required
def jobs():
    category = request.args.get('category', '')
    search = request.args.get('q', '')
    sort = request.args.get('sort', 'newest')

    query = Job.query.filter_by(status='open')

    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(
            db.or_(
                Job.title.ilike(f'%{search}%'),
                Job.description.ilike(f'%{search}%'),
            )
        )

    if sort == 'budget_high':
        query = query.order_by(Job.budget.desc())
    elif sort == 'budget_low':
        query = query.order_by(Job.budget.asc())
    else:
        query = query.order_by(Job.created_at.desc())

    job_list = query.all()

    categories = [
        'Web Development', 'Python Development', 'UI/UX Design',
        'Graphic Design', 'Content Writing', 'Digital Marketing',
        'Data Entry', 'Mobile App Development',
    ]

    return render_template(
        'jobs.html',
        jobs=job_list,
        categories=categories,
        category=category,
        search=search,
        sort=sort,
        total=len(job_list),
    )


@app.route('/jobs/new', methods=['GET', 'POST'])
@login_required
@role_required('client')
def new_job():
    if request.method == 'POST':
        deadline = request.form.get('deadline') or None
        if deadline:
            from datetime import date as date_type
            try:
                deadline = date_type.fromisoformat(deadline)
            except ValueError:
                deadline = None

        job = Job(
            client_id=session['user_id'],
            title=request.form['title'],
            description=request.form['description'],
            budget=float(request.form['budget']),
            category=request.form['category'],
            skills_required=request.form.get('skills_required', ''),
            deadline=deadline,
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('client_dashboard'))

    categories = [
        'Web Development', 'Python Development', 'UI/UX Design',
        'Graphic Design', 'Content Writing', 'Digital Marketing',
        'Data Entry', 'Mobile App Development',
    ]
    return render_template('post_job.html', categories=categories)


@app.route('/jobs/<int:job_id>')
@login_required
def job_detail(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        flash('That job could not be found.', 'error')
        return redirect(url_for('jobs'))

    already_applied = False
    if session.get('role') == 'freelancer':
        already_applied = Application.query.filter_by(
            job_id=job_id, freelancer_id=session['user_id']
        ).first() is not None

    return render_template('job_detail.html', job=job, already_applied=already_applied)


@app.route('/jobs/<int:job_id>/apply', methods=['POST'])
@login_required
@role_required('freelancer')
def apply_to_job(job_id):
    existing = Application.query.filter_by(
        job_id=job_id, freelancer_id=session['user_id']
    ).first()
    if existing:
        flash('You already applied to this job.', 'error')
        return redirect(url_for('job_detail', job_id=job_id))

    application = Application(
        job_id=job_id,
        freelancer_id=session['user_id'],
        cover_letter=request.form['cover_letter'],
        proposed_rate=float(request.form['proposed_rate']),
    )
    db.session.add(application)
    db.session.commit()
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('job_detail', job_id=job_id))


@app.route('/jobs/<int:job_id>/applicants')
@login_required
@role_required('client')
def view_applicants(job_id):
    job = Job.query.filter_by(id=job_id, client_id=session['user_id']).first()
    if not job:
        flash('That job could not be found.', 'error')
        return redirect(url_for('client_dashboard'))

    applicants = (
        Application.query
        .filter_by(job_id=job_id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return render_template('applicants.html', job=job, applicants=applicants)


@app.route('/applications/<int:app_id>/status', methods=['POST'])
@login_required
@role_required('client')
def update_application_status(app_id):
    new_status = request.form['status']
    if new_status not in ('accepted', 'rejected'):
        flash('Invalid status.', 'error')
        return redirect(request.referrer or url_for('client_dashboard'))

    application = db.session.get(Application, app_id)
    if application and application.job.client_id == session['user_id']:
        application.status = new_status
        db.session.commit()
        flash(f'Application {new_status}.', 'success')
    else:
        flash('Application not found.', 'error')

    return redirect(request.referrer or url_for('client_dashboard'))


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@app.route('/profile')
@login_required
def my_profile():
    user = db.session.get(User, session['user_id'])
    profile = Profile.query.filter_by(user_id=session['user_id']).first()
    return render_template('profile.html', user=user, profile=profile)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    profile = Profile.query.filter_by(user_id=session['user_id']).first()
    if not profile:
        profile = Profile(user_id=session['user_id'])
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.bio = request.form.get('bio', '')
        profile.skills = request.form.get('skills', '')
        profile.hourly_rate = float(request.form['hourly_rate']) if request.form.get('hourly_rate') else None
        profile.github = request.form.get('github', '')
        profile.linkedin = request.form.get('linkedin', '')
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('my_profile'))

    return render_template('edit_profile.html', profile=profile)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
