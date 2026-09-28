from werkzeug.security import generate_password_hash

from app import get_db, profiles_collection

SAMPLE_PASSWORD = 'password123'


def seed():
    db = get_db()
    with db.cursor() as cur:
        users = [
            ('Aditi Rao', 'aditi@example.com', 'client'),
            ('Rohit Sharma', 'rohit@example.com', 'client'),
            ('Priya Nair', 'priya@example.com', 'freelancer'),
            ('Sameer Khan', 'sameer@example.com', 'freelancer'),
        ]
        user_ids = {}
        for name, email, role in users:
            cur.execute('SELECT id FROM users WHERE email = %s', (email,))
            existing = cur.fetchone()
            if existing:
                user_ids[email] = existing['id']
                continue
            cur.execute(
                'INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)',
                (name, email, generate_password_hash(SAMPLE_PASSWORD), role),
            )
            user_ids[email] = cur.lastrowid
            if role == 'freelancer':
                profiles_collection.insert_one({
                    'user_id': cur.lastrowid,
                    'bio': '',
                    'skills': [],
                    'portfolio_links': [],
                    'hourly_rate': None,
                })

        jobs = [
            (
                user_ids['aditi@example.com'],
                'Build a landing page',
                'Need a responsive one-page site for a product launch, built with plain HTML/CSS/JS.',
                5000,
                'Web Development',
                'HTML, CSS, JavaScript',
            ),
            (
                user_ids['rohit@example.com'],
                'Logo for a bakery',
                'Looking for a warm, hand-drawn style logo plus a simple usage guide.',
                2000,
                'Design',
                'Illustrator, branding',
            ),
        ]
        for client_id, title, desc, budget, category, skills in jobs:
            cur.execute(
                'SELECT id FROM jobs WHERE client_id = %s AND title = %s',
                (client_id, title),
            )
            if cur.fetchone():
                continue
            cur.execute(
                '''INSERT INTO jobs (client_id, title, description, budget, category, skills_required)
                   VALUES (%s, %s, %s, %s, %s, %s)''',
                (client_id, title, desc, budget, category, skills),
            )

    print('Seed data ready.')
    print('Client login:     aditi@example.com / password123')
    print('Freelancer login: priya@example.com / password123')


if __name__ == '__main__':
    seed()
