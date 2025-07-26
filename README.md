# Python Web App with Flask, Docker, Kubernetes, CI/CD, and GitOps

## Project Overview

This project demonstrates a robust, full-stack deployment pipeline for a simple Python Flask web application. It showcases modern DevOps practices, including containerization with Docker, orchestration with Kubernetes, continuous integration and continuous delivery (CI/CD) with GitHub Actions, and a GitOps deployment strategy using ArgoCD.

The core application is a minimalist To-Do List, designed primarily to serve as a practical example of a production-ready deployment workflow.

## Features

* **To-Do List Application:**
    * Add new tasks.
    * Mark tasks as complete.
    * Delete tasks.
    * Display tasks in chronological order.
* **Containerized (Docker):** Application packaged into a lightweight Docker image for consistent environments.
* **Kubernetes Native:** Designed for deployment on a Kubernetes cluster.
    * Declarative deployments with resource management (requests/limits).
    * Readiness and Liveness Probes for robust health checks and self-healing.
* **Automated CI/CD (GitHub Actions):**
    * Automated build, test, and containerization on every push/PR.
    * Integrated **Trivy** for proactive Docker image vulnerability scanning.
    * Automated image tagging with Git SHA for immutable releases.
* **GitOps Deployment (ArgoCD):**
    * Git repository as the single source of truth for desired application state.
    * CI pipeline updates Kubernetes manifests directly in Git.
    * ArgoCD automatically reconciles the cluster state to match Git, ensuring reliable, auditable, and automated deployments.

## Technologies Used

* **Backend:** Python 3.9, Flask, Flask-SQLAlchemy, Gunicorn
* **Database:** SQLite (default for development, configured via `SQLALCHEMY_DATABASE_URI`)
* **Containerization:** Docker
* **Orchestration:** Kubernetes
* **CI/CD:** GitHub Actions
* **GitOps:** ArgoCD
* **Security Scanning:** Trivy
* **YAML Manipulation:** `yq`

## Architecture & Deployment Flow

1.  **Code Commit:** Developer pushes code changes to the `main` branch (or opens a Pull Request) on GitHub.
2.  **CI/CD Trigger:** GitHub Actions workflow (`.github/workflows/main.yml`) is triggered.
3.  **Build & Test:**
    * Python dependencies are installed (`requirements.txt`).
    * Unit/integration tests are run (`pytest`).
4.  **Containerization:**
    * A Docker image is built from the `Dockerfile`.
    * The image is tagged with both `latest` and the unique `git SHA` of the triggering commit.
    * The image is pushed to Docker Hub.
5.  **Security Scan:** The newly built Docker image is scanned for vulnerabilities using Trivy. The pipeline fails on critical/high severity findings.
6.  **GitOps Update:**
    * The `k8s/deployment.yaml` file within the repository is updated (using `yq`) to reference the new Docker image tagged with the `git SHA`.
    * This updated `deployment.yaml` is then committed and pushed back to the GitHub repository.
7.  **ArgoCD Reconciliation:**
    * ArgoCD, running in the Kubernetes cluster, continuously monitors the `k8s/` directory of this Git repository.
    * Upon detecting the `deployment.yaml` change, ArgoCD automatically pulls the new manifest from Git.
    * It then reconciles the cluster state to match the desired state in Git, initiating the rollout of the new application version in Kubernetes.

## Getting Started (Local Development)

To run the application locally for development and testing:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Vishwasoratur/python-web-app.git
    cd python-web-app
    ```
2.  **Create a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Flask application:**
    ```bash
    python app.py
    ```
    The application should now be accessible at `http://127.0.0.1:5000`.

## Running Tests

To run the unit and integration tests:

1.  Ensure you have followed the "Getting Started" steps to set up your virtual environment and install dependencies.
2.  Run `pytest`: 
    ```bash
    pytest
    ```

## Deployment to Kubernetes (High-Level)

This project is set up for automated deployment via GitOps using GitHub Actions and ArgoCD.

1.  **Container Registry:** Ensure you have a Docker Hub (or compatible) account configured with secrets in your GitHub repository (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`).
2.  **Kubernetes Cluster:** Have access to a Kubernetes cluster (e.g., Minikube, Docker Desktop K8s, EKS, GKE, AKS).
3.  **ArgoCD Installation:** Install ArgoCD in your Kubernetes cluster and configure it to monitor the `k8s/` directory of *this* repository.
4.  **Trigger Deployment:** Push changes to the `main` branch. The GitHub Actions workflow will build, test, push the image, update the `deployment.yaml` in Git, and push it. ArgoCD will then automatically synchronize the cluster.

**Manual Application (for initial setup/testing without full GitOps):**

If you want to manually apply the Kubernetes manifests (e.g., for initial testing before setting up ArgoCD):

```bash
# Ensure you have kubectl configured to your cluster
kubectl apply -f k8s/
