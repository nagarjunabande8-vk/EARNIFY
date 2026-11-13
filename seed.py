"""Seed the database with sample users and jobs."""

from app import app, db
from models import Application, Job, Profile, User


SAMPLE_PASSWORD = 'password123'

USERS = [
    ('Aditi Rao', 'aditi@example.com', 'client'),
    ('Rohit Sharma', 'rohit@example.com', 'client'),
    ('Priya Nair', 'priya@example.com', 'freelancer'),
    ('Sameer Khan', 'sameer@example.com', 'freelancer'),
    ('Ananya Singh', 'ananya@example.com', 'freelancer'),
    ('Vikram Patel', 'vikram@example.com', 'client'),
]

JOBS = [
    {
        'client_email': 'aditi@example.com',
        'title': 'Build a Responsive Landing Page',
        'description': 'Need a modern, responsive landing page for a SaaS product launch. Must include hero section, features grid, pricing table, testimonials, and a contact form. Clean code with semantic HTML5, CSS3 animations, and mobile-first approach.',
        'budget': 8000,
        'category': 'Web Development',
        'skills': 'HTML, CSS, JavaScript, Responsive Design',
    },
    {
        'client_email': 'aditi@example.com',
        'title': 'Python Data Analysis Dashboard',
        'description': 'Create a data analysis dashboard using Python, Pandas, and Matplotlib. The dashboard should read CSV data, generate interactive charts, and export PDF reports. Clean, well-documented code required.',
        'budget': 12000,
        'category': 'Python Development',
        'skills': 'Python, Pandas, Matplotlib, Data Analysis',
    },
    {
        'client_email': 'rohit@example.com',
        'title': 'Logo and Brand Identity for Bakery',
        'description': 'Looking for a warm, hand-drawn style logo plus a complete brand identity guide including color palette, typography, and usage guidelines for a new artisan bakery brand.',
        'budget': 5000,
        'category': 'Graphic Design',
        'skills': 'Illustrator, Photoshop, Branding, Logo Design',
    },
    {
        'client_email': 'rohit@example.com',
        'title': 'UI/UX Design for Mobile Banking App',
        'description': 'Design complete UI/UX for a mobile banking application. Deliverables include user research findings, wireframes, high-fidelity mockups in Figma, and a clickable prototype. Must follow accessibility guidelines.',
        'budget': 15000,
        'category': 'UI/UX Design',
        'skills': 'Figma, UI Design, UX Research, Prototyping',
    },
    {
        'client_email': 'vikram@example.com',
        'title': 'SEO Blog Articles for Tech Startup',
        'description': 'Write 10 SEO-optimized blog articles (1500+ words each) for a B2B tech startup. Topics include cloud computing, AI trends, and cybersecurity. Must include keyword research and meta descriptions.',
        'budget': 6000,
        'category': 'Content Writing',
        'skills': 'SEO Writing, Blog Writing, Research, Copywriting',
    },
    {
        'client_email': 'vikram@example.com',
        'title': 'Social Media Marketing Campaign',
        'description': 'Plan and execute a 30-day social media marketing campaign across Instagram, LinkedIn, and Twitter for a fintech product launch. Deliverables include content calendar, post designs, and analytics report.',
        'budget': 10000,
        'category': 'Digital Marketing',
        'skills': 'Social Media, Content Strategy, Canva, Analytics',
    },
    {
        'client_email': 'aditi@example.com',
        'title': 'Data Entry and CRM Migration',
        'description': 'Migrate 5000+ customer records from spreadsheets into a new CRM system. Clean and validate data, remove duplicates, and ensure all fields are correctly mapped. Attention to detail is critical.',
        'budget': 3000,
        'category': 'Data Entry',
        'skills': 'Excel, Data Entry, CRM, Data Cleaning',
    },
    {
        'client_email': 'rohit@example.com',
        'title': 'Cross-Platform Mobile App with Flutter',
        'description': 'Build a cross-platform mobile app for a food delivery startup using Flutter. Features include user authentication, restaurant listing, cart management, order tracking, and push notifications.',
        'budget': 25000,
        'category': 'Mobile App Development',
        'skills': 'Flutter, Dart, Firebase, REST API',
    },
]


def seed():
    with app.app_context():
        user_map = {}
        for name, email, role in USERS:
            existing = User.query.filter_by(email=email).first()
            if existing:
                user_map[email] = existing
                continue

            user = User(name=name, email=email, role=role)
            user.set_password(SAMPLE_PASSWORD)
            db.session.add(user)
            db.session.flush()

            if role == 'freelancer':
                profile = Profile(user_id=user.id, bio=f'Hi, I am {name}. Passionate freelancer.')
                db.session.add(profile)

            user_map[email] = user

        for j in JOBS:
            client = user_map[j['client_email']]
            existing = Job.query.filter_by(client_id=client.id, title=j['title']).first()
            if existing:
                continue

            job = Job(
                client_id=client.id,
                title=j['title'],
                description=j['description'],
                budget=j['budget'],
                category=j['category'],
                skills_required=j['skills'],
            )
            db.session.add(job)

        db.session.commit()

        print('Seed data ready.')
        print(f'Client login:     aditi@example.com / {SAMPLE_PASSWORD}')
        print(f'Freelancer login: priya@example.com / {SAMPLE_PASSWORD}')


if __name__ == '__main__':
    seed()
