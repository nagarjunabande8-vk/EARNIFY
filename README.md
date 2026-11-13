# Earnify

A full-stack freelancing platform connecting clients and freelancers —
job posting, browsing, and applications end to end.

- **Frontend:** HTML, CSS, JavaScript (server-rendered via Jinja2, no framework)
- **Backend:** Flask (Python) — routing, auth, business logic
- **Databases:** MySQL (users, jobs, applications) + MongoDB (freelancer portfolios)

## Why two databases

MySQL holds everything with a clear relational shape: a job belongs to a
client, an application belongs to a job and a freelancer. Those are
foreign-key relationships, so MySQL's joins and constraints do the work
(see `schema.sql`).

MongoDB holds freelancer portfolio data instead — bio, skills, portfolio
links, rate — which varies a lot from one freelancer to the next and
doesn't need fixed columns. A signup as a freelancer creates one document
in the `profiles` collection.

## Setup

1. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create the MySQL database**
   ```bash
   mysql -u root -p < schema.sql
   ```

3. **Make sure MongoDB is running locally**, or point `MONGO_URI` at a
   hosted instance (e.g. MongoDB Atlas).

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # then edit .env with your MySQL password, SECRET_KEY, etc.
   ```

5. **(Optional) Add demo data**
   ```bash
   python seed.py
   ```
   Creates two clients and two freelancers, all with the password
   `password123`, plus two sample jobs.

6. **Run the app**
   ```bash
   python app.py
   ```
   Visit `http://localhost:5000`.

## Project structure

```
earnify/
├── app.py              Routes, auth, MySQL + MongoDB access
├── config.py            Environment-based configuration
├── schema.sql            MySQL schema (users, jobs, applications)
├── seed.py                Optional demo data
├── requirements.txt
├── .env.example
├── static/
│   ├── css/style.css
│   └── js/script.js
└── templates/
    ├── base.html          Shared layout, nav, flash messages
    ├── index.html          Landing page
    ├── signup.html / login.html
    ├── jobs.html            Browse + filter open jobs
    ├── job_detail.html       Single job + application form
    ├── post_job.html          Client: create a job
    ├── dashboard_client.html   Client: their posted jobs
    ├── dashboard_freelancer.html  Freelancer: their applications
    └── applicants.html         Client: review + accept/decline applicants
```

## Feature map (back to the resume bullets)

| Resume bullet | Where it lives |
|---|---|
| Job posting, browsing, application workflows end-to-end | `new_job`, `jobs`, `job_detail`, `apply_to_job`, `view_applicants`, `update_application_status` in `app.py` |
| Responsive HTML/CSS/JS frontend | `static/`, `templates/`, mobile nav + breakpoint in `style.css` |
| Flask backend, routing and business logic | `app.py` |
| MySQL + MongoDB schemas for accounts, jobs, applications | `schema.sql` (MySQL) + `profiles_collection` (MongoDB) |
| UI/UX for students and first-time freelancers, reduced onboarding friction | Two-field-minimum signup, role picked up front from the homepage, one-form job application |

## Known simplifications (worth naming if asked in an interview)

- Sessions use Flask's built-in signed cookies rather than a server-side
  session store — fine at this scale, worth mentioning as a scaling
  consideration.
- No file uploads (resumes, portfolio images) — the MongoDB profile
  document has a `portfolio_links` field as a placeholder for that.
- No email verification or password reset flow.
- No pagination on the jobs listing yet — add `LIMIT`/`OFFSET` to the
  query in `jobs()` once there's enough data to need it.
