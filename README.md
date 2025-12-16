# ParkVision 2.0

A full-featured, intelligent parking analytics system that provides real-time occupancy detection, license plate tracking, and interactive lot management tools. ParkVision transforms parking management from a static detection prototype into a comprehensive analytics platform.

## 🎯 What It Solves

ParkVision 2.0 addresses the challenges of modern parking management:

- **Real-time Occupancy Monitoring**: Automatically detect and track vehicle occupancy in parking lots using computer vision
- **Intelligent Analytics**: Generate insights on parking patterns, utilization rates, and peak hours
- **Multi-lot Management**: Manage multiple parking facilities from a single dashboard
- **Vehicle Tracking**: Track vehicles entering and exiting lots with session management
- **User Authentication**: Secure access control for parking administrators
- **Interactive Dashboard**: Modern mobile and web interface for monitoring and managing parking operations

## 🏗️ Architecture

ParkVision 2.0 is built as a microservices architecture with three main components:

```
┌─────────────────┐
│   Frontend      │  React Native/Expo Dashboard
│   (Mobile/Web)  │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│    Backend      │  FastAPI REST API
│   (Python)      │
└────────┬────────┘
         │
         │ Database
         │
┌────────▼────────┐      ┌──────────────┐
│   PostgreSQL    │      │   AI/CV      │  YOLO + DeepSORT
│    Database     │◄─────┤   Pipeline   │  Vehicle Detection
└─────────────────┘      └──────────────┘  & Tracking
```

### Components

1. **Frontend** (`frontend/`): React Native mobile application built with Expo
2. **Backend** (`backend/`): FastAPI-based REST API with PostgreSQL database
3. **AI/CV Module** (`ai_cv/`): Computer vision pipeline for vehicle detection and tracking

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Relational database for persistent storage
- **SQLAlchemy** - Python ORM for database operations
- **bcrypt** - Secure password hashing
- **Pydantic** - Data validation and settings management
- **pytest** - Testing framework

### Frontend
- **React Native** - Cross-platform mobile framework
- **Expo** - Development platform and tooling
- **TypeScript** - Type-safe JavaScript
- **Expo Router** - File-based routing

### AI/Computer Vision
- **YOLO (Ultralytics)** - Real-time object detection
- **DeepSORT** - Multi-object tracking
- **OpenCV** - Image and video processing
- **NumPy, SciPy, Pandas** - Data processing and analysis

## 📡 API Routes

### Base URL
```
http://localhost:8000
```

### Authentication (`/auth`)
- `POST /auth/register` - Register a new user
  - Request body: `{username, email, password}`
  - Returns: User object (password excluded)
- `POST /auth/login` - Authenticate user
  - Request body: `{username, password}`
  - Returns: User object with updated `last_login`
- `GET /auth/users` - Get all users (admin)
- `GET /auth/users/{user_id}` - Get user by ID
- `PUT /auth/users/{user_id}` - Update user
- `DELETE /auth/users/{user_id}` - Delete user

### Parking Lots (`/lots`)
- `GET /lots/` - Get all parking lots
- `POST /lots/` - Create a new parking lot
  - Request body: `{name, address, total_spaces, description, init_frame_path, video_path, video_start_time}`
- `GET /lots/{lot_id}` - Get specific parking lot by ID
- `PUT /lots/{lot_id}` - Update parking lot
- `DELETE /lots/{lot_id}` - Delete parking lot

### Analytics (`/analytics`)
- Analytics endpoints for parking statistics and insights (see `backend/app/api/analytics_routes.py`)

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🗄️ Database Schema

### Core Models

- **User**: User accounts with authentication
  - `id`, `username`, `email`, `password_hash`, `is_admin`, `created_at`, `last_login`

- **ParkingLot**: Parking facility information
  - `id`, `name`, `address`, `total_spaces`, `description`, `init_frame_path`, `video_path`, `video_start_time`, `created_at`, `updated_at`

- **ParkingSpot**: Individual parking spaces within a lot
  - Related to `ParkingLot` via foreign key

- **SpotStatus**: Real-time occupancy status of parking spots
  - Tracks current state of each spot

- **Vehicle**: Vehicle information and tracking
  - Related to `User` for ownership tracking

- **ParkingAnalytics**: Historical analytics and statistics
  - Related to `ParkingLot` for aggregated data

## 🚀 Getting Started

### Prerequisites

- **Docker** and **Docker Compose** (recommended)
- Or:
  - Python 3.11+ (for backend and AI/CV)
  - Node.js 18+ and npm (for frontend)
  - PostgreSQL 15+ (for local development)

### Quick Start with Docker

#### Backend

```bash
cd backend
docker compose up
```

This will:
- Start PostgreSQL database on port `5432`
- Start FastAPI backend on `http://localhost:8000`
- Auto-initialize database tables

#### AI/CV Module

```bash
cd ai_cv
docker compose build
docker compose up
```

#### Frontend

```bash
cd frontend/parkvision_dashboard
npm install
npx expo start
```

### Local Development Setup

#### Backend

1. Create virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (create `.env`):
   ```env
   DATABASE_URL=postgresql://parkvision:parkvision@localhost:5432/parkvision
   ```

4. Run the server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### AI/CV Module

1. Install system dependencies (Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-opencv ffmpeg libsm6 libxext6
   ```

2. Install Python dependencies:
   ```bash
   cd ai_cv
   pip install -r requirements.txt
   ```

3. YOLO models will be downloaded automatically on first use

#### Frontend

1. Install dependencies:
   ```bash
   cd frontend/parkvision_dashboard
   npm install
   ```

2. Start development server:
   ```bash
   npx expo start
   ```

## 📁 Project Structure

```
parkvision2.0/
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   │   ├── auth_routes.py
│   │   │   ├── lot_routes.py
│   │   │   └── analytics_routes.py
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utilities (DB, config)
│   │   └── tests/          # Test suite
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                # React Native frontend
│   └── parkvision_dashboard/
│       ├── app/            # Expo Router app directory
│       ├── assets/         # Images, fonts, etc.
│       └── package.json
│
├── ai_cv/                   # Computer vision pipeline
│   ├── detection/          # Vehicle detection (YOLO)
│   ├── recognition/        # Tracking (DeepSORT) & sessions
│   ├── utilities/          # Helper functions
│   ├── tests/              # Test suite
│   ├── run_pipeline.py     # Main execution script
│   └── requirements.txt
│
└── docs/                    # Additional documentation
```

## 🔧 Features

### Current Features
- ✅ User authentication with secure password hashing
- ✅ Parking lot CRUD operations
- ✅ Real-time vehicle detection using YOLO
- ✅ Multi-object tracking with DeepSORT
- ✅ Parking spot occupancy analysis
- ✅ Vehicle session management
- ✅ RESTful API with OpenAPI documentation
- ✅ Docker containerization
- ✅ Cross-platform mobile dashboard

### Planned Features
- 🔄 License plate recognition
- 🔄 Advanced analytics and reporting
- 🔄 Real-time video streaming integration
- 🔄 WebSocket support for live updates
- 🔄 Historical data visualization
- 🔄 Multi-user role management

## 🧪 Testing

### Backend Tests

```bash
# In Docker
docker compose exec backend pytest

# Locally
cd backend
pytest
```

### AI/CV Tests

```bash
cd ai_cv
python3 build_test_data.py
python3 tests/test_detect.py
python3 tests/test_tracker.py
python3 tests/test_lot_detection.py
```

## 📚 Documentation

- [Backend README](backend/README.md) - Detailed backend setup and API documentation
- [AI/CV README](ai_cv/README.md) - Computer vision pipeline documentation
- [Frontend README](frontend/parkvision_dashboard/README.md) - Frontend development guide

## 🤝 Contributing

1. Create a new branch for your feature
2. Make your changes and test locally
3. Run tests to ensure nothing breaks
4. Submit a pull request

## 📝 License

[Add your license information here]

## 🔗 Links

- **API Documentation**: `http://localhost:8000/docs` (when backend is running)
- **GitHub Repository**: [cooperwooley/parkvision2.0](https://github.com/cooperwooley/parkvision2.0)

---

**ParkVision 2.0** - Transforming parking management through intelligent computer vision and analytics.
