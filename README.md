# Final Project: Calculations App

This is my final IS601 project. The main purpose of this project is to show how the work from previous modules connects and work to make a functioning web application. 

FastAPI and SQLAlchemy calculator application with user registration/login,
persisted calculation history, Docker deployment, and CI/CD. 

## Repository Links

- GitHub Repository: https://github.com/cmgoncalves1998/final_is601
- Docker Hub Repository: https://hub.docker.com/r/christianmgoncalves1/final_is601

## New Feature: Usage Summary Report

My feature I decided to implement is a detailed usage summary report for authenticated users. This project adds an report/history features that:

- `GET /calculations/stats` returns total calculations, average operands,
  average result, operation counts, most-used operation, and latest activity.
- The dashboard displays those metrics in a Usage Summary panel.
- The summary refreshes after calculations are created or deleted.
- No Alembic migration is required because the feature summarizes existing
  calculation rows and does not change the database schema.

## Running the Application

Install dependencies and start the app locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

With Docker Compose:

```bash
docker compose up --build
```

The app runs at `http://localhost:8000`.

## Running Tests

Start Postgres with Docker Compose, install Playwright, then run the suite:

```bash
docker compose up -d db
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
pytest -q
```

The full command reports the combined coverage percentage. Focused commands are
useful while developing, but their coverage percentages only reflect that subset.

Useful focused commands:

```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## Docker Hub

The GitHub Actions workflow builds and pushes the application image to:

[christianmgoncalves1/final_is601](https://hub.docker.com/r/christianmgoncalves1/final_is601)

Tags pushed by CI:

- `christianmgoncalves1/final_is601:latest`
- `christianmgoncalves1/final_is601:${GITHUB_SHA}`

## CI/CD

`.github/workflows/test.yml` runs unit, integration, and Playwright E2E tests,
builds the Docker image, scans it with Trivy, and pushes to Docker Hub after
the test and security jobs pass on `main`.

---

# 📦 Project Setup

---

# 🧩 1. Install Homebrew (Mac Only)

> Skip this step if you're on Windows.

Homebrew is a package manager for macOS.  
You’ll use it to easily install Git, Python, Docker, etc.

**Install Homebrew:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

# 🧩 2. Install and Configure Git

## Install Git

- **MacOS (using Homebrew)**

```bash
brew install git
```

- **Windows**

Download and install [Git for Windows](https://git-scm.com/download/win).  
Accept the default options during installation.

**Verify Git:**

```bash
git --version
```

---

## Configure Git Globals

Set your name and email so Git tracks your commits properly:

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```


## Generate SSH Keys and Connect to GitHub

> Only do this once per machine.

1. Generate a new SSH key:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

(Press Enter at all prompts.)

2. Start the SSH agent:

```bash
eval "$(ssh-agent -s)"
```

3. Add the SSH private key to the agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

4. Copy your SSH public key:

- **Mac/Linux:**

```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```

- **Windows (Git Bash):**

```bash
cat ~/.ssh/id_ed25519.pub | clip
```

5. Add the key to your GitHub account:
   - Go to [GitHub SSH Settings](https://github.com/settings/keys)
   - Click **New SSH Key**, paste the key, save.

6. Test the connection:

```bash
ssh -T git@github.com
```

You should see a success message.

---

# 🧩 3. Clone the Repository

Now you can safely clone the course project:

```bash
git clone <repository-url>
cd <repository-directory>
```

---

#4. Install Python 3.10+

## Install Python

- **MacOS (Homebrew)**

```bash
brew install python
```

- **Windows**

Download and install [Python for Windows](https://www.python.org/downloads/).  

**Verify Python:**

```bash
python3 --version
```
or
```bash
python --version
```

---

## Create and Activate a Virtual Environment


``'bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate.bat  # Windows
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

---

#5. (Optional) Docker Setup

> Skip if Docker isn't used in this module.

## Install Docker

- [Install Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- [Install Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

## Build Docker Image

```bash
docker build -t <image-name> .
```

## Run Docker Container

```bash
docker run -it --rm <image-name>
```

---

# 🚀 6. Running the Project

- **Without Docker**:

```bash
python main.py
```

- **With Docker**:

```bash
docker run -it --rm <image-name>
```

# 7. Final Project Reflection:

This final project helped me understand how different parts of a backend application all come together. Each step taken for the final project is just a small piece of the puzzle. I liked the idea of a statistics summary because I see myself as an analytical and data-driven person, so I went with that feature. The biggest learning experience for me was writing the new feature and seeing everything come to life. Making sure all the parts of the project worked together and making the github actions pass was the most difficult part for me. I always had problems on our previous modules getting that to work but now I understand alot of the things needed to make it work. I enjoyed learning how to design an application from beginning to end, and what goes into that. I also plan to be leveraging the skills I learned in this class to lean more about AI and build more projects. AI worked as a guide for me to help me implement tests and understand front-end items. In my previous classes, I have worked with python code, but I was not familiar with front-end development. AI was able to guide me along the way with something I have nver worked with before... I was able thoroughly review what the AI was giving me and I am happy with all the learning I have done over this project and IS601 as a whole. Something I will work on over the summer in my free-time along with my internship is building more applications with AI's help and learning to ask questions to properly to build more effectively. 
