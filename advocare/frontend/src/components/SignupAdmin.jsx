import React, { useState } from "react";
import API from "../services/api";
import { useNavigate } from "react-router-dom";

function SignupAdmin() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
    phone: "",
    secret_key: "",
    terms: false,
  });
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (formData.password !== formData.confirm_password) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }
    if (!formData.terms) {
      setError("You must accept the terms and conditions");
      setLoading(false);
      return;
    }

    const payload = {
      full_name: formData.full_name,
      email: formData.email,
      password: formData.password,
      role: "admin",
      phone: formData.phone,
      secret_key: formData.secret_key,
    };

    try {
      const res = await API.post("accounts/register/", payload);
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      localStorage.setItem("role", "admin");
      
      alert("Admin account created! You can now log in.");
      // ✅ Redirect to login page after signup
      navigate("/");
    } catch (err) {
      if (err.response) {
        const messages = Object.values(err.response.data).flat().join(" ");
        setError(messages);
      } else {
        setError("Network error. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form active">
      {error && <div className="alert alert-error">{error}</div>}
      
      <div className="auth-form-group">
        <label className="auth-form-label required-field">Full Name</label>
        <input
          type="text"
          className="auth-form-control"
          name="full_name"
          value={formData.full_name}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="auth-form-group">
        <label className="auth-form-label required-field">Email Address</label>
        <input
          type="email"
          className="auth-form-control"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="form-row">
        <div className="auth-form-group">
          <label className="auth-form-label required-field">Password</label>
          <div className="password-container">
            <input
              type={showPassword ? "text" : "password"}
              className="auth-form-control"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
            <button type="button" className="toggle-password" onClick={() => setShowPassword(!showPassword)}>
              <i className={`fas ${showPassword ? "fa-eye-slash" : "fa-eye"}`}></i>
            </button>
          </div>
        </div>
        <div className="auth-form-group">
          <label className="auth-form-label required-field">Confirm Password</label>
          <div className="password-container">
            <input
              type={showConfirmPassword ? "text" : "password"}
              className="auth-form-control"
              name="confirm_password"
              value={formData.confirm_password}
              onChange={handleChange}
              required
            />
            <button type="button" className="toggle-password" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
              <i className={`fas ${showConfirmPassword ? "fa-eye-slash" : "fa-eye"}`}></i>
            </button>
          </div>
        </div>
      </div>
      
      <div className="auth-form-group">
        <label className="auth-form-label">Phone Number (optional)</label>
        <input
          type="tel"
          className="auth-form-control"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
        />
      </div>
      
      <div className="auth-form-group">
        <label className="auth-form-label required-field">Admin Secret Key</label>
        <input
          type="password"
          className="auth-form-control"
          name="secret_key"
          value={formData.secret_key}
          onChange={handleChange}
          required
        />
        <small style={{ color: '#6c757d', fontSize: '12px' }}>Contact system administrator for the secret key</small>
      </div>
      
      <div className="checkbox-container">
        <input
          type="checkbox"
          name="terms"
          checked={formData.terms}
          onChange={handleChange}
          required
        />
        <label className="checkbox-label">
          I agree to the Terms of Service and Privacy Policy
        </label>
      </div>
      
      <button type="submit" className="auth-submit-btn" disabled={loading}>
        {loading ? <><i className="fas fa-spinner fa-spin"></i> Creating Account...</> : "Create Admin Account"}
      </button>
      
      <div className="auth-links">
        <button type="button" className="auth-link" onClick={() => navigate("/")}>
          Already have an account? Sign In
        </button>
      </div>
    </form>
  );
}

export default SignupAdmin;
