import './About.css';

const About = () => {
  return (
    <div className="about-container">
      <h1>About MedAssist</h1>
      
      <section className="about-section">
        <h2>Our Mission</h2>
        <p>
          MedAssist aims to make preliminary medical information more accessible through 
          AI-powered consultations. We strive to provide a supportive platform where users 
          can discuss their health concerns and receive informative guidance.
        </p>
      </section>
      
      <section className="about-section">
        <h2>How It Works</h2>
        <p>
          Our AI assistant uses advanced natural language processing and medical knowledge 
          to provide informative responses to your health questions. You can also upload 
          images for analysis, making it easier to discuss visual symptoms.
        </p>
      </section>
      
      <section className="about-section disclaimer">
        <h2>Important Disclaimer</h2>
        <p>
          MedAssist is designed to provide information and support, not to replace 
          professional medical advice. The AI assistant can help you understand general 
          medical concepts and provide preliminary insights, but it should not be used 
          for diagnosis or treatment decisions.
        </p>
        <p>
          Always consult with qualified healthcare professionals for medical concerns. 
          In case of emergency, contact your local emergency services immediately.
        </p>
      </section>
      
      <section className="about-section">
        <h2>Contact Us</h2>
        <p>
          If you have any questions or feedback about MedAssist, please contact us at:
          <br />
          <a href="mailto:support@medassist.example.com">support@medassist.example.com</a>
        </p>
      </section>
    </div>
  );
};

export default About;