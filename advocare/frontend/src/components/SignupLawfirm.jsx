import React, { useState } from "react";
import API from "../services/api";
import { useNavigate } from "react-router-dom";

function SignupLawfirm() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
    firm_name: "",
    phone: "",
    registration_no: "",
    experience: "",
    specialization: "",
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
      role: "lawfirm",
      firm_name: formData.firm_name,
      phone: formData.phone,
      registration_no: formData.registration_no,
      experience: parseInt(formData.experience, 10),
      specialization: formData.specialization,
    };

    try {
      const res = await API.post("accounts/register/", payload);
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      localStorage.setItem("role", "lawfirm");
      alert("Law firm account created successfully! Please wait for admin approval.");
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
        <label className="auth-form-label required-field">Law Firm Name</label>
        <input
          type="text"
          className="auth-form-control"
          name="firm_name"
          value={formData.firm_name}
          onChange={handleChange}
          required
        />
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
        <label className="auth-form-label required-field">Registration Number</label>
        <input
          type="text"
          className="auth-form-control"
          name="registration_no"
          value={formData.registration_no}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="auth-form-group">
        <label className="auth-form-label required-field">Experience (Years)</label>
        <input
          type="number"
          className="auth-form-control"
          name="experience"
          value={formData.experience}
          onChange={handleChange}
          min="0"
          required
        />
      </div>
      
      <div className="auth-form-group">
        <label className="auth-form-label required-field">Specialization</label>
        <select
          className="auth-form-control"
          name="specialization"
          value={formData.specialization}
          onChange={handleChange}
          required
        >
          <option value="" disabled>Select your specialization</option>
          <option value="corporate">Corporate Law</option>
          <option value="criminal">Criminal Law</option>
          <option value="family">Family Law</option>
          <option value="intellectual">Intellectual Property</option>
          <option value="real_estate">Real Estate Law</option>
          <option value="tax">Tax Law</option>
          <option value="immigration">Immigration Law</option>
          <option value="employment">Employment Law</option>
          <option value="civil">Civil Law</option>
          <option value="constitutional">Constitutional Law</option>
        </select>
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
      
      <button type="submit" className="auth-submit-btn">Create Law Firm Account</button>
      
      <div className="auth-links">
        <button className="auth-link" onClick={() => navigate("/")}>
          Already have an account? Sign In
        </button>
      </div>
    </form>
  );
}

export default SignupLawfirm;

























// import React, { useState } from "react";
// import axios from "axios";
// import { useNavigate } from "react-router-dom";

// function SignupLawfirm() {
//   const navigate = useNavigate();
//   const [formData, setFormData] = useState({
//     full_name: "",
//     firm_name: "",
//     email: "",
//     phone: "",
//     password: "",
//     confirm_password: "",
//     registration_no: "",
//     experience: "",
//     specialization: "",
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
//       firm_name: formData.firm_name,
//       phone: formData.phone,
//       password: formData.password,
//       registration_no: formData.registration_no,
//       experience: formData.experience,
//       specialization: formData.specialization,
//       role: "lawfirm",
//     };

//     try {
//       const res = await axios.post("http://localhost:8000/api/signup/lawfirm/", payload);
//       localStorage.setItem("token", res.data.token);
//       localStorage.setItem("role", "lawfirm");
//       navigate("/lawfirm-dashboard");
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
//       <input type="hidden" name="role" value="lawfirm" />
//       {error && <div className="alert alert-error">{error}</div>}

//       <div className="form-group">
//         <label className="form-label required-field" htmlFor="lawfirmFullName">
//           Full Name
//         </label>
//         <input
//           type="text"
//           className="form-control"
//           id="lawfirmFullName"
//           name="full_name"
//           value={formData.full_name}
//           onChange={handleChange}
//           placeholder="Enter your full name"
//           required
//         />
//       </div>

//       <div className="form-group">
//         <label className="form-label required-field" htmlFor="lawfirmFirmName">
//           Law Firm Name
//         </label>
//         <input
//           type="text"
//           className="form-control"
//           id="lawfirmFirmName"
//           name="firm_name"
//           value={formData.firm_name}
//           onChange={handleChange}
//           placeholder="Enter your law firm name"
//           required
//         />
//       </div>

//       <div className="form-row">
//         <div className="form-group">
//           <label className="form-label required-field" htmlFor="lawfirmEmail">
//             Email Address
//           </label>
//           <input
//             type="email"
//             className="form-control"
//             id="lawfirmEmail"
//             name="email"
//             value={formData.email}
//             onChange={handleChange}
//             placeholder="Enter your email"
//             required
//           />
//         </div>
//         <div className="form-group">
//           <label className="form-label required-field" htmlFor="lawfirmPhone">
//             Phone Number
//           </label>
//           <input
//             type="tel"
//             className="form-control"
//             id="lawfirmPhone"
//             name="phone"
//             value={formData.phone}
//             onChange={handleChange}
//             placeholder="Enter your phone number"
//             required
//           />
//         </div>
//       </div>

//       <div className="form-row">
//         <div className="form-group">
//           <label className="form-label required-field" htmlFor="lawfirmPassword">
//             Password
//           </label>
//           <div className="password-container">
//             <input
//               type={showPassword ? "text" : "password"}
//               className="form-control"
//               id="lawfirmPassword"
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
//           <label className="form-label required-field" htmlFor="lawfirmConfirmPassword">
//             Confirm Password
//           </label>
//           <div className="password-container">
//             <input
//               type={showConfirmPassword ? "text" : "password"}
//               className="form-control"
//               id="lawfirmConfirmPassword"
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

//       <div className="form-row">
//         <div className="form-group">
//           <label className="form-label required-field" htmlFor="lawfirmRegistrationNo">
//             Registration Number
//           </label>
//           <input
//             type="text"
//             className="form-control"
//             id="lawfirmRegistrationNo"
//             name="registration_no"
//             value={formData.registration_no}
//             onChange={handleChange}
//             placeholder="Enter your bar registration number"
//             required
//           />
//         </div>
//         <div className="form-group">
//           <label className="form-label required-field" htmlFor="lawfirmExperience">
//             Experience (Years)
//           </label>
//           <input
//             type="number"
//             className="form-control"
//             id="lawfirmExperience"
//             name="experience"
//             value={formData.experience}
//             onChange={handleChange}
//             min="0"
//             max="50"
//             placeholder="Years of experience"
//             required
//           />
//         </div>
//       </div>

//       <div className="form-group">
//         <label className="form-label required-field" htmlFor="lawfirmSpecialization">
//           Specialization
//         </label>
//         <select
//           className="specialization-select"
//           id="lawfirmSpecialization"
//           name="specialization"
//           value={formData.specialization}
//           onChange={handleChange}
//           required
//         >
//           <option value="" disabled>Select your specialization</option>
//           <option value="corporate">Corporate Law</option>
//           <option value="criminal">Criminal Law</option>
//           <option value="family">Family Law</option>
//           <option value="intellectual">Intellectual Property</option>
//           <option value="real_estate">Real Estate Law</option>
//           <option value="tax">Tax Law</option>
//           <option value="immigration">Immigration Law</option>
//           <option value="employment">Employment Law</option>
//           <option value="civil">Civil Law</option>
//           <option value="constitutional">Constitutional Law</option>
//         </select>
//       </div>

//       <div className="checkbox-container">
//         <input
//           type="checkbox"
//           id="lawfirmTerms"
//           name="terms"
//           checked={formData.terms}
//           onChange={handleChange}
//           required
//         />
//         <label className="checkbox-label" htmlFor="lawfirmTerms">
//           I agree to the <button className="auth-link" onClick={(e) => e.preventDefault()}>Terms of Service</button> and <button className="auth-link" onClick={(e) => e.preventDefault()}>Privacy Policy</button>
//         </label>
//       </div>

//       <button type="submit" className="submit-btn">Create Law Firm Account</button>

//       <div className="auth-links">
//         <button className="auth-link" onClick={(e) => { e.preventDefault(); document.querySelector('.auth-tab[data-tab="login"]')?.click(); }}>Already have an account? Sign In</button>
//       </div>
//     </form>
//   );
// }

// export default SignupLawfirm;