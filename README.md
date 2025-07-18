# Queue Management System

A full-stack web application for managing queues, built with Django (backend) and React (frontend).

## Features
- Queue Manager login and registration (with email OTP verification)
- Create and manage multiple queues
- Add persons/tokens to queues (unique per queue)
- View and reorder tokens in each queue
- Assign the top token for service
- Cancel tokens from the queue
- Dashboard with analytics: average wait time, queue length trends, active queues, and more
- Clean, modern, and responsive UI

## Tech Stack
- **Backend:** Django, Django REST Framework, PostgreSQL
- **Frontend:** React, Axios, Tailwind CSS

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js & npm
- PostgreSQL

### Backend Setup
1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
2. Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure your PostgreSQL database in `backend/queue_management/settings.py` if needed.
4. Run migrations:
   ```sh
   python manage.py migrate
   ```
5. Start the backend server:
   ```sh
   python manage.py runserver
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the frontend development server:
   ```sh
   npm start
   ```

The frontend will run on [http://localhost:3000](http://localhost:3000) and the backend on [http://localhost:8000](http://localhost:8000).

## Usage
- Register as a Queue Manager and verify your email.
- Log in to create and manage queues.
- Add tokens to queues, reorder, assign for service, or cancel as needed.
- View analytics on the dashboard.

## Evaluation Criteria
1. **Working application**: All features functional and integrated.
2. **Code in Github**: Codebase is version-controlled and available on GitHub.
3. **Good UI**: Clean, modern, and user-friendly interface.
4. **Bug free**: No known bugs; robust error handling and validation.

## License
This project is for educational/demo purposes.
