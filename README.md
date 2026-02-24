# ISL Connect - Project Overview

This directory contains the Production-Ready ISL recognition system.

## Directory Structure

- **backend/**: Contains the FastAPI server, model inference logic, and configuration.
- **frontend_react/**: Contains the React frontend application (Vite project).

## Prerequisites

- Python 3.8+
- Node.js 16+
- **Model Files**: ensure `isl_lstm_model.h5` and `label_map.json` are inside the `backend/` folder.

## Quick Start

### 1. Start the Backend

Open a terminal in the `backend` folder:

```bash
cd backend
pip install -r requirements.txt  # Install dependencies (first time only)
uvicorn main:app --reload
```

The server runs at `http://localhost:8000`.

### 2. Start the Frontend

Open a new terminal in the `frontend_react` folder:

```bash
cd frontend_react
npm install     # Install dependencies (first time only)
npm run dev
```

The website runs at `http://localhost:5173`.

## Detailed Usage

1.  Open `http://localhost:5173` in your browser.
2.  **Home Page**:
    - Allow camera access.
    - Click **"Initiate Capture"**.
    - Perform a sign for 5 seconds.
    - The predicted sign will appear.
3.  **Dictionary Page**:
    - Browse and search for ISL signs.
