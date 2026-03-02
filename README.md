# Train Booking Service
A backend service built with Django and Django REST Framework for managing train ticket bookings. 

This project was developed as a portfolio piece to demonstrate proficiency in building scalable, secure, and well-documented API services.

# Getting Started
### 1. Clone the repository
First, you need to download the source code to your computer. Open your terminal or command prompt and run the following command: 

```shell
git clone https://github.com/YOUR_USERNAME/train-booking-service.git
cd train-booking-service
```
*(Replace YOUR_USERNAME with your actual GitHub username).*


### 2. Configure Environment Variables
The project requires an `.env` file to handle secrets and database credentials. 
Create a new file named `.env` in the root directory of the project and add the following configuration:
```shell
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_SETTINGS_MODULE=core.settings.dev
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=db
POSTGRES_DB_PORT=5432
```
### 3. Build and Run with Docker

This project is fully containerized. Ensure you have Docker and Docker Compose installed. To build the images and start the services, run:

```shell
docker-compose up --build
```
**What this command does:**

- Builds the Docker image for the Django application.
- Pulls the PostgreSQL image.
- Runs database migrations automatically.
- Collects static files.
- Starts the development server on http://127.0.0.1:8000.

### 4. Running the Tests
To ensure everything is working correctly, you can run the full suite of 66 tests inside the container:
```shell
docker-compose run app python manage.py test
```

### 5. Accessing the Admin Panel
Once the application is running, you can access the Django admin panel to manage your data:
- URL: `http://127.0.0.1:8000/admin/`
- *Note: Make sure to create a superuser if you haven't already:*
```shell
docker-compose run app python manage.py createsuperuser
```

## Features
- Authentication: Secure user management using JWT (JSON Web Tokens).
- API Documentation: Interactive documentation via Swagger and Redoc (powered by drf-spectacular).
- Admin Panel: Built-in Django admin interface for managing stations, routes, and bookings.
- Containerization: Full Docker support for seamless development and deployment.
- Configuration: Multi-environment settings (base, dev, prod).
- Robust Testing: Includes 66 comprehensive tests to ensure service reliability.

## Prerequisites
- Docker and Docker Compose installed on your machine.
- An .env file in the root directory (refer to the env section below).

## API Documentation
Once the server is running, you can explore the API endpoints and test requests using the built-in documentation:

- Swagger: `http://localhost:8000/api/v1/doc/swagger/`
- Redoc: `http://localhost:8000/api/v1/doc/redoc/`

## Tech Stack
- **Framework:** Django 5.2.11, Django REST Framework
- **Database:** PostgreSQL 16.0
- **Authentication** SimpleJWT
- **Docs:** drf-spectacular
- **Deployment:** Docker, Docker Compose

## Project Structure
```shell
train-booking-service/
├── core/                   # Project configuration (settings, wsgi, asgi)
│   ├── settings/           # Split settings (base.py, dev.py, prod.py)
│   └── urls.py             # Root URL configuration (admin, api, swagger)
├── station/                # Main application: Stations, Routes, Trains
│   ├── models.py           # Database schema
│   ├── serializers.py      # DRF data validation and transformation
│   ├── views.py            # API endpoints logic
│   ├── urls.py             # Station-specific routing
│   └── tests/              # Test suite for station logic
├── user/                   # Authentication and profile management
│   ├── models.py           # Custom user model
│   ├── serializers.py      # JWT token and user registration logic
│   └── views.py            # User-related API endpoints
├── docker-compose.yaml     # Service orchestration (app, db)
├── Dockerfile              # Docker image configuration
└── requirements.txt        # Project dependencies
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Improvements
- [ ] Implement Redis for caching API responses.
- [ ] Add integration with a third-party payment gateway.
- [ ] Add GitHub Actions for continuous integration (CI) and automated testing.