# Carpool Management Application

A full-stack web application for managing school carpools with support for multiple user roles, automated scheduling, and preference-based ride assignments.

## Features

- Multi-role user system (Admin, Parent, Student)
- Secure authentication with JWT
- Admin user management
- Flexible carpool scheduling
- Driver preference management
- Automated schedule generation
- Mobile-first web interface
- Azure cloud integration

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
│   │   ├── core/
│   │   ├── db/
│   │   └── models/
│   └── requirements.txt
├── frontend/
│   ├── components/
│   ├── pages/
│   └── package.json
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 