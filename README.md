# AI-Powered Recruitment Platform

An intelligent recruitment system that automates candidate screening, detects hiring bias, and provides diversity insights for HR teams.

## Features

- **AI-Powered Resume Parsing** - Automatic skill extraction and candidate profiling
- **Smart Matching Algorithm** - TF-IDF vectorization with cosine similarity scoring
- **Bias Detection** - Real-time alerts for potential hiring discrimination
- **Diversity Analytics** - Shannon entropy-based diversity scoring
- **Real-time Dashboard** - Live candidate rankings and status updates
- **Email Automation** - Automated notifications for shortlisting and rejections
- **AI Assistant** - Contextual recruitment guidance and insights

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight database
- **spaCy** - Natural Language Processing
- **scikit-learn** - Machine learning algorithms
- **PyPDF2 & python-docx** - Document parsing
- **SMTP & Jinja2** - Email templating and delivery
- **Google Generative AI** - AI assistant integration

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern UI component library
- **Lucide React** - Icon library

## Project Structure

```
talent-matcher/
├── backend/
│   ├── api/
│   │   ├── candidate.py      # Candidate status management
│   │   ├── dashboard.py      # Analytics and insights
│   │   ├── jd.py            # Job description handling
│   │   ├── resume.py        # Resume upload and processing
│   │   └── ai_assistant.py  # AI chat functionality
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   ├── db.py           # Database connection
│   │   └── models.py       # SQLAlchemy models
│   ├── services/
│   │   ├── ai_assistant.py  # AI service logic
│   │   ├── mailer.py       # Email services
│   │   ├── matcher.py      # Matching algorithms
│   │   └── parser.py       # Resume parsing
│   ├── uploads/            # File storage
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js app router pages
│   │   ├── components/    # Reusable UI components
│   │   └── lib/          # Utility functions
│   ├── package.json      # Node.js dependencies
│   └── tailwind.config.js # Tailwind configuration
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings:
   # - GEMINI_API_KEY (for AI assistant)
   # - EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD (for notifications)
   ```

6. **Start the backend server**
   ```bash
   python main.py
   ```
   Server runs on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   Application runs on `http://localhost:3000`

## User Workflow

### 1. Upload Job Description
- Navigate to `/upload-jd`
- Upload JD file or paste text
- System extracts required skills automatically
- JD becomes active for candidate matching

### 2. Upload Candidate Resumes
- Navigate to `/upload-resume`
- Select target job description
- Upload resume file (PDF/DOCX)
- Fill candidate details (auto-populated from resume)
- System creates match score against selected JD

### 3. Review Dashboard
- Navigate to `/dashboard`
- View ranked candidates by match score
- Monitor bias alerts and diversity metrics
- Use AI assistant for insights

### 4. Manage Candidates
- Update candidate status (Pending → Shortlisted → Rejected/Accepted)
- Bulk shortlist multiple candidates
- Automatic email notifications sent
- Real-time dashboard updates

<img width="3840" height="1506" alt="Untitled diagram _ Mermaid Chart-2025-09-06-173231" src="https://github.com/user-attachments/assets/1361e739-8178-4502-be13-4668c5258de8" />



## API Endpoints

### Job Description Management
```
POST   /jd/upload              # Upload job description
GET    /jd/                    # Get all job descriptions
GET    /jd/{jd_id}            # Get specific job description
```

### Resume & Candidate Management
```
POST   /resume/extract         # Extract resume details for auto-fill
POST   /resume/upload          # Upload resume and create candidate
GET    /resume/                # Get all candidates
GET    /resume/{candidate_id}  # Get specific candidate details
PATCH  /candidate/status       # Update candidate status
GET    /candidate/statuses     # Get status distribution
```

### Dashboard & Analytics
```
GET    /dashboard/candidates   # Get ranked candidates
GET    /dashboard/insights     # Get comprehensive analytics
GET    /dashboard/bias-alerts  # Get bias detection results
GET    /dashboard/diversity-metrics  # Get diversity analysis
GET    /dashboard/skills-heatmap     # Get skills gap analysis
POST   /dashboard/shortlist    # Bulk shortlist candidates
GET    /dashboard/candidate/{id}/details  # Detailed candidate view
```

### AI Assistant
```
POST   /ai/chat               # Chat with AI assistant
GET    /ai/suggestions        # Get contextual suggestions
GET    /ai/status            # Get AI service status
```

## AI & Machine Learning

### Resume Parsing
- **spaCy NLP** for named entity recognition
- **Regular expressions** for contact information extraction
- **Keyword matching** for skill identification
- **Experience calculation** from date patterns

### Matching Algorithm
- **TF-IDF Vectorization** for skill comparison
- **Cosine Similarity** for compatibility scoring
- **Weighted scoring**: Skills (70%) + Experience (30%)
- **Gap analysis** with learning suggestions

### Bias Detection
- **Gender distribution** monitoring
- **Experience bias** detection
- **Education background** analysis
- **Severity classification** (Low/Medium/High)

### Diversity Scoring
- **Shannon Entropy** algorithm
- **Multi-factor analysis**: Gender (40%) + Experience (35%) + Education (25%)
- **Real-time recalculation** with new candidates

## Email Configuration

Configure SMTP settings in `.env`:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

### Email Templates
- **Shortlist notifications** with interview details
- **Rejection emails** with feedback
- **Professional HTML formatting**

## Configuration

### Environment Variables
```env
# AI Assistant
GEMINI_API_KEY=your-gemini-api-key

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Database
DATABASE_URL=sqlite:///./talent_matcher.db
```

## Deployment

### Backend Deployment
```bash
# Production server
uvicorn main:app --host 0.0.0.0 --port 8000

# With auto-reload for development
uvicorn main:app --reload
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Start production server
npm start
```

## Database Schema

### Core Tables
- **candidates** - Candidate information and extracted data
- **jds** - Job descriptions and requirements
- **match_results** - Matching scores and analysis
- **bias_alerts** - Bias detection results
- **diversity_metrics** - Diversity analysis data

## AI Assistant Setup

1. **Get Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create new API key
   - Add to `.env` file

2. **Features**
   - Context-aware responses about candidates
   - Recruitment insights and recommendations
   - Bias analysis explanations
   - Suggested questions based on dashboard state
  
## Screenshot / Preview
<img width="2940" height="7846" alt="screencapture-localhost-3000-dashboard-2025-09-06-23_07_54" src="https://github.com/user-attachments/assets/a09d3e40-0c07-4098-a4c4-5cde7fb5920d" />



