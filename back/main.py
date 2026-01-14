from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
from PIL import Image
import io
import os
import json
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import tempfile
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Global variables
gemini_client = None
gemini_vision_model_name = 'gemini-2.5-flash'
gemini_chat_model_name = 'gemini-2.5-flash'

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    
class ChatResponse(BaseModel):
    response: str
    timestamp: str
    xray_analysis: Optional[str] = None

class ReportRequest(BaseModel):
    patient_name: str
    patient_age: int
    patient_gender: str
    symptoms: str
    diagnosis: str
    xray_analysis: Optional[str] = None
    medications: List[str]
    instructions: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Gemini client on startup"""
    global gemini_client

    try:
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        print("🔄 Initializing Gemini Client...")
        
        # Initialize Gemini client
        gemini_client = genai.Client(api_key=api_key)
        print("✅ Gemini Client initialized successfully!")

    except Exception as e:
        print(f"❌ Error initializing Gemini client: {e}")
        raise

    yield
    
    # Cleanup on shutdown
    print("🔄 Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Medical Chatbot API",
    description="AI-powered medical chatbot with X-ray analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== HELPER FUNCTIONS ====================

def format_markdown_for_pdf(text: str) -> str:
    """
    Convert basic Markdown to ReportLab-compatible XML tags
    """
    if not text:
        return ""
    
    # Escape basic HTML characters
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Bold: **text** -> <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Italic: *text* -> <i>text</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    # Lists: - item or * item -> <br/>• item
    text = re.sub(r'(?m)^[-*]\s+', r'<br/>&bull; ', text)
    
    # Newlines -> <br/>
    text = text.replace('\n', '<br/>')
    
    return text

async def analyze_xray_image(image: Image.Image) -> str:
    """
    Analyze X-ray image using Gemini Vision model
    """
    try:
        if not gemini_client:
            raise Exception("Gemini client not initialized")
        
        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Prepare prompt for X-ray analysis
        analysis_prompt = """You are an expert radiologist. Analyze this X-ray image and provide detailed, accurate medical observations.

Please describe:
1. Key anatomical structures visible
2. Any abnormalities or concerning findings
3. Potential clinical diagnoses
4. Recommendations for further evaluation if needed

Provide a thorough but concise analysis."""
        
        # Get analysis from Gemini Vision model
        vision_response = gemini_client.models.generate_content(
            model=gemini_vision_model_name,
            contents=[analysis_prompt, image]
        )
        
        analysis = vision_response.text
        
        return analysis
        
    except Exception as e:
        raise Exception(f"X-ray analysis failed: {str(e)}")


def build_chat_messages(message: str, history: List[ChatMessage], xray_analysis: Optional[str] = None) -> str:
    """
    Build comprehensive prompt with conversation history and optional X-ray analysis
    """
    system_context = """You are an experienced medical professional and healthcare advisor with expertise in:
- General medicine and common health conditions
- Symptom analysis and differential diagnosis
- Medication information and treatment guidelines
- Radiology and medical imaging interpretation
- Patient education and preventive care

Guidelines:
- Provide accurate, evidence-based medical information
- Be empathetic, clear, and professional
- Always remind users that this is for informational purposes only
- Recommend consulting healthcare professionals for proper diagnosis and treatment
- If discussing X-ray findings, integrate them naturally into your medical assessment
- Use clear, non-technical language when possible, but include medical terms when necessary
"""
    
    # Build conversation context
    conversation_context = ""
    if history:
        conversation_context = "\n\nPrevious conversation:\n"
        for msg in history[-5:]:  # Last 5 messages for context
            role_label = "Patient" if msg.role == "user" else "Doctor"
            conversation_context += f"{role_label}: {msg.content}\n"
    
    # Add X-ray analysis if available
    xray_context = ""
    if xray_analysis:
        xray_context = f"\n\nX-RAY ANALYSIS RESULTS:\n{xray_analysis}\n\nPlease integrate these imaging findings into your medical assessment and recommendations.\n"
    
    # Combine all parts
    full_prompt = f"""{system_context}{conversation_context}{xray_context}

Current Patient Message: {message}

Provide your medical assessment and recommendations:"""
    
    return full_prompt


# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check and API information"""
    return {
        "message": "Medical Chatbot API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /api/chat - Send messages and optionally analyze X-rays",
            "generate_report": "POST /api/generate-report - Generate PDF medical reports",
            "status": "GET /api/status - Check system status"
        },
        "models": {
            "gemini_client_initialized": gemini_client is not None,
            "vision_model": gemini_vision_model_name,
            "chat_model": gemini_chat_model_name
        }
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(...),
    conversation_history: str = Form(default="[]"),
    xray_image: Optional[UploadFile] = File(default=None)
):
    """
    Unified chat endpoint that handles both text conversations and X-ray analysis
    
    Parameters:
    - message: The user's text message
    - conversation_history: JSON string of previous messages (optional)
    - xray_image: X-ray image file for analysis (optional)
    
    Returns:
    - response: AI-generated medical response
    - xray_analysis: X-ray analysis results if image was provided
    - timestamp: Response timestamp
    """
    try:
        # Validate client is initialized
        if not gemini_client:
            raise HTTPException(status_code=503, detail="Gemini client not initialized")
        
        # Parse conversation history
        try:
            history = json.loads(conversation_history)
            history = [ChatMessage(**msg) for msg in history]
        except json.JSONDecodeError:
            history = []
        
        xray_analysis_result = None
        
        # Process X-ray image if provided
        if xray_image:
            # Validate file type
            if not xray_image.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Uploaded file must be an image")
            
            try:
                # Read and analyze X-ray
                contents = await xray_image.read()
                image = Image.open(io.BytesIO(contents))
                xray_analysis_result = await analyze_xray_image(image)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"X-ray analysis failed: {str(e)}")
        
        # Build comprehensive prompt
        full_prompt = build_chat_messages(message, history, xray_analysis_result)
        
        # Get response from Gemini chat model
        try:
            response = gemini_client.models.generate_content(
                model=gemini_chat_model_name,
                contents=full_prompt
            )
            ai_response = response.text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chat model error: {str(e)}")
        
        return ChatResponse(
            response=ai_response,
            xray_analysis=xray_analysis_result,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/api/generate-report")
async def generate_report(report: ReportRequest):
    """
    Generate a professional medical prescription/report PDF
    
    Parameters:
    - patient_name: Full name of the patient
    - patient_age: Age in years
    - patient_gender: Gender
    - symptoms: Chief complaints and symptoms
    - diagnosis: Medical diagnosis
    - xray_analysis: X-ray findings (optional)
    - medications: List of prescribed medications with dosage
    - instructions: Treatment instructions and follow-up advice
    
    Returns:
    - PDF file download
    """
    try:
        # Create temporary PDF file
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_path = temp_pdf.name
        temp_pdf.close()
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Header Section
        title = Paragraph("MEDICAL PRESCRIPTION & REPORT", title_style)
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Date and Report ID
        report_id = f"MR{datetime.now().strftime('%Y%m%d%H%M%S')}"
        date_time = Paragraph(
            f"<b>Report ID:</b> {report_id}<br/><b>Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
            styles['Normal']
        )
        story.append(date_time)
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Information Table
        story.append(Paragraph("Patient Information", heading_style))
        
        patient_data = [
            ["Name:", report.patient_name],
            ["Age:", f"{report.patient_age} years"],
            ["Gender:", report.patient_gender],
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4.5*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Chief Complaints
        story.append(Paragraph("Chief Complaints", heading_style))
        story.append(Paragraph(format_markdown_for_pdf(report.symptoms), styles['Normal']))
        story.append(Spacer(1, 0.25*inch))
        
        # X-ray Analysis (if provided)
        if report.xray_analysis:
            story.append(Paragraph("Radiological Findings", heading_style))
            # Handle long text by wrapping in paragraph
            xray_para = Paragraph(format_markdown_for_pdf(report.xray_analysis), styles['Normal'])
            story.append(xray_para)
            story.append(Spacer(1, 0.25*inch))
        
        # Diagnosis
        story.append(Paragraph("Medical Diagnosis", heading_style))
        diagnosis_para = Paragraph(format_markdown_for_pdf(report.diagnosis), styles['Normal'])
        story.append(diagnosis_para)
        story.append(Spacer(1, 0.25*inch))
        
        # Prescribed Medications
        story.append(Paragraph("Prescribed Medications", heading_style))
        
        # Create medication table for better formatting
        med_data = [[f"{i}.", format_markdown_for_pdf(med)] for i, med in enumerate(report.medications, 1)]
        med_table = Table(med_data, colWidths=[0.5*inch, 6*inch])
        med_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(med_table)
        story.append(Spacer(1, 0.25*inch))
        
        # Instructions and Advice
        story.append(Paragraph("Instructions & Follow-up Advice", heading_style))
        instructions_para = Paragraph(format_markdown_for_pdf(report.instructions), styles['Normal'])
        story.append(instructions_para)
        story.append(Spacer(1, 0.4*inch))
        
        # Important Notice
        story.append(Spacer(1, 0.3*inch))
        
        notice_style = ParagraphStyle(
            'Notice',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            borderWidth=1,
            borderColor=colors.HexColor('#cccccc'),
            borderPadding=10,
            backColor=colors.HexColor('#f9f9f9')
        )
        
        notice = Paragraph(
            "<b>IMPORTANT NOTICE:</b> This is an AI-generated medical report for reference purposes only. "
            "It should not replace professional medical advice, diagnosis, or treatment. Always consult "
            "with qualified healthcare professionals for medical concerns. This report does not constitute "
            "a doctor-patient relationship.",
            notice_style
        )
        story.append(notice)
        
        # Build PDF
        doc.build(story)
        
        # Generate filename
        safe_name = report.patient_name.replace(' ', '_').replace('/', '_')
        filename = f"Medical_Report_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Return PDF file
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        # Cleanup temp file on error
        if 'pdf_path' in locals() and os.path.exists(pdf_path):
            os.unlink(pdf_path)
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")


@app.get("/api/status")
async def get_status():
    """
    Check system and model status
    """
    return {
        "status": "operational",
        "gemini": {
            "client_initialized": gemini_client is not None,
            "vision_model": gemini_vision_model_name,
            "chat_model": gemini_chat_model_name,
        },
        "system": {
            "api_key_configured": os.getenv("GEMINI_API_KEY") is not None,
        },
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Medical Chatbot API...")
    print("🌐 Server will be available at: http://127.0.0.1:8000")
    print("📚 API Documentation: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)