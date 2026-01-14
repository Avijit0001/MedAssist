import { useState, useRef } from 'react';
import ChatWindow from './ChatWindow';
import MessageInput from './MessageInput';
import './ChatInterface.css';

const ChatInterface = ({ messages = [], onSendMessage, onDownloadPrescription, title = 'Medical Assistant' }) => {
  const [reportType, setReportType] = useState('X-Ray');
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportFile, setReportFile] = useState(null);
  const [reportText, setReportText] = useState('');
  const fileInputRef = useRef(null);

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setReportFile({
          file: file,
          preview: reader.result
        });
        setReportText(`[Report Type: ${reportType}] `);
        setShowReportModal(true);
      };
      reader.readAsDataURL(file);
    }
    // Reset the input so the same file can be selected again if needed
    e.target.value = null;
  };

  const handleCloseModal = () => {
    setShowReportModal(false);
    setReportFile(null);
    setReportText('');
  };

  const handleConfirmReport = () => {
    if (reportFile) {
      onSendMessage({
        text: reportText || `[Report: ${reportType}] Uploaded ${reportFile.file.name}`,
        image: reportFile.preview,
        file: reportFile.file,
        sender: 'user',
        isReport: true,
        reportType: reportType
      });
      handleCloseModal();
    }
  };



  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="chat-title">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 3v12h-5c-.023 0-.047 0-.07.002a3.008 3.008 0 0 0-2.93 2.998v3l-6-3v-15h14Z"></path>
            <path d="m12.5 15 .134.972a1.2 1.2 0 0 0 1.173 1.028h1.193"></path>
          </svg>
          <h1>{title}</h1>
        </div>

        <div className="chat-actions">
          <div className="report-group">
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="report-select"
            >
              <option value="X-Ray">X-Ray</option>
              <option value="CT Scan">CT Scan</option>
              <option value="MRI">MRI</option>
              <option value="Blood Test">Blood Test</option>
              <option value="Ultrasound">Ultrasound</option>
            </select>
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              accept="image/*"
              onChange={handleFileChange}
            />
            <button onClick={handleUploadClick} className="action-btn submit-btn">
              Submit Report
            </button>
          </div>

          <button onClick={onDownloadPrescription} className="action-btn download-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Download Prescription
          </button>
        </div>
      </div>
      <ChatWindow messages={messages} />
      <MessageInput onSendMessage={onSendMessage} />

      {showReportModal && (
        <div className="report-modal-overlay">
          <div className="report-modal">
            <div className="modal-header">
              <h3>Submit {reportType} Report</h3>
              <button onClick={handleCloseModal} className="close-modal-btn">&times;</button>
            </div>
            <div className="modal-body">
              {reportFile && (
                <div className="report-preview-container">
                  <img src={reportFile.preview} alt="Report Preview" className="report-preview-img" />
                </div>
              )}
              <div className="report-info">
                <strong>File:</strong> {reportFile?.file.name}
              </div>
              <textarea
                className="report-text-input"
                placeholder="Add a description or note about this report..."
                value={reportText}
                onChange={(e) => setReportText(e.target.value)}
                autoFocus
              ></textarea>
            </div>
            <div className="modal-footer">
              <button onClick={handleCloseModal} className="modal-btn cancel-btn">Cancel</button>
              <button onClick={handleConfirmReport} className="modal-btn send-report-btn">
                Send Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;