import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';

function LoginForm() {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [selectedRole, setSelectedRole] = useState('client');
    const [registrationNo, setRegistrationNo] = useState('');
    const [secretKey, setSecretKey] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const payload = {
                email,
                password,
                role: selectedRole,
            };

            if (selectedRole === 'lawfirm') {
                payload.registration_no = registrationNo;
            }
            if (selectedRole === 'admin') {
                payload.secret_key = secretKey;
            }

            const response = await API.post('accounts/login/', payload);

            if (response.data.access) {
                localStorage.setItem('access_token', response.data.access);
                localStorage.setItem('refresh_token', response.data.refresh);
                localStorage.setItem('user', JSON.stringify(response.data.user));
                localStorage.setItem('role', response.data.user.role);

                const userRole = response.data.user.role;
                const isOnboarded = response.data.user.is_onboarded;
                const status = response.data.user.status;

                // ✅ Redirect based on role and status
                if (userRole === 'admin') {
                    navigate('/admin-dashboard');
                } else if (userRole === 'client') {
                    if (status === 'approved') {
                        navigate('/client-portal');
                    } else if (status === 'pending') {
                        navigate('/pending-onboarding');
                    } else {
                        navigate('/client-onboarding');
                    }
                } else if (userRole === 'lawfirm') {
                    if (isOnboarded && status === 'approved') {
                        navigate('/lawfirm-portal');
                    } else if (status === 'pending') {
                        navigate('/lawfirm-pending-onboarding');
                    } else {
                        navigate('/lawfirm-onboarding');
                    }
                }
            }
        } catch (err) {
            console.error('Login error:', err);
            setError(err.response?.data?.error || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className="auth-role-container">
                <div className="auth-role-title">I am a</div>
                <div className="auth-role-buttons">
                    <button
                        type="button"
                        className={`auth-role-btn client ${selectedRole === 'client' ? 'active' : ''}`}
                        onClick={() => setSelectedRole('client')}
                    >
                        <i className="fas fa-user"></i> Client
                    </button>
                    <button
                        type="button"
                        className={`auth-role-btn lawyer ${selectedRole === 'lawfirm' ? 'active' : ''}`}
                        onClick={() => setSelectedRole('lawfirm')}
                    >
                        <i className="fas fa-gavel"></i> Law Firm / Lawyer
                    </button>
                    <button
                        type="button"
                        className={`auth-role-btn admin ${selectedRole === 'admin' ? 'active' : ''}`}
                        onClick={() => setSelectedRole('admin')}
                    >
                        <i className="fas fa-user-shield"></i> Admin
                    </button>
                </div>
            </div>

            <div className="auth-form-group">
                <label className="auth-form-label">Email</label>
                <input
                    type="email"
                    className="auth-form-control"
                    value={email}
                    autocomplete="off"
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
            </div>

            {selectedRole === 'lawfirm' && (
                <div className="auth-form-group">
                    <label className="auth-form-label">Registration Number</label>
                    <input
                        type="text"
                        className="auth-form-control"
                        value={registrationNo}
                        onChange={(e) => setRegistrationNo(e.target.value)}
                        required
                    />
                </div>
            )}

            {selectedRole === 'admin' && (
                <div className="auth-form-group">
                    <label className="auth-form-label">Secret Key</label>
                    <input
                        type="password"
                        className="auth-form-control"
                        value={secretKey}
                        onChange={(e) => setSecretKey(e.target.value)}
                        required
                        placeholder="Enter admin secret key"
                    />
                </div>
            )}

            <div className="auth-form-group">
                <label className="auth-form-label">Password</label>
                <input
                    type="password"
                    className="auth-form-control"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
            </div>

            {error && <div className="error-message" style={{ color: 'red', marginBottom: '15px' }}>{error}</div>}

            <button type="submit" className="auth-submit-btn" disabled={loading}>
                {loading ? <i className="fas fa-spinner fa-spin"></i> : <i className="fas fa-sign-in-alt"></i>}
                {loading ? ' Signing In...' : ' Sign In'}
            </button>

            <div className="auth-links">
                <a href="#" className="auth-link">Forgot Password?</a>
                <a href="#" className="auth-link">Need Help?</a>
            </div>
        </form>
    );
}

export default LoginForm;
































