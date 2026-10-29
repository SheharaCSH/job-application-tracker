# Job Application Tracker

A full-stack web app for tracking job applications on a status board (Applied, Interview, Offer, Rejected).

**Live demo:** https://job-application-tracker-one-pied.vercel.app

> The back end runs on a free instance that sleeps when idle, so the first request after a pause can take about 50 seconds.

## Features
- User registration and login with JWT authentication and hashed passwords
- Each user only sees and edits their own applications
- Add, update, move between stages, and delete applications
- Input validation on the API (Pydantic) and interactive API docs

## Tech stack
- **Front end:** React, Vite
- **Back end:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL (Neon) in production, SQLite locally
- **Deployment:** Vercel (front end), Render (API)

## Run it locally

Back end:

```
git clone https://github.com/SheharaCSH/job-application-tracker.git
cd job-application-tracker/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Front end (in a second terminal):

```
cd job-application-tracker/frontend
npm install
npm run dev
```

Open http://localhost:5173. API docs are at http://127.0.0.1:8000/docs.

## What I learned
Designing a relational schema, securing an API with JWT, connecting a React app to a REST back end, handling CORS, and deploying across three platforms with environment variables for secrets.

## Next steps
Add editing for all fields, search and filters, a stats dashboard, and automated tests.

## Author
Chamudi Shehara Hennayaka