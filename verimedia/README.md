# VeriMedia - Deepfake Cryptographic Verification

VeriMedia is a platform that uses Neural Networks and Cryptography to detect AI Deepfakes and Face Swaps.

## System Requirements
- **Python 3.10+** (For the AI Backend)
- **Node.js 18+** (For the React Frontend)

---

## How to Run Locally

### 1. Start the Backend (AI Engine)
Open a terminal and navigate to the `verimedia/backend` folder:
```bash
cd backend
python3 -m venv venv

# Activate the virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install the heavy AI dependencies (this will download ~2GB of PyTorch)
pip install -r requirements.txt

# Start the Python AI Server
uvicorn app.main:app --reload
```
The backend will run on `http://localhost:8000`.

### 2. Start the Frontend (User Interface)
Open a **second terminal** and navigate to the `verimedia/frontend` folder:
```bash
cd frontend

# Install Node modules
npm install

# Start the Next.js server
npm run dev
```
The frontend will run on `http://localhost:3000`. 

Open your browser to `http://localhost:3000` and start testing!

---

## The Easiest Way: Using Docker
If you have Docker Desktop installed, you can skip all the manual setup and dependencies! Just run:
```bash
cd verimedia
docker-compose up --build
```
This will automatically download the AI models, configure the backend, and spin up the frontend. Once it finishes building, you can open `http://localhost:3000` in your browser!
