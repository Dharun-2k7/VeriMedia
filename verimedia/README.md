# VeriMedia - Deepfake Cryptographic Verification

VeriMedia is a platform that uses Neural Networks and Cryptography to detect AI Deepfakes and Face Swaps.

---

## 🚀 Deploy to Render (1-Click)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Dharun-2k7/VeriMedia)

> **After clicking the button**, Render will ask you to set two environment variables:
> 1. `FRONTEND_URL` → Leave blank for now (you'll fill it after the services spin up)
> 2. `NEXT_PUBLIC_API_URL` → Leave blank for now
>
> Once both services are live:
> - Copy the **backend** URL (e.g. `https://verimedia-backend.onrender.com`) and set `NEXT_PUBLIC_API_URL` to `https://verimedia-backend.onrender.com/api` in the **frontend** service env vars.
> - Copy the **frontend** URL (e.g. `https://verimedia-frontend.onrender.com`) and set `FRONTEND_URL` to `https://verimedia-frontend.onrender.com` in the **backend** service env vars.
> - Redeploy both services for the changes to take effect.

---

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
