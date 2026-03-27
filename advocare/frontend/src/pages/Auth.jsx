import React, { useState } from "react";
import styles from "../assets/styles/auth.module.css";

import LoginForm from "../components/LoginForm";
import SignupClient from "../components/SignupClient";
import SignupLawfirm from "../components/SignupLawfirm";
import SignupAdmin from "../components/SignupAdmin";

function Auth() {
  const [tab, setTab] = useState("login");
  const [role, setRole] = useState("client");

  return (
    <div className={styles.container}>
      {/* Branding Section */}
      <div className={styles['branding-section']}>
        <div className={styles.logo}>
          <div className={styles['logo-icon']}>
            <i className="fas fa-balance-scale"></i>
          </div>
          <div className={styles['logo-text']}>Advocare</div>
        </div>

        <div className={styles['branding-content']}>
          <h1 className={styles['branding-title']}>Smart Legal Case Management System</h1>
          <p className={styles['branding-subtitle']}>
            Streamline your legal practice with our comprehensive platform designed
            for modern law firms and their clients.
          </p>
          <ul className={styles['features-list']}>
            <li><i className="fas fa-check-circle"></i> Secure client‑lawyer communication</li>
            <li><i className="fas fa-check-circle"></i> Case tracking and deadline management</li>
            <li><i className="fas fa-check-circle"></i> Document storage and collaboration</li>
            <li><i className="fas fa-check-circle"></i> Compliance and regulatory tools</li>
          </ul>
        </div>
      </div>

      {/* Auth Section */}
      <div className={styles['auth-section']}>
        <div className={styles['auth-container']}>
          <div className={styles['auth-header']}>
            <h2 className={styles['auth-title']}>Welcome to Advocare</h2>
            <p className={styles['auth-subtitle']}>Sign in to your account or create a new one</p>
          </div>

          {/* Tabs */}
          <div className={styles['auth-tabs']}>
            <button
              className={`${styles['auth-tab']} ${tab === "login" ? styles.active : ""}`}
              onClick={() => setTab("login")}
            >
              Sign In
            </button>
            <button
              className={`${styles['auth-tab']} ${tab === "signup" ? styles.active : ""}`}
              onClick={() => setTab("signup")}
            >
              Sign Up
            </button>
          </div>

          {/* Role Selector (only for signup) */}
          {tab === "signup" && (
            <div className={styles['role-selector-container']}>
              <div className={styles['role-selector-title']}>I am a</div>
              <div className={styles['role-selector']}>
                <button
                  className={`${styles['role-btn']} ${styles.client} ${role === "client" ? styles.active : ""}`}
                  onClick={() => setRole("client")}
                >
                  <i className="fas fa-user"></i> Client
                </button>
                <button
                  className={`${styles['role-btn']} ${styles.lawyer} ${role === "lawfirm" ? styles.active : ""}`}
                  onClick={() => setRole("lawfirm")}
                >
                  <i className="fas fa-gavel"></i> Law Firm / Lawyer
                </button>
                <button
                  className={`${styles['role-btn']} ${styles.admin} ${role === "admin" ? styles.active : ""}`}
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