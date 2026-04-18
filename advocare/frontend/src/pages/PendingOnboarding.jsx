import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';

function PendingOnboarding() {
    const navigate = useNavigate();
    const [onboardingData, setOnboardingData] = useState(null);
    const [status, setStatus] = useState('pending');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkStatus = async () => {
            try {
                const token = localStorage.getItem('access_token');
                if (!token) {
                    navigate('/');
                    return;
                }

                const storedData = localStorage.getItem('onboarding_data');
                if (storedData) {
                    setOnboardingData(JSON.parse(storedData));
                }

                const response = await API.get('profiles/client-status/');
                setStatus(response.data.status);
                
                if (response.data.status === 'approved') {
                    localStorage.removeItem('onboarding_data');
                    localStorage.removeItem('onboarding_status');
                    navigate('/client-portal');
                } else if (response.data.status === 'rejected') {
                    localStorage.setItem('onboarding_message', 'Your application was rejected. Please fill valid credentials.');
                    localStorage.removeItem('onboarding_data');
                    localStorage.removeItem('onboarding_status');
                    navigate('/client-onboarding');
                }
            } catch (error) {
                console.error('Error checking status:', error);
            } finally {
                setLoading(false);
            }
        };

        checkStatus();
        const interval = setInterval(checkStatus, 5000);
        return () => clearInterval(interval);
    }, [navigate]);

    if (loading) {
        return (
            <div className="pending-container">
                <div className="pending-card">
                    <div className="spinner"></div>
                    <h2>Loading...</h2>
                </div>
            </div>
        );
    }

    return (
        <div className="pending-container">
            <div className="pending-card">
                <div className="pending-icon">
                    <i className="fas fa-clock"></i>
                </div>
                <h2 className="pending-title">Application Under Review</h2>
                <p className="pending-subtitle">
                    Thank you for submitting your details. Our team is reviewing your application.
                </p>
                
                <div className="pending-badge">
                    <i className="fas fa-hourglass-half me-2"></i> 
                    Status: Pending Admin Review
                </div>
                
                {onboardingData && (
                    <div className="pending-details">
                        <p><strong>Submitted on:</strong> {new Date(onboardingData.submitted_at).toLocaleString()}</p>
                        <p><strong>Case Title:</strong> {onboardingData.case_title}</p>
                        <p><strong>Case Type:</strong> {onboardingData.case_type}</p>
                    </div>
                )}
                
                <p className="pending-note">
                    You will receive an email notification once your application is approved.
                </p>
                
                <button className="pending-button" onClick={() => navigate('/')}>
                    <i className="fas fa-home me-2"></i> Back to Home
                </button>
            </div>
        </div>
    );
}

export default PendingOnboarding;











// import React, { useState, useEffect } from 'react';
// import { useNavigate } from 'react-router-dom';
// import API from '../services/api';

// function PendingOnboarding() {
//     const navigate = useNavigate();
//     const [onboardingData, setOnboardingData] = useState(null);
//     const [status, setStatus] = useState('pending');
//     const [loading, setLoading] = useState(true);

//     useEffect(() => {
//         const checkStatus = async () => {
//             try {
//                 const token = localStorage.getItem('access_token');
//                 if (!token) {
//                     navigate('/');
//                     return;
//                 }

//                 // Get stored onboarding data
//                 const storedData = localStorage.getItem('onboarding_data');
//                 if (storedData) {
//                     setOnboardingData(JSON.parse(storedData));
//                 }

//                 // Check client profile status
//                 const response = await API.get('profiles/client-status/');
//                 setStatus(response.data.status);
                
//                 // If approved, redirect to client portal
//                 if (response.data.status === 'approved') {
//                     localStorage.removeItem('onboarding_data');
//                     localStorage.removeItem('onboarding_status');
//                     navigate('/client-portal');
//                 }
//                 // If rejected, redirect to onboarding with message
//                 else if (response.data.status === 'rejected') {
//                     localStorage.setItem('onboarding_message', 'Your application was rejected. Please fill valid credentials.');
//                     localStorage.removeItem('onboarding_data');
//                     localStorage.removeItem('onboarding_status');
//                     navigate('/client-onboarding');
//                 }
//             } catch (error) {
//                 console.error('Error checking status:', error);
//             } finally {
//                 setLoading(false);
//             }
//         };

//         checkStatus();
        
//         // Poll every 5 seconds for status update
//         const interval = setInterval(checkStatus, 5000);
//         return () => clearInterval(interval);
//     }, [navigate]);

//     if (loading) {
//         return (
//             <div className="pending-container">
//                 <div className="pending-card">
//                     <div className="spinner"></div>
//                     <h2>Loading...</h2>
//                 </div>
//             </div>
//         );
//     }

//     return (
//         <div className="pending-container">
//             <div className="pending-card">
//                 <div className="pending-icon">
//                     <i className="fas fa-clock"></i>
//                 </div>
//                 <h2 className="pending-title">Application Under Review</h2>
//                 <p className="pending-subtitle">
//                     Thank you for submitting your details. Our team is reviewing your application.
//                 </p>
                
//                 <div className="pending-badge">
//                     <i className="fas fa-hourglass-half me-2"></i> 
//                     Status: Pending Admin Review
//                 </div>
                
//                 {onboardingData && (
//                     <div className="pending-details">
//                         <p><strong>Submitted on:</strong> {new Date(onboardingData.submitted_at).toLocaleString()}</p>
//                         <p><strong>Case Title:</strong> {onboardingData.case_title}</p>
//                         <p><strong>Case Type:</strong> {onboardingData.case_type}</p>
//                     </div>
//                 )}
                
//                 <p className="pending-note">
//                     You will receive an email notification once your application is approved.
//                 </p>
                
//                 <button className="pending-button" onClick={() => navigate('/')}>
//                     <i className="fas fa-home me-2"></i> Back to Home
//                 </button>
//             </div>
//         </div>
//     );
// }

// export default PendingOnboarding;