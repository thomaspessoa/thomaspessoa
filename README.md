# Rizzatti - Bus Tracking System

## Overview

Rizzatti is a web-based bus tracking application designed to manage and monitor bus routes and driver activities. It provides distinct interfaces for administrators and drivers. Administrators can view real-time locations of active buses on a map and see a list of active trips. Drivers can log in, manage their trips (start, end), and automatically share their geolocation while a trip is active.

## Key Features

*   **Role-Based Authentication:** Separate login and dashboards for Administrators and Drivers.
*   **Administrator Dashboard:**
    *   Real-time map view of all active buses using Leaflet.js.
    *   List view of active trips with details (driver, schedule, start time, location).
*   **Driver Dashboard:**
    *   Start new trips with schedule information.
    *   End active trips.
    *   Automatic geolocation tracking via the browser while a trip is active, updating the server.
*   **Trip Management:** Creation, activation, and completion of trips linked to drivers.
*   **Session Management:** Secure user sessions using Flask-Login.

## Technology Stack

*   **Backend:** Python, Flask
*   **Database:** SQLite (via Flask-SQLAlchemy)
*   **Authentication:** Flask-Login
*   **Frontend:** HTML, CSS, JavaScript
*   **Mapping:** Leaflet.js
*   **Password Hashing:** Werkzeug security helpers

## Prerequisites

*   Python 3.8 or newer
*   pip (Python package installer)
*   A modern web browser with JavaScript enabled (for geolocation and map display).
*   Git (for cloning the repository).

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd rizzatti-bus-tracker 
    ```
    (Replace `<repository_url>` with the actual URL of the repository)

2.  **Create and Activate a Python Virtual Environment:**
    *   On macOS and Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Database:**
    The database (`database/app.db`) and default users are automatically created the first time you run the application. If you need to reset the database, you can delete the `database` directory and restart the app.

5.  **Run the Application:**
    ```bash
    python app.py
    ```
    The application will be accessible at `http://localhost:8080` by default.

## Running Tests

To run the unit and integration tests, navigate to the project's root directory and execute:

```bash
python -m unittest discover tests
```
This will discover and run all tests located in the `tests` directory.

## Default Credentials

The application comes with two pre-created users:

*   **Administrator:**
    *   Username: `admin`
    *   Password: `admin_password`
*   **Driver:**
    *   Username: `driver1`
    *   Password: `driver_password`

You can log in with these credentials to explore the respective dashboards and functionalities.

---

This project was developed as part of a guided exercise.
