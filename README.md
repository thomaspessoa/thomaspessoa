# Mini-plataforma “Catálogo de Filmes”

This project is a mini-platform for a movie catalog, built with a full-stack architecture. It includes a Python FastAPI backend, a PostgreSQL database, a static frontend served by Nginx, and observability with Prometheus and Grafana. The entire application is containerized and orchestrated with Docker Compose.

## Features

-   **API (Python/FastAPI):**
    -   `GET /health`: Health check endpoint.
    -   `GET, POST, PUT, DELETE /movies`: Full CRUD operations for movies.
    -   Exposes Prometheus metrics at `/metrics`.
-   **Database (PostgreSQL):**
    -   Persistent data storage for movies using a Docker volume.
-   **Frontend (Static HTML/CSS/JS):**
    -   Simple interface to view the movie catalog.
    -   Served by a lightweight Nginx container.
    -   Communicates with the backend via a reverse proxy.
-   **Observability (Prometheus & Grafana):**
    -   Prometheus scrapes metrics from the API.
    -   Grafana provides a pre-configured dashboard to visualize API CPU and memory usage.
-   **Containerization & Orchestration:**
    -   Multi-stage `Dockerfile` for an optimized and secure API image.
    -   `docker-compose.yml` to manage all services.
    -   Custom network for inter-service communication.
    -   Health checks to ensure service availability.
-   **CI/CD (GitHub Actions):**
    -   A CI pipeline that automatically builds and pushes the API's Docker image to a container registry when changes are made to the `api` directory.

## Project Structure

```
.
├── .env.example
├── .github/workflows/ci.yml
├── api/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── main.py
│   └── requirements.txt
├── docker-compose.yml
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── nginx/
│       ├── Dockerfile
│       └── nginx.conf
├── grafana/
│   ├── provisioning/
│   │   ├── dashboards.yml
│   │   └── dashboards/
│   │       └── api-dashboard.json
├── prometheus.yml
└── README.md
```

## Getting Started

### Prerequisites

-   Docker
-   Docker Compose

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/thomaspessoa/movie-catalog.git
    cd movie-catalog
    ```

2.  **Create the environment file:**

    Copy the example environment file and customize the variables if needed. The default values are sufficient for local development.

    ```bash
    cp .env.example .env
    ```

3.  **Build and run the application:**

    Use Docker Compose to build the images and start all the services in detached mode.

    ```bash
    docker-compose up -d --build
    ```

### Usage

Once the application is running, you can access the different services:

-   **Frontend:** [http://localhost:8080](http://localhost:8080)
-   **API:** [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
-   **Prometheus:** [http://localhost:9090](http://localhost:9090)
-   **Grafana:** [http://localhost:3000](http://localhost:3000)
    -   **Login:** `admin` / `admin` (you will be prompted to change the password on first login)
    - The API dashboard will be pre-installed.

### Testing the API

You can use the Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs) to interact with the API endpoints.

-   **Create a movie (POST /movies):**

    ```json
    {
      "id": 1,
      "title": "Inception",
      "director": "Christopher Nolan",
      "year": 2010
    }
    ```

-   **Get all movies (GET /movies):**
    -   You should see the movie you just created.
-   **Get a specific movie (GET /movies/{movie_id}):**
    -   Use the ID of the movie you created.
-   **Update a movie (PUT /movies/{movie_id}):**
    -   Update the movie details.
-   **Delete a movie (DELETE /movies/{movie_id}):**
    -   Delete the movie you created.

### Data Persistence

The PostgreSQL database uses a named volume (`postgres_data`) to persist data. This means that even if you stop and remove the containers with `docker-compose down`, your data will be preserved and available when you run `docker-compose up` again.

### CI/CD

The repository includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that automatically builds and pushes the API's Docker image to Docker Hub whenever changes are pushed to the `main` branch in the `api/` directory.

To make this work in your own fork, you will need to configure the following secrets in your repository settings:

-   `DOCKER_USERNAME`: Your Docker Hub username.
-   `DOCKER_PASSWORD`: Your Docker Hub password or access token.

## Stopping the Application

To stop and remove all the containers, networks, and volumes, run:

```bash
docker-compose down
```

If you want to remove the named volume as well (deleting all data), run:

```bash
docker-compose down -v
```