import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function LoginForm() {
  const navigate = useNavigate();
  const [role, setRole] = useState("client"); // "client", "lawfirm", "admin"
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    remember_me: false,
    registration_no: "",    // only for lawfirm
    secret_key: "",         // only for admin
  });
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const payload = {
      username: formData.username,
      password: formData.password,
      remember_me: formData.remember_me,
      role: role,
    };
    if (role === "lawfirm") payload.registration_no = formData.registration_no;
    if (role === "admin") payload.secret_key = formData.secret_key;

    try {
      const res = await axios.post("http://localhost:8000/api/login/", payload);
      localStorage.setItem("token", res.data.token);
      localStorage.setItem("role", res.data.role);
      if (res.data.role === "client") navigate("/client-dashboard");
      else if (res.data.role === "lawfirm") navigate("/lawfirm-dashboard");
      else if (res.data.role === "admin") navigate("/admin-dashboard");
    } catch (err) {
      setError(err.response?.data?.message || "Login failed");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form active">
      {error && <div className="alert alert-error">{error}</div>}

      {/* Role Selector */}
      <div className="role-selector-container">
        <div className="role-selector-title">I am a</div>
        <div className="role-selector">
          <button
            type="button"
            className={`role-btn client ${role === "client" ? "active" : ""}`}
            onClick={() => setRole("client")}
          >
            <i className="fas fa-user"></i> Client
          </button>
          <button
            type="button"
            className={`role-btn lawyer ${role === "lawfirm" ? "active" : ""}`}
            onClick={() => setRole("lawfirm")}
          >
            <i className="fas fa-gavel"></i> Law Firm / Lawyer
          </button>
          <button
            type="button"
            className={`role-btn admin ${role === "admin" ? "active" : ""}`}
            onClick={() => setRole("admin")}
          >
            <i className="fas fa-user-shield"></i> Admin
          </button>
        </div>
      </div>

      {/* Username / Email */}
      <div className="form-group">
        <label className="form-label" htmlFor="loginUsername">
          Email or Username
        </label>
        <input
          type="text"
          className="form-control"
          id="loginUsername"
          name="username"
          value={formData.username}
          onChange={handleChange}
          placeholder="Enter your email or username"
          required
        />
      </div>

      {/* Password with React toggle */}
      <div className="form-group">
        <label className="form-label" htmlFor="loginPassword">
          Password
        </label>
        <div className="password-container">
          <input
            type={showPassword ? "text" : "password"}
            className="form-control"
            id="loginPassword"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Enter your password"
            required
          />
          <button
            type="button"
            className="toggle-password"
            onClick={() => setShowPassword(!showPassword)}
          >
            <i className={`fas ${showPassword ? "fa-eye-slash" : "fa-eye"}`}></i>
          </button>
        </div>
      </div>

      {/* Lawfirm‑specific field */}
      {role === "lawfirm" && (
        <div className="form-group">
          <label className="form-label required-field" htmlFor="registrationNo">
            Registration Number
          </label>
          <input
            type="text"
            className="form-control"
            id="registrationNo"
            name="registration_no"
            value={formData.registration_no}
            onChange={handleChange}
            placeholder="Enter your bar registration number"
            required
          />
        </div>
      )}

      {/* Admin‑specific field */}
      {role === "admin" && (
        <div className="form-group">
          <label className="form-label required-field" htmlFor="secretKey">
            Admin Secret Key
          </label>
          <input
            type="password"
            className="form-control"
            id="secretKey"
            name="secret_key"
            value={formData.secret_key}
            onChange={handleChange}
            placeholder="Enter admin secret key"
            required
          />
          <small className="admin-note">Contact system administrator for secret key</small>
        </div>
      )}

      {/* Remember Me */}
      <div className="checkbox-container">
        <input
          type="checkbox"
          id="rememberMe"
          name="remember_me"
          checked={formData.remember_me}
          onChange={handleChange}
        />
        <label className="checkbox-label" htmlFor="rememberMe">
          Remember me on this device
        </label>
      </div>

      <button type="submit" className="submit-btn">Sign In</button>

      {/* Links – as shown in the screenshot */}
      <div className="auth-links">
        <button className="auth-link" onClick={(e) => e.preventDefault()}>
          Forgot Password?
        </button>
        <button className="auth-link" onClick={(e) => e.preventDefault()}>
          Need Help?
        </button>
      </div>
    </form>
  );
}

export default LoginForm;