import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';

function LawfirmPendingOnboarding() {
    const navigate = useNavigate();
    const [onboardingData, setOnboardingData] = useState(null);
    const [status, setStatus] = useState('pending');
    const [loading, setLoading] = useState(true);
    let pollingInterval = null;

    useEffect(() => {
        let isMounted = true;

        const checkStatus = async () => {
            try {
                const token = localStorage.getItem('access_token');
                if (!token) {
                    navigate('/');
                    return;
                }

                const storedData = localStorage.getItem('lawfirm_onboarding_data');
                if (storedData && isMounted) {
                    setOnboardingData(JSON.parse(storedData));
                }

                const response = await API.get('profiles/lawfirm-status/');
                if (isMounted) {
                    setStatus(response.data.status);
                    
                    if (response.data.status === 'approved') {
                        if (pollingInterval) clearInterval(pollingInterval);
                        localStorage.removeItem('lawfirm_onboarding_data');
                        localStorage.removeItem('lawfirm_onboarding_status');
                        navigate('/lawfirm-portal');
                    } else if (response.data.status === 'rejected') {
                        if (pollingInterval) clearInterval(pollingInterval);
                        localStorage.setItem('lawfirm_onboarding_message', 'Your application was rejected. Please fill valid credentials.');
                        localStorage.removeItem('lawfirm_onboarding_data');
                        localStorage.removeItem('lawfirm_onboarding_status');
                        navigate('/lawfirm-onboarding');
                    }
                }
            } catch (error) {
                console.error('Error checking status:', error);
            } finally {
                if (isMounted) setLoading(false);
            }
        };

        checkStatus();
        pollingInterval = setInterval(checkStatus, 5000);
        
        return () => {
            isMounted = false;
            if (pollingInterval) clearInterval(pollingInterval);
        };
    }, [navigate]);

    if (loading) {
        return (
            <div className="lawfirm-pending-container">
                <div className="lawfirm-pending-card">
                    <div className="spinner"></div>
                    <h2>Loading...</h2>
                </div>
            </div>
        );
    }

    return (
        <div className="lawfirm-pending-container">
            <div className="lawfirm-pending-card">
                <div className="lawfirm-pending-icon">
                    <i className="fas fa-building"></i>
                </div>
                <h2 className="lawfirm-pending-title">Firm Application Under Review</h2>
                <p className="lawfirm-pending-subtitle">
                    Thank you for submitting your law firm details. Our admin team is reviewing your application.
                </p>
                
                <div className="lawfirm-pending-badge">
                    <i className="fas fa-hourglass-half me-2"></i> 
                    Status: Pending Admin Verification
                </div>
                
                {onboardingData && (
                    <div className="lawfirm-pending-details">
                        <p><strong>Submitted on:</strong> {new Date(onboardingData.submitted_at).toLocaleString()}</p>
                        <p><strong>Firm Name:</strong> {onboardingData.firm_name}</p>
                        <p><strong>Registration No:</strong> {onboardingData.registration_no}</p>
                        <p><strong>Primary Lawyer:</strong> {onboardingData.primary_lawyer_name}</p>
                    </div>
                )}
                
                <div className="lawfirm-pending-info-box">
                    <i className="fas fa-info-circle"></i>
                    <div className="lawfirm-pending-info-content">
                        <p><strong>What happens next?</strong></p>
                        <p>Our team will verify your firm's credentials and documents. This process typically takes 2-3 business days.</p>
                    </div>
                </div>
                
                <p className="lawfirm-pending-note">
                    You will receive an email notification once your firm is verified and approved.
                </p>
                
                <div className="lawfirm-pending-warning">
                    <div className="lawfirm-pending-warning-item">
                        <i className="fas fa-lock"></i> Dashboard will be read-only until approval
                    </div>
                    <div className="lawfirm-pending-warning-item">
                        <i className="fas fa-ban"></i> Cannot accept new cases until verified
                    </div>
                </div>
                
                <button className="lawfirm-pending-button" onClick={() => navigate('/')}>
                    <i className="fas fa-home me-2"></i> Back to Home
                </button>
            </div>
        </div>
    );
}

export default LawfirmPendingOnboarding;