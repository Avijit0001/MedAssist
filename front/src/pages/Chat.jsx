import { useState } from 'react';
import ChatInterface from '../components/ChatInterface';
import './Chat.css';

const Chat = () => {
  const [userDetails, setUserDetails] = useState({
    name: '',
    age: '',
    gender: '',
    complaints: ''
  });
  const [isFormSubmitted, setIsFormSubmitted] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserDetails(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (userDetails.name && userDetails.age && userDetails.gender && userDetails.complaints) {
      setIsFormSubmitted(true);
      setMessages([
        {
          text: `Hello ${userDetails.name}! I've noted that you are a ${userDetails.age} year old ${userDetails.gender} experiencing "${userDetails.complaints}". I'm here to assist you. Please tell me more about your symptoms or upload any relevant medical images.`,
          sender: 'bot'
        }
      ]);
    }
  };

  const handleSendMessage = async (newMessage) => {
    setMessages(prev => [...prev, newMessage]);
    setIsLoading(true);

    try {
      let botResponseText = "";
      let xrayAnalysisText = "";
      let xrayAnalysisResult = null;

      // Prepare FormData for the unified /api/chat endpoint
      const formData = new FormData();
      formData.append('message', newMessage.text || "Please analyze this image."); // Fallback text if only image

      // Prepare history
      const chatHistory = messages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text
      }));
      formData.append('conversation_history', JSON.stringify(chatHistory));

      // Append image if present
      if (newMessage.file) {
        formData.append('xray_image', newMessage.file);
      }

      const response = await fetch('/api/chat', {
        method: 'POST',
        body: formData, // No Content-Type header, browser sets it with boundary
      });

      if (!response.ok) throw new Error('Chat failed');

      const data = await response.json();
      botResponseText = data.response;
      xrayAnalysisResult = data.xray_analysis;

      if (xrayAnalysisResult) {
        xrayAnalysisText = `\n\n**X-Ray Analysis:**\n${xrayAnalysisResult}`;
        botResponseText += xrayAnalysisText;
      }

      setMessages(prev => [...prev, {
        text: botResponseText,
        sender: 'bot',
        xrayAnalysis: xrayAnalysisResult // Store raw analysis for report generation
      }]);

    } catch (error) {
      console.error("Error:", error);
      setMessages(prev => [...prev, {
        text: "I apologize, but I encountered an error processing your request. Please try again.",
        sender: 'bot',
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPrescription = async () => {
    setIsLoading(true);
    try {
      // 1. Extract structured data using the chat model
      const chatHistory = messages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text
      }));

      const extractionPrompt = `
        Based on the conversation history, please generate a JSON object for a medical report.
        The JSON MUST have these exact fields:
        - "diagnosis": (string) The likely diagnosis based on symptoms and analysis.
        - "medications": (list of strings) Recommended medications.
        - "instructions": (string) Patient instructions and advice.
        
        If specific details were not discussed, infer reasonable general medical advice based on the symptoms (${userDetails.complaints}).
        Output ONLY the raw JSON string, no markdown formatting or explanations.
      `;

      const formData = new FormData();
      formData.append('message', extractionPrompt);
      formData.append('conversation_history', JSON.stringify(chatHistory));

      const extractionResponse = await fetch('/api/chat', {
        method: 'POST',
        body: formData,
      });

      if (!extractionResponse.ok) throw new Error('Failed to generate report data');

      const extractionData = await extractionResponse.json();
      let reportData = {};

      try {
        // Clean up potential markdown code blocks
        const cleanJson = extractionData.response.replace(/```json/g, '').replace(/```/g, '').trim();
        reportData = JSON.parse(cleanJson);
      } catch (e) {
        console.error("JSON Parse Error:", e);
        // Fallback data
        reportData = {
          diagnosis: "Consultation in progress",
          medications: ["As advised by physician"],
          instructions: "Please follow up with a specialist."
        };
      }

      // 2. Generate PDF
      // Find the most recent X-ray analysis from the messages
      const lastXrayAnalysis = messages
        .filter(m => m.xrayAnalysis)
        .pop()?.xrayAnalysis || null;

      const reportRequest = {
        patient_name: userDetails.name,
        patient_age: parseInt(userDetails.age),
        patient_gender: userDetails.gender,
        symptoms: userDetails.complaints,
        diagnosis: reportData.diagnosis || "Pending Diagnosis",
        medications: reportData.medications || [],
        instructions: reportData.instructions || "No specific instructions.",
        xray_analysis: lastXrayAnalysis
      };

      const pdfResponse = await fetch('/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportRequest),
      });

      if (!pdfResponse.ok) throw new Error('Failed to generate PDF');

      // 3. Trigger Download
      const blob = await pdfResponse.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Medical_Report_${userDetails.name.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setMessages(prev => [...prev, {
        text: "[System] Prescription/Report downloaded successfully.",
        sender: 'bot',
        isSystem: true
      }]);

    } catch (error) {
      console.error("Report Error:", error);
      setMessages(prev => [...prev, {
        text: "Failed to generate prescription. Please try again.",
        sender: 'bot',
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isFormSubmitted) {
    return (
      <div className="chat-page-container">
        <div className="details-form-card">
          <div className="form-header">
            <h2>Patient Intake</h2>
            <p>Please provide your details to start the consultation</p>
          </div>
          <form onSubmit={handleSubmit} className="details-form">
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={userDetails.name}
                onChange={handleInputChange}
                placeholder="e.g. John Doe"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="age">Age</label>
                <input
                  type="number"
                  id="age"
                  name="age"
                  value={userDetails.age}
                  onChange={handleInputChange}
                  placeholder="e.g. 30"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="gender">Gender</label>
                <select
                  id="gender"
                  name="gender"
                  value={userDetails.gender}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="complaints">Chief Complaints</label>
              <textarea
                id="complaints"
                name="complaints"
                value={userDetails.complaints}
                onChange={handleInputChange}
                placeholder="Describe your main symptoms..."
                rows="4"
                required
              ></textarea>
            </div>

            <button type="submit" className="start-chat-btn">
              Start Consultation
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-page-container">
      <div className="chat-area-full">
        <ChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          onDownloadPrescription={handleDownloadPrescription}
          title="Medical Assistant"
        />
        {isLoading && <div className="loading-indicator">Processing...</div>}
      </div>
    </div>
  );
};

export default Chat;