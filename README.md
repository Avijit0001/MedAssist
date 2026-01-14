# MedAssist - AI-Powered Medical Consultation Platform

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-gray?logo=github)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19.1+-blue.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

*An intelligent healthcare assistant platform powered by Google Gemini AI*

[Features](#features) • [Tech Stack](#tech-stack) • [Getting Started](#getting-started) • [API Documentation](#api-documentation) • [Contributing](#contributing)

</div>

---

## 🎯 Overview

**MedAssist** is a full-stack medical consultation platform that leverages Google's Gemini AI to provide preliminary medical advice, symptom analysis, and AI-assisted medical image interpretation. Built with a modern React frontend and FastAPI backend, it offers a seamless experience for users seeking health information and medical insights.

### ⚠️ Disclaimer
This platform is designed for **informational purposes only** and should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for proper medical care.

---

## 🌟 Features

### Core Capabilities

- **💬 Medical Consultations**: Get preliminary medical advice through conversational AI interaction
- **🔍 Symptom Analysis**: Describe your symptoms and receive potential insights about your condition
- **📸 Medical Image Analysis**: Upload X-rays, CT scans, MRI, ultrasound, and blood test images for AI-assisted analysis
- **📋 Patient Profiles**: Track patient details including name, age, gender, and chief complaints
- **📄 PDF Report Generation**: Generate professional medical reports and prescriptions with recommendations
- **🔄 Conversation History**: Maintain context across multiple consultations for better AI responses
- **⚡ Real-time Responses**: Fast, intelligent responses powered by Gemini 2.5 Flash model

---

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- **Language**: Python 3.8+
- **AI Models**: Google Gemini 2.5 Flash (Chat & Vision)
- **PDF Generation**: ReportLab
- **Image Processing**: Pillow (PIL)
- **APIs**: FastAPI with CORS middleware

### Frontend
- **Library**: React 19.1+
- **Build Tool**: Vite 7.1+
- **Routing**: React Router 7.9+
- **Markdown Rendering**: React Markdown 10.1+
- **Styling**: CSS3 with responsive design

### Key Dependencies
- `google-genai`: Google Gemini AI integration
- `python-dotenv`: Environment variable management
- `reportlab`: PDF generation
- `pillow`: Image processing
- `cors`: Cross-Origin Resource Sharing middleware

---

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Home • Chat Interface • Patient Forms • Reports    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/REST
┌────────────────▼────────────────────────────────────────────┐
│              Backend (FastAPI + Python)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Chat Endpoint (/api/chat)                        │   │
│  │  • Report Generation (/api/generate-report)         │   │
│  │  • X-ray Analysis (Gemini Vision)                   │   │
│  │  • PDF Generation & Download                        │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────┘
                 │
         ┌───────▼────────┐
         │ Google Gemini  │
         │ AI (2.5 Flash) │
         └────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** installed on your system
- **Node.js 16+** and **npm** for frontend development
- **Google Gemini API Key** ([Get it here](https://makersuite.google.com/app/apikey))
- **Git** for version control

### Backend Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/MedAssist.git
cd MedAssist/back
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install fastapi uvicorn google-genai python-dotenv pillow reportlab python-multipart
```

#### 4. Configure Environment
Create a `.env` file in the `back` directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

#### 5. Start the Backend Server
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`

**Interactive API Documentation**: Visit `http://127.0.0.1:8000/docs` (Swagger UI)

---

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd ../front
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Start Development Server
```bash
npm run dev
```

The application will open at `http://localhost:5173` (or specified port)

#### 4. Build for Production
```bash
npm run build
```

---

## 📡 API Documentation

### Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/` | Health check and API information |
| `POST` | `/api/chat` | Send messages and analyze medical images |
| `POST` | `/api/generate-report` | Generate professional PDF reports |
| `GET` | `/api/status` | System status check |

### POST /api/chat

**Unified Chat Endpoint** - Handle both text conversations and X-ray analysis

**Request (Form Data):**
```json
{
  "message": "I have a persistent headache and fever",
  "conversation_history": "[{\"role\": \"user\", \"content\": \"...\"}, ...]",
  "xray_image": "<binary image file>"
}
```

**Response:**
```json
{
  "response": "Based on your symptoms of headache and fever...",
  "xray_analysis": "The X-ray shows...",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

**cURL Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -F "message=Analyze my X-ray image" \
  -F "conversation_history=[]" \
  -F "xray_image=@xray.jpg"
```

---

### POST /api/generate-report

**PDF Report Generation** - Create professional medical reports

**Request (JSON):**
```json
{
  "patient_name": "John Doe",
  "patient_age": 35,
  "patient_gender": "Male",
  "symptoms": "Chest pain, shortness of breath",
  "diagnosis": "Suspected acute coronary syndrome",
  "xray_analysis": "Chest X-ray shows normal cardiac silhouette",
  "medications": [
    "Aspirin 500mg - twice daily for 5 days",
    "Atorvastatin 20mg - once daily"
  ],
  "instructions": "Rest for 48 hours, avoid strenuous activity, follow-up with cardiologist"
}
```

**Response:**
- Returns a PDF file for download with formatted medical report

---

### GET /api/status

**System Status Check** - Verify API and model initialization

**Response:**
```json
{
  "message": "Medical Chatbot API",
  "status": "running",
  "version": "1.0.0",
  "models": {
    "gemini_client_initialized": true,
    "vision_model": "gemini-2.5-flash",
    "chat_model": "gemini-2.5-flash"
  }
}
```

---

## 📁 Project Structure

```
MedAssist/
├── back/                          # Backend (FastAPI)
│   ├── main.py                   # Main API application
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # Environment variables (create this)
│
├── front/                         # Frontend (React + Vite)
│   ├── src/
│   │   ├── components/           # Reusable React components
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── MessageInput.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── PatientList.jsx
│   │   ├── pages/                # Page components
│   │   │   ├── Home.jsx
│   │   │   ├── Chat.jsx
│   │   │   └── About.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
└── README.md                      # This file
```

---

## 🎨 User Interface

### Home Page
- Hero section with welcome message
- Feature cards highlighting capabilities
- Quick-start button to begin consultations

### Chat Interface
- Patient information form (name, age, gender, symptoms)
- Real-time message display
- File upload for medical images
- Report type selection dropdown
- PDF report generation

### Component Hierarchy
```
App
├── Home
├── Chat
│   └── ChatInterface
│       ├── ChatWindow
│       └── MessageInput
├── About
└── Navbar
```

---

## 🔐 Security Considerations

### Current Implementation
- CORS is enabled for all origins (*)
- Environment variables for API keys
- Input validation for file uploads

### Production Recommendations
- 🔒 Restrict CORS to specific frontend domain
- 🔐 Implement authentication and authorization
- 🛡️ Add rate limiting to API endpoints
- 📝 Validate all user inputs on backend
- 🔑 Rotate API keys regularly
- 📊 Implement logging and monitoring

### Important Notes
- Never commit `.env` files to version control
- Store sensitive API keys securely
- Use HTTPS in production
- Implement HIPAA compliance if handling real patient data

---

## 🚦 Getting Help

### Common Issues

**Backend won't start**
```bash
# Clear cache and reinstall
rm -r venv
python -m venv venv
pip install -r requirements.txt
```

**API connection errors**
- Verify backend is running: `http://127.0.0.1:8000/docs`
- Check vite proxy configuration in `vite.config.js`
- Ensure CORS middleware is properly configured

**Gemini API errors**
- Verify API key is correct in `.env`
- Check API key has proper permissions
- Ensure API is enabled in Google Cloud Console

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Google Gemini API Guide](https://ai.google.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)

---

## 🤝 Contributing

Contributions are welcome! Here's how to help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use React functional components with hooks
- Include comments for complex logic
- Test changes before submitting PR
- Update documentation as needed

---

## ⚠️ Medical Disclaimer

**MedAssist is NOT a substitute for professional medical advice.** This platform:
- Provides general information only
- Should not be used for diagnosis or treatment decisions
- Cannot replace consultation with licensed healthcare providers
- Is designed for educational purposes

**Always consult with qualified healthcare professionals for proper medical evaluation and treatment.**

---

## 👨‍💻 About

MedAssist is an AI-powered medical consultation assistant that demonstrates the capabilities of modern AI in healthcare informatics. Built with modern web technologies and powered by Google's Gemini AI.

---

<div align="center">

**[⬆ Back to Top](#medassist---ai-powered-medical-consultation-platform)**

Made with ❤️ By Avijit0001

</div>
