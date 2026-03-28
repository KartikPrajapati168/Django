import React, { useState } from "react";
import API from "../services/api";
import { useNavigate } from "react-router-dom";

function SignupClient() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
    phone: "",
    city: "",
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
      role: "client",
      phone: formData.phone,
      city: formData.city,
    };

    try {
      const res = await API.post("accounts/register/", payload);
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      localStorage.setItem("role", "client");

      // Save the user details for later use
      const userData = {
        full_name: payload.full_name,
        email: payload.email,
        phone: payload.phone,
        city: payload.city,
      };
      localStorage.setItem("user", JSON.stringify(userData));
      alert("Account created successfully");
      navigate("/client-onboarding");
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
        <label className="auth-form-label required-field">Phone Number</label>
        <input
          type="tel"
          className="auth-form-control"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="auth-form-group">
        <label className="auth-form-label required-field">City</label>
        <input
          type="text"
          className="auth-form-control"
          name="city"
          value={formData.city}
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
      
      <button type="submit" className="auth-submit-btn">Create Account</button>
      
      <div className="auth-links">
        <button className="auth-link" onClick={() => navigate("/")}>
          Already have an account? Sign In
        </button>
      </div>
    </form>
  );
}

export default SignupClient;































// import React, { useState } from "react";
// import axios from "axios";
// import { useNavigate } from "react-router-dom";

// function SignupClient() {
//   const navigate = useNavigate();
//   const [formData, setFormData] = useState({
//     full_name: "",
//     email: "",
//     phone: "",
//     password: "",
//     confirm_password: "",
//     city: "",
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

//     // Prepare payload - adjust field names to match your backend
//     const payload = {
//       email: formData.email,          // if your backend uses email as username
//       username: formData.email,       // some backends require username
//       full_name: formData.full_name,
//       phone: formData.phone,
//       password: formData.password,
//       city: formData.city,
//       role: "client",                 // if your backend needs role
//     };

//     try {
//       const res = await axios.post("http://localhost:8000/accounts/register", payload);
//       localStorage.setItem("token", res.data.token);
//       localStorage.setItem("role", "client");
//       navigate("/client-dashboard");
//     } catch (err) {
//       // Show the exact error from the server
//       if (err.response && err.response.data) {
//         const serverErrors = err.response.data;
//         if (typeof serverErrors === "object") {
//           // Extract all error messages
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
//       <input type="hidden" name="role" value="client" />
//       {error && <div className="alert alert-error">{error}</div>}

//       <div className="form-group">
//         <label className="form-label required-field" htmlFor="clientFullName">
//           Full Name
//         </label>
//         <input
//           type="text"
//           className="form-control"
//           id="clientFullName"
//           name="full_name"
//           value={formData.full_name}
//           onChange={handleChange}
//           placeholder="Enter your full name"
//           required
//         />
//       </div>

//       <div className="form-row">
//         <div className="form-group">
//           <label className="form-label required-field" htmlFor="clientEmail">
//             Email Address
//           </label>
//           <input
//             type="email"
//             className="form-control"
//             id="clientEmail"
//             name="email"
//             value={formData.email}
//             onChange={handleChange}
//             placeholder="Enter your email"
//             required
//           />
//         </div>
//         <div className="form-group">
//           <label className="form-label" htmlFor="clientPhone">
//             Phone Number
//           </label>
//           <input
//             type="tel"
//             className="form-control"
//             id="clientPhone"
//             name="phone"
//             value={formData.phone}
//             onChange={handleChange}
//             placeholder="Enter your phone number"
//           />
//         </div>
//       </div>

//       <div className="form-row">
//         <div className="form-group">
//           <label className="form-label required-field" htmlFor="clientPassword">
//             Password
//           </label>
//           <div className="password-container">
//             <input
//               type={showPassword ? "text" : "password"}
//               className="form-control"
//               id="clientPassword"
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
//           <label className="form-label required-field" htmlFor="clientConfirmPassword">
//             Confirm Password
//           </label>
//           <div className="password-container">
//             <input
//               type={showConfirmPassword ? "text" : "password"}
//               className="form-control"
//               id="clientConfirmPassword"
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
//         <label className="form-label" htmlFor="clientCity">
//           City
//         </label>
//         <input
//           type="text"
//           className="form-control"
//           id="clientCity"
//           name="city"
//           value={formData.city}
//           onChange={handleChange}
//           placeholder="Enter your city"
//         />
//       </div>

//       <div className="checkbox-container">
//         <input
//           type="checkbox"
//           id="clientTerms"
//           name="terms"
//           checked={formData.terms}
//           onChange={handleChange}
//           required
//         />
//         <label className="checkbox-label" htmlFor="clientTerms">
//           I agree to the <button className="auth-link" onClick={(e) => e.preventDefault()}>Terms of Service</button> and <button className="auth-link" onClick={(e) => e.preventDefault()}>Privacy Policy</button>
//         </label>
//       </div>

//       <button type="submit" className="submit-btn">Create Account</button>

//       <div className="auth-links">
//         <button className="auth-link" onClick={(e) => { e.preventDefault(); document.querySelector('.auth-tab[data-tab="login"]')?.click(); }}>Already have an account? Sign In</button>
//       </div>
//     </form>
//   );
// }

// export default SignupClient;




