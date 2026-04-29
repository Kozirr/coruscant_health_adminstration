# Welcome to Coruscant Health Administration
***

## Task
Rebuild the Medical Management System for the Coruscant Health Administration (CHA), an organization within the Galactic Republic responsible for the health care of Coruscant's citizens. The challenge is to create a secure, role-based platform that manages patients, doctors, departments, emergency services, and encrypted medical documents while ensuring top UI/UX and automated deployment.

## Description
We solved the problem by building a modern full-stack application using Django REST Framework on the backend and React on the frontend. The system supports five stakeholder roles (Patient, Doctor, Administrator, Emergency Services, and Department) with dedicated dashboards and workflows. Patient health data is ingested via simulated device CSV uploads. Doctors can monitor trends, write prescriptions, and order services. Departments receive and execute orders. Emergency Services can input patients in seconds. All uploaded documents are encrypted with AES-256 before storage on AWS S3. The application is containerized with Docker for local development and deploys automatically to Railway via GitHub Actions CI/CD.

## Installation
```bash
git clone <repository>
cd coruscant_health_adminstration

# Local development with Docker Compose
docker-compose up --build

# Or manual backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend setup
cd ../frontend
npm install
npm run dev
```

## Usage
```bash
# Root-level CLI entrypoint
./coruscant_health_administration John Doe

# Or directly via Django management command
cd backend
python manage.py health_official John Doe
```

### The Core Team


<span><i>Made at <a href='https://qwasar.io'>Qwasar SV -- Software Engineering School</a></i></span>
<span><img alt='Qwasar SV -- Software Engineering School' src='https://storage.googleapis.com/qwasar-public/qwasar-logo_50x50.png' width='20px' /></span>
