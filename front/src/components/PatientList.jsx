import { useState } from 'react';
import './PatientList.css';

const PatientList = ({ patients, activePatient, onSelectPatient, onNewChat }) => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredPatients = patients.filter(patient => 
    patient.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="patient-list">
      <div className="patient-list-header">
        <h2>Patient Chats</h2>
        <button className="new-chat-btn" onClick={onNewChat}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 5v14M5 12h14"></path>
          </svg>
          New Chat
        </button>
      </div>
      
      <div className="search-container">
        <input
          type="text"
          placeholder="Search patients..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>
      
      <div className="patients-container">
        {filteredPatients.length > 0 ? (
          filteredPatients.map(patient => (
            <div 
              key={patient.id}
              className={`patient-item ${activePatient === patient.id ? 'active' : ''}`}
              onClick={() => onSelectPatient(patient.id)}
            >
              <div className="patient-avatar">
                {patient.name.charAt(0).toUpperCase()}
              </div>
              <div className="patient-info">
                <h3>{patient.name}</h3>
                <p>{patient.lastMessage}</p>
              </div>
              <div className="patient-time">
                {patient.lastMessageTime}
              </div>
            </div>
          ))
        ) : (
          <div className="no-patients">
            {searchTerm ? 'No matching patients found' : 'No patient chats yet'}
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientList;