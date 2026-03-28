import React, { useState } from "react";
import API from "../services/api";
import { useNavigate } from "react-router-dom";

function SignupAdmin() {
  const navigate = useNavigate();
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
    setError("");

    if (formData.password !== formData.confirm_password) {
      setError("Passwords do not match");
      return;
    }
    if (!formData.terms) {
      setError("You must accept the terms and conditions");
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
      navigate("/");
    } catch (err) {
      if (err.response) {
        const messages = Object.values(err.response.data).flat().join(" ");
        setError(messages);
      } else {
        setError("Network error. Please try again.");
      }
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
      
      <button type="submit" className="auth-submit-btn">Create Admin Account</button>
      
      <div className="auth-links">
        <button className="auth-link" onClick={() => navigate("/")}>
          Already have an account? Sign In
        </button>
      </div>
    </form>
  );
}

export default SignupAdmin;
























































// import React, { useState } from "react";
// import axios from "axios";
// import { useNavigate } from "react-router-dom";

// function SignupAdmin() {
//   const navigate = useNavigate();
//   const [formData, setFormData] = useState({
//     full_name: "",
//     email: "",
//     phone: "",
//     password: "",
//     confirm_password: "",
//     secret_key: "",
//     terms: false,
//   });
//   const [error, setError] = useState("");
//   const [showPassword, setShowPassword] = useState(false);
//   const [showConfirmPassword, setShowConfirmPassword] = useState(false);

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

//     if (formData.password !== formData.confirm_password) {
//       setError("Passwords do not match");
//       return;
//     }
//     if (!formData.terms) {
//       setError("You must accept the terms and conditions");
//       return;
//     }

//     const payload = {
//       email: formData.email,
//       username: formData.email,
//       full_name: formData.full_name,
//       phone: formData.phone,
//       password: formData.password,
//       secret_key: formData.secret_key,
//       role: "admin",
//     };

//     try {
//       const res = await axios.post("http://localhost:8000/api/signup/admin/", payload);
//       localStorage.setItem("token", res.data.token);
//       localStorage.setItem("role", "admin");
//       navigate("/admin-dashboard");
//     } catch (err) {
//       if (err.response && err.response.data) {
//         const serverErrors = err.response.data;
//         if (typeof serverErrors === "object") {
//           const messages = Object.values(serverErrors).flat().join(" ");
//           setError(messages);
//         } else {
//           setError(serverErrors.message || "Signup failed");
//         }
//       } else {
//         setError("Network error. Please try again.");
//       }
//     }
//   };

//   return (
//     <form onSubmit={handleSubmit} className="auth-form active">
//       <input type="hidden" name="role" value="admin" />
//       {error && <div className="alert alert-error">{error}</div>}

//       <div className="form-group">
//         <label className="form-label required-field" htmlFor="adminFullName">
//           Full Name
//         </label>
//         <input
//           type="text"
//           className="form-control"
//           id="adminFullName"
//           name="full_name"
//           value={formData.full_name}
//           onChange={handleChange}
//           placeholder="Enter your full name"
//           required
//         />
//       </div>

//       <div className="form-group">
//         <label className="form-label required-field" htmlFor="adminEmail">
//           Email Address
//         </label>
//         <input
//           type="email"
//           className="form-control"
//           id="adminEmail"
//           name="email"
//           value={formData.email}
//           onChange={handleChange}
//           placeholder="Enter your email"
//           required
//         />
//       </div>

//       <div className="form-group">
//         <label className="form-label" htmlFor="adminPhone">
//           Phone Number
//         </label>
//         <input
//           type="tel"
//           className="form-control"
//           id="adminPhone"
//           name="phone"
//           value={formData.phone}
//           onChange={handleChange}
//           placeholder="Enter your phone number"
//         />
//       </div>

//       <div className="form-row">
//         <div className="form-group">
//           <label className="form-label required-field" htmlFor="adminPassword">
//             Password
//           </label>
//           <div className="password-container">
//             <input
//               type={showPassword ? "text" : "password"}
//               className="form-control"
//               id="adminPassword"
//               name="password"
//               value={formData.password}
//               onChange={handleChange}
//               placeholder="Create a password"
//               required
//             />
//             <button type="button" className="toggle-password" onClick={() => setShowPassword(!showPassword)}>
//               <i className={`fas ${showPassword ? "fa-eye-slash" : "fa-eye"}`}></i>
//             </button>
//           </div>
//         </div>
//         <div className="form-group">
//           <label className="form-label required-field" htmlFor="adminConfirmPassword">
//             Confirm Password
//           </label>
//           <div className="password-container">
//             <input
//               type={showConfirmPassword ? "text" : "password"}
//               className="form-control"
//               id="adminConfirmPassword"
//               name="confirm_password"
//               value={formData.confirm_password}
//               onChange={handleChange}
//               placeholder="Confirm your password"
//               required
//             />
//             <button type="button" className="toggle-password" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
//               <i className={`fas ${showConfirmPassword ? "fa-eye-slash" : "fa-eye"}`}></i>
//             </button>
//           </div>
//         </div>
//       </div>

//       <div className="form-group">
//         <label className="form-label required-field" htmlFor="adminSecretKey">
//           Admin Secret Key
//         </label>
//         <input
//           type="password"
//           className="form-control"
//           id="adminSecretKey"
//           name="secret_key"
//           value={formData.secret_key}
//           onChange={handleChange}
//           placeholder="Enter admin secret key"
//           required
//         />
//         <small className="admin-note">Contact system administrator for secret key</small>
//       </div>

//       <div className="checkbox-container">
//         <input
//           type="checkbox"
//           id="adminTerms"
//           name="terms"
//           checked={formData.terms}
//           onChange={handleChange}
//           required
//         />
//         <label className="checkbox-label" htmlFor="adminTerms">
//           I agree to the <button className="auth-link" onClick={(e) => e.preventDefault()}>Terms of Service</button> and <button className="auth-link" onClick={(e) => e.preventDefault()}>Privacy Policy</button>
//         </label>
//       </div>

//       <button type="submit" className="submit-btn">Create Admin Account</button>

//       <div className="auth-links">
//         <button className="auth-link" onClick={(e) => { e.preventDefault(); document.querySelector('.auth-tab[data-tab="login"]')?.click(); }}>Already have an account? Sign In</button>
//       </div>
//     </form>
//   );
// }

// export default SignupAdmin;