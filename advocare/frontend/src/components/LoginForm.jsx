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






































// import React, { useState } from "react";
// import axios from "axios";
// import { useNavigate } from "react-router-dom";

// function LoginForm() {
//   const navigate = useNavigate();
//   const [role, setRole] = useState("client");
//   const [formData, setFormData] = useState({
//     email: "",
//     password: "",
//     remember_me: false,
//     registration_no: "",
//     secret_key: "",
//   });
//   const [error, setError] = useState("");
//   const [showPassword, setShowPassword] = useState(false);

//   const handleChange = (e) => {
//     const { name, value, type, checked } = e.target;
//     setFormData({
//       ...formData,
//       [name]: type === "checkbox" ? checked : value,
//     });
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setError("");

//     const payload = {
//       email: formData.email,
//       password: formData.password,
//       role: role,
//     };
//     if (role === "lawfirm") payload.registration_no = formData.registration_no;
//     if (role === "admin") payload.secret_key = formData.secret_key;
//     if (formData.remember_me) payload.remember_me = true;

//     try {
//       const res = await axios.post("http://localhost:8000/accounts/login/", payload);
//       console.log("Login response:", res.data);

//       // Normalize role to lowercase (backend may return "Admin" or "admin")
//       const userRole = (res.data.role || role).toLowerCase();
//       localStorage.setItem("access_token", res.data.access);
//       localStorage.setItem("refresh_token", res.data.refresh);
//       localStorage.setItem("role", userRole);

//       if (res.data.user) {
//         localStorage.setItem("user", JSON.stringify(res.data.user));
//       }

//       let redirectPath = "/";
//       if (userRole === "client") redirectPath = "/client-dashboard";
//       else if (userRole === "lawfirm") redirectPath = "/lawfirm-dashboard";
//       else if (userRole === "admin") redirectPath = "/admin-dashboard";

//       console.log("Redirecting to:", redirectPath);

//       // First try React Router navigation
//       navigate(redirectPath);

//       // Fallback: if after 500ms the URL hasn't changed, force a hard redirect
//       setTimeout(() => {
//         if (window.location.pathname !== redirectPath) {
//           console.warn("Navigate didn't work, falling back to hard redirect");
//           window.location.href = redirectPath;
//         }
//       }, 500);
//     } catch (err) {
//       setError(err.response?.data?.error || "Login failed");
//     }
//   };

//   return (
//     <form onSubmit={handleSubmit} className="auth-form active">
//       {error && <div className="alert alert-error">{error}</div>}

//       <div className="auth-role-container">
//         <div className="auth-role-title">I am a</div>
//         <div className="auth-role-buttons">
//           <button
//             type="button"
//             className={`auth-role-btn client ${role === "client" ? "active" : ""}`}
//             onClick={() => setRole("client")}
//           >
//             <i className="fas fa-user"></i> Client
//           </button>
//           <button
//             type="button"
//             className={`auth-role-btn lawyer ${role === "lawfirm" ? "active" : ""}`}
//             onClick={() => setRole("lawfirm")}
//           >
//             <i className="fas fa-gavel"></i> Law Firm / Lawyer
//           </button>
//           <button
//             type="button"
//             className={`auth-role-btn admin ${role === "admin" ? "active" : ""}`}
//             onClick={() => setRole("admin")}
//           >
//             <i className="fas fa-user-shield"></i> Admin
//           </button>
//         </div>
//       </div>

//       <div className="auth-form-group">
//         <label className="auth-form-label" htmlFor="loginEmail">
//           Email
//         </label>
//         <input
//           type="email"
//           className="auth-form-control"
//           id="loginEmail"
//           name="email"
//           value={formData.email}
//           onChange={handleChange}
//           placeholder="Enter your email"
//           required
//         />
//       </div>

//       <div className="auth-form-group">
//         <label className="auth-form-label" htmlFor="loginPassword">
//           Password
//         </label>
//         <div className="password-container">
//           <input
//             type={showPassword ? "text" : "password"}
//             className="auth-form-control"
//             id="loginPassword"
//             name="password"
//             value={formData.password}
//             onChange={handleChange}
//             placeholder="Enter your password"
//             required
//           />
//           <button
//             type="button"
//             className="toggle-password"
//             onClick={() => setShowPassword(!showPassword)}
//           >
//             <i className={`fas ${showPassword ? "fa-eye-slash" : "fa-eye"}`}></i>
//           </button>
//         </div>
//       </div>

//       {role === "lawfirm" && (
//         <div className="auth-form-group">
//           <label className="auth-form-label required-field" htmlFor="registrationNo">
//             Registration Number
//           </label>
//           <input
//             type="text"
//             className="auth-form-control"
//             id="registrationNo"
//             name="registration_no"
//             value={formData.registration_no}
//             onChange={handleChange}
//             placeholder="Enter your bar registration number"
//             required
//           />
//         </div>
//       )}

//       {role === "admin" && (
//         <div className="auth-form-group">
//           <label className="auth-form-label required-field" htmlFor="secretKey">
//             Admin Secret Key
//           </label>
//           <input
//             type="password"
//             className="auth-form-control"
//             id="secretKey"
//             name="secret_key"
//             value={formData.secret_key}
//             onChange={handleChange}
//             placeholder="Enter admin secret key"
//             required
//           />
//           <small className="admin-note">Contact system administrator for secret key</small>
//         </div>
//       )}

//       <div className="checkbox-container">
//         <input
//           type="checkbox"
//           id="rememberMe"
//           name="remember_me"
//           checked={formData.remember_me}
//           onChange={handleChange}
//         />
//         <label className="checkbox-label" htmlFor="rememberMe">
//           Remember me on this device
//         </label>
//       </div>

//       <button type="submit" className="auth-submit-btn">Sign In</button>

//       <div className="auth-links">
//         <button className="auth-link" onClick={(e) => e.preventDefault()}>
//           Forgot Password?
//         </button>
//         <button className="auth-link" onClick={(e) => e.preventDefault()}>
//           Need Help?
//         </button>
//       </div>
//     </form>
//   );
// }

// export default LoginForm;



























// import React, { useState } from "react";
// import axios from "axios";
// import { useNavigate } from "react-router-dom";

// function LoginForm() {
//   const navigate = useNavigate();
//   const [role, setRole] = useState("client"); // "client", "lawfirm", "admin"
//   const [formData, setFormData] = useState({
//     username: "",
//     password: "",
//     remember_me: false,
//     registration_no: "",    // only for lawfirm
//     secret_key: "",         // only for admin
//   });
//   const [error, setError] = useState("");
//   const [showPassword, setShowPassword] = useState(false);

//   const handleChange = (e) => {
//     const { name, value, type, checked } = e.target;
//     setFormData({
//       ...formData,
//       [name]: type === "checkbox" ? checked : value,
//     });
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setError("");

//     const payload = {
//       username: formData.username,
//       password: formData.password,
//       remember_me: formData.remember_me,
//       role: role,
//     };
//     if (role === "lawfirm") payload.registration_no = formData.registration_no;
//     if (role === "admin") payload.secret_key = formData.secret_key;

//     try {
//       const res = await axios.post("http://localhost:8000/accounts/login/", payload);
//       localStorage.setItem("token", res.data.token);
//       localStorage.setItem("role", res.data.role);
//       if (res.data.role === "client") navigate("/client-dashboard");
//       else if (res.data.role === "lawfirm") navigate("/lawfirm-dashboard");
//       else if (res.data.role === "admin") navigate("/admin-dashboard");
//     } catch (err) {
//       setError(err.response?.data?.message || "Login failed");
//     }
//   };

//   return (
//     <form onSubmit={handleSubmit} className="auth-form active">
//       {error && <div className="alert alert-error">{error}</div>}

//       {/* Role Selector – uses existing auth-role classes */}
//       <div className="auth-role-container">
//         <div className="auth-role-title">I am a</div>
//         <div className="auth-role-buttons">
//           <button
//             type="button"
//             className={`auth-role-btn client ${role === "client" ? "active" : ""}`}
//             onClick={() => setRole("client")}
//           >
//             <i className="fas fa-user"></i> Client
//           </button>
//           <button
//             type="button"
//             className={`auth-role-btn lawyer ${role === "lawfirm" ? "active" : ""}`}
//             onClick={() => setRole("lawfirm")}
//           >
//             <i className="fas fa-gavel"></i> Law Firm / Lawyer
//           </button>
//           <button
//             type="button"
//             className={`auth-role-btn admin ${role === "admin" ? "active" : ""}`}
//             onClick={() => setRole("admin")}
//           >
//             <i className="fas fa-user-shield"></i> Admin
//           </button>
//         </div>
//       </div>

//       {/* Username / Email */}
//       <div className="auth-form-group">
//         <label className="auth-form-label" htmlFor="loginUsername">
//           Email or Username
//         </label>
//         <input
//           type="text"
//           className="auth-form-control"
//           id="loginUsername"
//           name="username"
//           value={formData.username}
//           onChange={handleChange}
//           placeholder="Enter your email or username"
//           required
//         />
//       </div>

//       {/* Password with toggle */}
//       <div className="auth-form-group">
//         <label className="auth-form-label" htmlFor="loginPassword">
//           Password
//         </label>
//         <div className="password-container">
//           <input
//             type={showPassword ? "text" : "password"}
//             className="auth-form-control"
//             id="loginPassword"
//             name="password"
//             value={formData.password}
//             onChange={handleChange}
//             placeholder="Enter your password"
//             required
//           />
//           <button
//             type="button"
//             className="toggle-password"
//             onClick={() => setShowPassword(!showPassword)}
//           >
//             <i className={`fas ${showPassword ? "fa-eye-slash" : "fa-eye"}`}></i>
//           </button>
//         </div>
//       </div>

//       {/* Lawfirm‑specific field */}
//       {role === "lawfirm" && (
//         <div className="auth-form-group">
//           <label className="auth-form-label required-field" htmlFor="registrationNo">
//             Registration Number
//           </label>
//           <input
//             type="text"
//             className="auth-form-control"
//             id="registrationNo"
//             name="registration_no"
//             value={formData.registration_no}
//             onChange={handleChange}
//             placeholder="Enter your bar registration number"
//             required
//           />
//         </div>
//       )}

//       {/* Admin‑specific field */}
//       {role === "admin" && (
//         <div className="auth-form-group">
//           <label className="auth-form-label required-field" htmlFor="secretKey">
//             Admin Secret Key
//           </label>
//           <input
//             type="password"
//             className="auth-form-control"
//             id="secretKey"
//             name="secret_key"
//             value={formData.secret_key}
//             onChange={handleChange}
//             placeholder="Enter admin secret key"
//             required
//           />
//           <small className="admin-note">Contact system administrator for secret key</small>
//         </div>
//       )}

//       {/* Remember Me */}
//       <div className="checkbox-container">
//         <input
//           type="checkbox"
//           id="rememberMe"
//           name="remember_me"
//           checked={formData.remember_me}
//           onChange={handleChange}
//         />
//         <label className="checkbox-label" htmlFor="rememberMe">
//           Remember me on this device
//         </label>
//       </div>

//       <button type="submit" className="auth-submit-btn">Sign In</button>

//       {/* Links – as shown in the screenshot */}
//       <div className="auth-links">
//         <button className="auth-link" onClick={(e) => e.preventDefault()}>
//           Forgot Password?
//         </button>
//         <button className="auth-link" onClick={(e) => e.preventDefault()}>
//           Need Help?
//         </button>
//       </div>
//     </form>
//   );
// }

// export default LoginForm;