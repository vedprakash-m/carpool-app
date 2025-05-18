# Carpool Management Application

A comprehensive full-stack web application for managing school carpools with support for multiple user roles, automated scheduling, and preference-based ride assignments.

## Features

- **Multi-role User System**: Admin, Parent, and Student roles with appropriate permissions
- **Secure Authentication**: JWT-based authentication and role-based access control
- **Admin User Management**: Comprehensive tools for user administration
- **Schedule Templates**: Create and manage weekly carpool schedule templates
- **Driver Preferences**: Parents can submit weekly availability preferences with constraints
- **Automated Schedule Generation**: Algorithm generates schedules based on preferences and historical fairness
- **Swap Requests**: Parents can request schedule swaps with other drivers
- **Student Views**: Students can view their upcoming rides and drivers
- **Data Visualization**: Admin dashboard with carpool statistics and visualizations
- **Mobile-first Design**: Responsive UI optimized for all screen sizes
- **Azure Integration**: Built for deployment on Azure services

## Tech Stack

### Backend
- Python 3.8+
- FastAPI
- Azure Cosmos DB
- Azure Key Vault
- JWT Authentication

### Frontend
- Next.js
- React
- Tailwind CSS
- Zustand (State Management)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Azure subscription (for Cosmos DB and Key Vault)

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with the following variables:
```env
COSMOS_ENDPOINT=your_cosmos_db_endpoint
COSMOS_KEY=your_cosmos_db_key
COSMOS_DATABASE=carpool_db
JWT_SECRET_KEY=your_secret_key
AZURE_KEYVAULT_URL=your_keyvault_url
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
```

4. Run the development server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create a `.env.local` file with:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

3. Run the development server:
```bash
npm run dev
```

## API Documentation

Once the backend server is running, visit:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## Development

### Project Structure

```
carpool-app/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── api.py
│   │   │       └── endpoints/
│   │   │           ├── admin.py
│   │   │           ├── auth.py
│   │   │           ├── driver_preferences.py
│   │   │           ├── schedule_generation.py
│   │   │           ├── schedule_templates.py
│   │   │           ├── statistics.py
│   │   │           ├── student.py
│   │   │           ├── swap_requests.py
│   │   │           └── users.py
│   │   ├── core/
│   │   │   ├── auth.py
│   │   │   └── config.py
│   │   ├── db/
│   │   │   └── cosmos.py
│   │   ├── models/
│   │   │   ├── core.py
│   │   │   └── user.py
│   │   └── services/
│   │       └── schedule_generator.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── dashboard/
│   │   │   ├── generate/
│   │   │   ├── preferences/
│   │   │   ├── profile/
│   │   │   ├── rides/
│   │   │   ├── statistics/
│   │   │   ├── student/
│   │   │   ├── swap-requests/
│   │   │   ├── templates/
│   │   │   ├── users/
│   │   │   └── page.tsx
│   │   └── login/
│   │       └── page.tsx
│   ├── lib/
│   │   └── api.ts
│   ├── store/
│   │   └── auth.ts
│   ├── types/
│   │   └── index.ts
│   ├── package.json
│   └── tailwind.config.js
└── README.md

A comprehensive carpool management web application for schools, supporting multiple user roles, scheduling, and automatic assignment generation.

## Features

- **User Role Management**: Admin, Parent, and Student roles with appropriate permissions
- **Schedule Templates**: Create and manage weekly carpool schedule templates
- **Driver Preferences**: Parents can submit weekly availability preferences
- **Automated Scheduling**: Algorithm generates schedules based on preferences and historical fairness
- **Swap Requests**: Parents can request schedule swaps with other drivers
- **Mobile-First Design**: Responsive UI for all screen sizes
- **Azure Integration**: Utilizes Azure services for deployment and operation

## Technology Stack

- **Backend**: FastAPI with Python
- **Frontend**: Next.js with React and TypeScript
- **Database**: Azure Cosmos DB
- **Authentication**: JWT-based authentication
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **CI/CD**: GitHub Actions
- **Hosting**: Azure Static Web Apps (Frontend), Azure Functions (Backend)

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Local Development Setup

#### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/vedprakash-m/carpool-app.git
cd carpool-app
```

2. Set up a Python virtual environment:
```bash
cd backend
python -m venv .venv
```

3. Activate the virtual environment:
   - Windows: `.\.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the backend directory with the following content:
```
COSMOS_ENDPOINT=your_cosmos_db_endpoint
COSMOS_KEY=your_cosmos_db_key
JWT_SECRET_KEY=your_secure_jwt_secret
```

6. Run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## API Documentation

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
├── backend/              # FastAPI backend application
│   ├── app/              # Core application modules
│   │   ├── api/          # API routes and endpoints
│   │   ├── core/         # Core functionality (auth, config)
│   │   ├── db/           # Database connections and models
│   │   ├── models/       # Pydantic models
│   │   └── services/     # Business logic services
│   ├── .env              # Environment variables (not tracked)
│   ├── main.py           # Application entry point
│   └── requirements.txt  # Python dependencies
│
├── frontend/             # Next.js frontend application
│   ├── app/              # Next.js app folder structure
│   │   ├── dashboard/    # Dashboard pages
│   │   └── login/        # Authentication pages
│   ├── lib/              # Shared utilities and API client
│   ├── store/            # State management with Zustand
│   └── types/            # TypeScript type definitions
│
└── .github/              # GitHub configuration
    └── workflows/        # CI/CD workflows
```

## Recent Feature Updates

### Student Ride Views
- Students can now view their upcoming carpool schedules
- Mobile-friendly design with day-by-day visualization
- Includes driver contact information for each ride

### Carpool Statistics Dashboard
- Data visualization for administrators
- See ride distribution by driver, route type, and day of the week
- Filter statistics by different timeframes (week, month, quarter, year)
- Helps administrators ensure fair distribution of driving duties

### Enhanced Swap Requests
- Parents can now request and manage ride swaps
- Real-time status updates for pending, accepted, and rejected requests
- Improved notification system

## Deployment

This application is designed to deploy to Azure services:

1. Backend: Azure Functions (Consumption Plan) or Azure Container Apps
2. Frontend: Azure Static Web Apps
3. Database: Azure Cosmos DB (Serverless)
4. Secrets: Azure Key Vault

The GitHub Actions workflow in `.github/workflows/ci-cd.yml` handles automated testing and deployment.

## License

This project is licensed under the MIT License
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 