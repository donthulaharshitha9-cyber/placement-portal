
🎓 College Placement Portal (Python + Flask)

📌 Project Overview

The College Placement Portal is a web-based platform built using Python (Flask framework) and SQLite (via SQLAlchemy ORM) to streamline campus recruitment processes.
It enables students to register, manage profiles, upload resumes, view job listings, and apply for opportunities, while admins can post jobs, track applications, and update statuses.


---

🚀 Features

👩‍🎓 Student Module

Register and log in securely

Create & update profile

Upload resume (PDF only)

Browse job opportunities

Apply for jobs (no duplicate applications)

Track application status (Pending / Accepted / Rejected)


🛠 Admin Module

Secure admin login

Post new job openings

View student applications with resumes

Update application status

Manage job listings



---

🏗 Tech Stack

Backend: Python, Flask

Database: SQLite (with SQLAlchemy ORM)

Frontend: HTML, CSS (Bootstrap/Tailwind optional)

Authentication: Password hashing (Werkzeug), Flask sessions

File Handling: Resume uploads (PDFs, securely stored)



---

📂 Project Structure

College-Placement-Portal/
│── app.py                 # Main Flask application
│── templates/             # HTML templates
│── static/                # CSS, JS, Images
│── uploads/               # Resume uploads
│── placement.db           # SQLite database
│── README.md              # Project documentation


---

⚙️ Installation & Setup

1. Clone this repository:

git clone https://github.com/your-username/college-placement-portal.git
cd college-placement-portal


2. Create a virtual environment & install dependencies:

python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

pip install -r requirements.txt


3. Initialize the database:

python
>>> from app import db
>>> db.create_all()
>>> exit()


4. Run the application:

python app.py


5. Open in browser:

http://127.0.0.1:5000/




---

📸 Screenshots

Student Dashboard

Admin Dashboard

Job Listings & Application Tracking


(Add screenshots here for better presentation)


---

🔮 Future Scope

Mobile app integration (React Native / Flutter)

AI-powered job recommendations

Email/SMS notifications

Analytics dashboard for placement statistics

Integration with LinkedIn/GitHub
# placement-portal