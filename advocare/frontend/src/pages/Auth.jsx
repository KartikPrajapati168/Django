import React, { useState } from "react";
import LoginForm from "../components/LoginForm";
import SignupClient from "../components/SignupClient";
import SignupLawfirm from "../components/SignupLawfirm";
import SignupAdmin from "../components/SignupAdmin";

function Auth() {
  const [tab, setTab] = useState("login");
  const [role, setRole] = useState("client");

  return (
    <div className="auth-wrapper">
      {/* Branding Section */}
      <div className="auth-branding">
        <div className="auth-logo">
          <div className="auth-logo-icon">
            <i className="fas fa-balance-scale"></i>
          </div>
          <div className="auth-logo-text">Advocare</div>
        </div>

        <div className="auth-branding-content">
          <h1 className="auth-branding-title">Smart Legal Case Management System</h1>
          <p className="auth-branding-subtitle">
            Streamline your legal practice with our comprehensive platform designed
            for modern law firms and their clients.
          </p>
          <ul className="auth-features-list">
            <li><i className="fas fa-check-circle"></i> Secure client‑lawyer communication</li>
            <li><i className="fas fa-check-circle"></i> Case tracking and deadline management</li>
            <li><i className="fas fa-check-circle"></i> Document storage and collaboration</li>
            <li><i className="fas fa-check-circle"></i> Compliance and regulatory tools</li>
          </ul>
        </div>
      </div>

      {/* Auth Section */}
      <div className="auth-section">
        <div className="auth-container">
          <div className="auth-header">
            <h2 className="auth-title">Welcome to Advocare</h2>
            <p className="auth-subtitle">Sign in to your account or create a new one</p>
          </div>

          {/* Tabs */}
          <div className="auth-tabs">
            <button
              className={`auth-tab ${tab === "login" ? "active" : ""}`}
              onClick={() => setTab("login")}
            >
              Sign In
            </button>
            <button
              className={`auth-tab ${tab === "signup" ? "active" : ""}`}
              onClick={() => setTab("signup")}
            >
              Sign Up
            </button>
          </div>

          {/* Role Selector (only for signup) */}
          {tab === "signup" && (
            <div className="auth-role-container">
              <div className="auth-role-title">I am a</div>
              <div className="auth-role-buttons">
                <button
                  className={`auth-role-btn client ${role === "client" ? "active" : ""}`}
                  onClick={() => setRole("client")}
                >
                  <i className="fas fa-user"></i> Client
                </button>
                <button
                  className={`auth-role-btn lawyer ${role === "lawfirm" ? "active" : ""}`}
                  onClick={() => setRole("lawfirm")}
                >
                  <i className="fas fa-gavel"></i> Law Firm / Lawyer
                </button>
                <button
                  className={`auth-role-btn admin ${role === "admin" ? "active" : ""}`}
                  onClick={() => setRole("admin")}
                >
                  <i className="fas fa-user-shield"></i> Admin
                </button>
              </div>
            </div>
          )}

          {/* Forms */}
          {tab === "login" && <LoginForm />}
          {tab === "signup" && role === "client" && <SignupClient />}
          {tab === "signup" && role === "lawfirm" && <SignupLawfirm />}
          {tab === "signup" && role === "admin" && <SignupAdmin />}
        </div>
      </div>
    </div>
  );
}

export default Auth;