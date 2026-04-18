import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';

function LawfirmOnboarding() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [rejectionMessage, setRejectionMessage] = useState('');
    const [statusChecked, setStatusChecked] = useState(false);
    const [userData, setUserData] = useState({
        email: '',
        full_name: '',
        firm_name: '',
    });
    
    const [teamMembers, setTeamMembers] = useState([
        { id: 1, name: '', email: '', role: '', experience: '' }
    ]);
    const [selectedSpecializations, setSelectedSpecializations] = useState([]);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [formData, setFormData] = useState({
        firm_name: '',
        registration_no: '',
        address: '',
        city: '',
        state: '',
        website: '',
        phone: '',
        experience: '',
        specialization: '',
        primary_lawyer_name: '',
        primary_lawyer_bar_council_id: '',
        primary_lawyer_years_experience: '',
        primary_lawyer_specialization: '',
    });
    const [validationErrors, setValidationErrors] = useState({});
    const [showSuccessModal, setShowSuccessModal] = useState(false);
    const [progress, setProgress] = useState(0);
    
    const fileInputRef = useRef(null);
    const dropAreaRef = useRef(null);
    const pollingInterval = useRef(null);
    
    // Document status
    const [docStatus, setDocStatus] = useState({
        bar_certificate: false,
        firm_registration: false,
        id_proof: false
    });
    
    // Helper: Convert integer years to experience range string
    const yearsToExperienceRange = (years) => {
        if (years <= 2) return '0-2';
        if (years <= 5) return '3-5';
        if (years <= 10) return '6-10';
        if (years <= 15) return '11-15';
        return '15+';
    };
    
    // Helper: Convert range string (e.g., "3-5") to integer (lower bound)
    const rangeToYears = (range) => {
        if (!range) return null;
        const match = range.match(/(\d+)-(\d+)/);
        if (match) return parseInt(match[1], 10);
        if (range === '15+') return 15;
        return null;
    };
    
    // Firm Specialization options
    const firmSpecializationOptions = [
        { value: 'corporate', label: 'Corporate Law' },
        { value: 'criminal', label: 'Criminal Law' },
        { value: 'family', label: 'Family Law' },
        { value: 'intellectual', label: 'Intellectual Property' },
        { value: 'immigration', label: 'Immigration Law' },
        { value: 'tax', label: 'Tax Law' },
        { value: 'labor', label: 'Labor Law' },
        { value: 'civil', label: 'Civil Litigation' },
    ];
    
    // Primary Lawyer Specialization options
    const lawyerSpecializationOptions = [
        { value: 'corporate', label: 'Corporate Law' },
        { value: 'criminal', label: 'Criminal Law' },
        { value: 'family', label: 'Family Law' },
        { value: 'intellectual', label: 'Intellectual Property' },
        { value: 'immigration', label: 'Immigration Law' },
        { value: 'tax', label: 'Tax Law' },
        { value: 'labor', label: 'Labor Law' },
        { value: 'civil', label: 'Civil Litigation' },
    ];
    
    // Role options for team members
    const roleOptions = [
        { value: 'associate', label: 'Associate' },
        { value: 'partner', label: 'Partner' },
        { value: 'senior_advocate', label: 'Senior Advocate' },
        { value: 'legal_assistant', label: 'Legal Assistant' },
        { value: 'paralegal', label: 'Paralegal' },
    ];
    
    // Experience options
    const experienceOptions = [
        { value: '0-2', label: '0-2 years' },
        { value: '3-5', label: '3-5 years' },
        { value: '6-10', label: '6-10 years' },
        { value: '11-15', label: '11-15 years' },
        { value: '15+', label: '15+ years' },
    ];
    
    // ========== UPDATED: Load user data from both API and localStorage ==========
    useEffect(() => {
        let isMounted = true;
        
        const loadData = async () => {
            try {
                const token = localStorage.getItem('access_token');
                if (!token) {
                    navigate('/');
                    return;
                }
                
                // 1. Check law firm status – redirect if already approved or pending
                const statusRes = await API.get('profiles/lawfirm-status/');
                if (isMounted) {
                    if (statusRes.data.status === 'approved') {
                        if (pollingInterval.current) clearInterval(pollingInterval.current);
                        navigate('/lawfirm-portal');
                        return;
                    } else if (statusRes.data.status === 'pending') {
                        navigate('/lawfirm-pending-onboarding');
                        return;
                    }
                }
                
                // 2. Get user profile from /profiles/auth/me/
                let profileFullName = '';
                let profilePhone = '';
                let profileCity = '';
                try {
                    const meRes = await API.get('profiles/auth/me/');
                    if (isMounted && meRes.data) {
                        profileFullName = meRes.data.full_name || '';
                        profilePhone = meRes.data.phone || '';
                        profileCity = meRes.data.city || '';
                        setUserData(prev => ({
                            ...prev,
                            email: meRes.data.email || '',
                            full_name: profileFullName,
                        }));
                    }
                } catch (err) {
                    console.warn('Could not fetch /auth/me/', err);
                }
                
                // 3. Get law firm profile (if already exists from partial submission)
                let existingProfile = null;
                try {
                    const profileRes = await API.get('profiles/lawfirm-profile/');
                    if (isMounted && profileRes.data) {
                        existingProfile = profileRes.data;
                    }
                } catch (err) {
                    // No existing profile – ignore
                }
                
                // 4. Load signup data from localStorage (fallback)
                let signupData = {};
                const storedUser = localStorage.getItem('user');
                if (storedUser) {
                    try {
                        signupData = JSON.parse(storedUser);
                    } catch (e) {}
                }
                
                // Convert signup experience (integer) to range string
                let signupExperienceRange = '';
                if (signupData.experience && !isNaN(signupData.experience)) {
                    signupExperienceRange = yearsToExperienceRange(signupData.experience);
                }
                
                // 5. Merge data: existing profile > signup data > empty defaults
                const finalData = {
                    firm_name: existingProfile?.firm_name || signupData.firm_name || '',
                    registration_no: existingProfile?.registration_no || signupData.registration_no || '',
                    address: existingProfile?.address || '',
                    city: existingProfile?.city || signupData.city || profileCity || '',
                    state: existingProfile?.state || '',
                    website: existingProfile?.website || '',
                    phone: existingProfile?.phone || signupData.phone || profilePhone || '',
                    experience: existingProfile?.experience || signupExperienceRange || '',
                    specialization: existingProfile?.specialization || signupData.specialization || '',
                    primary_lawyer_name: existingProfile?.primary_lawyer_name || signupData.full_name || profileFullName || '',
                    primary_lawyer_bar_council_id: existingProfile?.primary_lawyer_bar_council_id || '',
                    primary_lawyer_years_experience: existingProfile?.primary_lawyer_years_experience || '',
                    primary_lawyer_specialization: existingProfile?.primary_lawyer_specialization || '',
                };
                
                setFormData(prev => ({ ...prev, ...finalData }));
                
                // Set firm name in userData for display
                setUserData(prev => ({
                    ...prev,
                    firm_name: finalData.firm_name,
                }));
                
                // If specialization is a comma‑separated string, split into array
                if (finalData.specialization && finalData.specialization.includes(',')) {
                    setSelectedSpecializations(finalData.specialization.split(','));
                } else if (finalData.specialization) {
                    setSelectedSpecializations([finalData.specialization]);
                }
                
                // If existing profile contains team members, load them
                if (existingProfile?.team_members && existingProfile.team_members.length) {
                    const members = existingProfile.team_members.map((tm, idx) => ({
                        id: idx + 1,
                        name: tm.name,
                        email: tm.email,
                        role: tm.role,
                        experience: tm.experience_years || '',
                    }));
                    setTeamMembers(members);
                }
                
                setStatusChecked(true);
                
                // Check for rejection message
                const message = localStorage.getItem('lawfirm_onboarding_message');
                if (message) {
                    setRejectionMessage(message);
                    localStorage.removeItem('lawfirm_onboarding_message');
                }
            } catch (error) {
                console.error('Error loading data:', error);
                setStatusChecked(true);
            }
        };
        
        loadData();
        
        return () => {
            isMounted = false;
            if (pollingInterval.current) clearInterval(pollingInterval.current);
        };
    }, [navigate]);
    
    // Handle input change
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (validationErrors[name]) {
            setValidationErrors(prev => ({ ...prev, [name]: '' }));
        }
        updateProgress();
    };
    
    // Handle team member change
    const handleTeamMemberChange = (id, field, value) => {
        setTeamMembers(prev => prev.map(member => 
            member.id === id ? { ...member, [field]: value } : member
        ));
        updateProgress();
    };
    
    // Add team member
    const addTeamMember = () => {
        const newId = Math.max(...teamMembers.map(m => m.id), 0) + 1;
        setTeamMembers(prev => [...prev, {
            id: newId,
            name: '',
            email: '',
            role: '',
            experience: ''
        }]);
    };
    
    // Remove team member
    const removeTeamMember = (id) => {
        if (teamMembers.length > 1) {
            setTeamMembers(prev => prev.filter(member => member.id !== id));
        }
    };
    
    // Handle firm specialization selection
    const toggleFirmSpecialization = (value) => {
        setSelectedSpecializations(prev => {
            if (prev.includes(value)) {
                return prev.filter(v => v !== value);
            } else {
                return [...prev, value];
            }
        });
        updateProgress();
    };
    
    // Handle primary lawyer specialization
    const handleLawyerSpecialization = (e) => {
        setFormData(prev => ({ ...prev, primary_lawyer_specialization: e.target.value }));
        updateProgress();
    };
    
    // File upload handling
    const handleFileSelect = (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
    };
    
    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (dropAreaRef.current) {
            dropAreaRef.current.classList.add('dragover');
        }
    };
    
    const handleDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (dropAreaRef.current) {
            dropAreaRef.current.classList.remove('dragover');
        }
    };
    
    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (dropAreaRef.current) {
            dropAreaRef.current.classList.remove('dragover');
        }
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    };
    
    const handleFiles = (files) => {
        const newFiles = files.map(file => ({
            id: Date.now() + '-' + file.name,
            name: file.name,
            size: formatFileSize(file.size),
            type: getFileType(file.name),
            file: file
        }));
        
        setUploadedFiles(prev => [...prev, ...newFiles]);
        
        files.forEach(file => {
            const fileName = file.name.toLowerCase();
            if (fileName.includes('bar') || fileName.includes('council') || fileName.includes('certificate')) {
                setDocStatus(prev => ({ ...prev, bar_certificate: true }));
            } else if (fileName.includes('registration') || fileName.includes('firm') || fileName.includes('proof')) {
                setDocStatus(prev => ({ ...prev, firm_registration: true }));
            } else if (fileName.includes('id') || fileName.includes('proof') || fileName.includes('passport') || fileName.includes('license')) {
                setDocStatus(prev => ({ ...prev, id_proof: true }));
            }
        });
    };
    
    const removeUploadedFile = (id) => {
        setUploadedFiles(prev => prev.filter(file => file.id !== id));
    };
    
    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    const getFileType = (fileName) => {
        const ext = fileName.split('.').pop().toLowerCase();
        if (['pdf'].includes(ext)) return 'pdf';
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) return 'image';
        if (['doc', 'docx'].includes(ext)) return 'word';
        if (['xls', 'xlsx'].includes(ext)) return 'excel';
        return 'file';
    };
    
    const getFileIcon = (fileType) => {
        switch(fileType) {
            case 'pdf': return 'fa-file-pdf';
            case 'image': return 'fa-file-image';
            case 'word': return 'fa-file-word';
            case 'excel': return 'fa-file-excel';
            default: return 'fa-file';
        }
    };
    
    // Validate form
    const validateForm = () => {
        const errors = {};
        
        // Firm Details
        if (!formData.firm_name) errors.firm_name = 'Please enter law firm name';
        if (!formData.registration_no) errors.registration_no = 'Please enter registration number';
        if (!formData.address) errors.address = 'Please enter address';
        if (!formData.city) errors.city = 'Please enter city';
        if (!formData.state) errors.state = 'Please enter state';
        if (!formData.experience) errors.experience = 'Please select firm experience';
        if (selectedSpecializations.length === 0) errors.specialization = 'Please select at least one specialization';
        
        // Primary Lawyer
        if (!formData.primary_lawyer_name) errors.primary_lawyer_name = 'Please enter primary lawyer name';
        if (!formData.primary_lawyer_bar_council_id) errors.primary_lawyer_bar_council_id = 'Please enter bar council ID';
        if (!formData.primary_lawyer_years_experience) errors.primary_lawyer_years_experience = 'Please select years of experience';
        if (!formData.primary_lawyer_specialization) errors.primary_lawyer_specialization = 'Please select lawyer specialization';
        
        // Team members
        teamMembers.forEach((member, index) => {
            if (!member.name) errors[`member_name_${index}`] = 'Name required';
            if (!member.email) errors[`member_email_${index}`] = 'Email required';
            if (!member.role) errors[`member_role_${index}`] = 'Role required';
            if (!member.experience) errors[`member_exp_${index}`] = 'Experience required';
        });
        
        setValidationErrors(errors);
        return Object.keys(errors).length === 0;
    };
    
    // Update progress
    const updateProgress = () => {
        let completed = 0;
        const sections = [
            formData.firm_name && formData.registration_no && formData.address && formData.city && formData.state && formData.experience && selectedSpecializations.length > 0,
            formData.primary_lawyer_name && formData.primary_lawyer_bar_council_id && formData.primary_lawyer_years_experience && formData.primary_lawyer_specialization,
            teamMembers.length > 0 && teamMembers.every(m => m.name && m.email && m.role && m.experience),
            true
        ];
        
        completed = sections.filter(Boolean).length;
        setProgress((completed / 4) * 100);
    };
    
    // Submit form
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) {
            alert('Please fill all required fields');
            return;
        }
        
        setLoading(true);
        
        const submitData = new FormData();
        
        // Firm Details
        submitData.append('firm_name', formData.firm_name);
        submitData.append('registration_no', formData.registration_no);
        submitData.append('address', formData.address);
        submitData.append('city', formData.city);
        submitData.append('state', formData.state);
        submitData.append('website', formData.website || '');
        submitData.append('phone', formData.phone || '');
        submitData.append('experience', formData.experience);
        submitData.append('specialization', selectedSpecializations.join(','));
        
        // Convert primary lawyer years experience from range to integer
        let lawyerYears = null;
        if (formData.primary_lawyer_years_experience) {
            lawyerYears = rangeToYears(formData.primary_lawyer_years_experience);
        }
        if (lawyerYears === null) {
            // Fallback: try to parse as integer directly
            lawyerYears = parseInt(formData.primary_lawyer_years_experience, 10);
        }
        
        // Primary Lawyer Details
        submitData.append('primary_lawyer_name', formData.primary_lawyer_name);
        submitData.append('primary_lawyer_bar_council_id', formData.primary_lawyer_bar_council_id);
        submitData.append('primary_lawyer_years_experience', lawyerYears !== null && !isNaN(lawyerYears) ? lawyerYears : 0);
        submitData.append('primary_lawyer_specialization', formData.primary_lawyer_specialization);
        submitData.append('terms_accepted', 'true');
        
        // Team Members
        submitData.append('team_members', JSON.stringify(teamMembers.map(m => ({
            name: m.name,
            email: m.email,
            role: m.role,
            experience_years: m.experience
        }))));
        
        // Documents
        uploadedFiles.forEach(file => {
            if (file.file) {
                let docType = 'other';
                const fileName = file.name.toLowerCase();
                if (fileName.includes('bar') || fileName.includes('council')) {
                    docType = 'bar_council_certificate';
                } else if (fileName.includes('registration') || fileName.includes('firm')) {
                    docType = 'firm_registration';
                } else if (fileName.includes('id') || fileName.includes('proof')) {
                    docType = 'lawyer_id_proof';
                }
                submitData.append(`documents_${docType}`, file.file);
            }
        });
        
        try {
            const token = localStorage.getItem('access_token');
            const response = await API.post('profiles/lawfirm-onboarding/', submitData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data',
                },
            });
            
            if (response.data.success || response.data.message) {
                // Store onboarding data for pending page
                localStorage.setItem('lawfirm_onboarding_status', 'pending');
                localStorage.setItem('lawfirm_onboarding_data', JSON.stringify({
                    firm_name: formData.firm_name,
                    registration_no: formData.registration_no,
                    primary_lawyer_name: formData.primary_lawyer_name,
                    submitted_at: new Date().toISOString()
                }));
                navigate('/lawfirm-pending-onboarding');
            }
        } catch (error) {
            console.error('Onboarding error:', error);
            if (error.response?.status === 401) {
                alert('Session expired. Please login again.');
                navigate('/');
            } else {
                // Show detailed error from backend
                const errorMsg = error.response?.data?.error || Object.values(error.response?.data || {}).flat().join(', ') || 'Network error. Please try again.';
                alert(errorMsg);
            }
        } finally {
            setLoading(false);
        }
    };
    
    const handleModalClose = () => {
        setShowSuccessModal(false);
        navigate('/lawfirm-dashboard');
    };
    
    useEffect(() => {
        updateProgress();
    }, [formData, teamMembers, selectedSpecializations]);
    
    // Show loading while checking status
    if (!statusChecked) {
        return (
            <div className="pending-container">
                <div className="pending-card">
                    <div className="spinner"></div>
                    <h2>Loading...</h2>
                </div>
            </div>
        );
    }
    
    return (
        <>
            {/* Rejection Banner */}
            {rejectionMessage && (
                <div className="rejection-banner" style={{
                    backgroundColor: '#f8d7da',
                    color: '#721c24',
                    padding: '12px 20px',
                    margin: '10px 20px',
                    borderRadius: '8px',
                    border: '1px solid #f5c6cb',
                    textAlign: 'center',
                    position: 'sticky',
                    top: 0,
                    zIndex: 1000
                }}>
                    <i className="fas fa-exclamation-triangle me-2"></i>
                    {rejectionMessage}
                    <button 
                        onClick={() => setRejectionMessage('')}
                        style={{ background: 'none', border: 'none', marginLeft: '15px', cursor: 'pointer', color: '#721c24' }}
                    >
                        <i className="fas fa-times"></i>
                    </button>
                </div>
            )}
            
            <div className="lawfirm-onboarding-container">
                <header className="onboarding-header">
                    <div className="onboarding-header-container">
                        <div className="onboarding-logo">
                            <div className="onboarding-logo-icon">
                                <i className="fas fa-balance-scale"></i>
                            </div>
                            <div className="onboarding-logo-text">AdvoCare</div>
                        </div>
                        <div className="onboarding-user-info">
                            <div className="onboarding-user-avatar">
                                {formData.primary_lawyer_name ? formData.primary_lawyer_name.charAt(0).toUpperCase() : 
                                 userData.full_name ? userData.full_name.charAt(0).toUpperCase() : 'LF'}
                            </div>
                            <div>
                                <div>{formData.primary_lawyer_name || userData.full_name || 'Law Firm'}</div>
                                <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>Law Firm Admin</div>
                            </div>
                        </div>
                    </div>
                </header>
                
                <div className="lawfirm-onboarding-main">
                    <div className="lawfirm-onboarding-grid">
                        {/* Form Section */}
                        <div className="lawfirm-form-container">
                            <h1 className="lawfirm-page-title">Law Firm Onboarding</h1>
                            <p className="lawfirm-page-subtitle">
                                Complete your firm's profile to get verified and start accepting cases through AdvocateCare.
                                All fields marked with * are required.
                            </p>
                            
                            <form onSubmit={handleSubmit}>
                                {/* Section 1: Firm Details */}
                                <section className="lawfirm-form-section">
                                    <div className="lawfirm-section-header">
                                        <div className="lawfirm-section-number">1</div>
                                        <h2 className="lawfirm-section-title">Firm Details</h2>
                                    </div>
                                    
                                    <div className="lawfirm-form-grid">
                                        <div className="lawfirm-form-group">
                                            <label className="lawfirm-label required">Law Firm Name</label>
                                            <input
                                                type="text"
                                                name="firm_name"
                                                className={`lawfirm-input ${validationErrors.firm_name ? 'error' : ''}`}
                                                value={formData.firm_name}
                                                onChange={handleChange}
                                                placeholder="Enter your law firm's name"
                                                required
                                            />
                                            {validationErrors.firm_name && <div className="lawfirm-error">{validationErrors.firm_name}</div>}
                                        </div>
                                        
                                        <div className="lawfirm-form-group">
                                            <label className="lawfirm-label required">Registration Number</label>
                                            <input
                                                type="text"
                                                name="registration_no"
                                                className={`lawfirm-input ${validationErrors.registration_no ? 'error' : ''}`}
                                                value={formData.registration_no}
                                                onChange={handleChange}
                                                placeholder="Firm registration number"
                                                required
                                            />
                                            {validationErrors.registration_no && <div className="lawfirm-error">{validationErrors.registration_no}</div>}
                                        </div>
                                        
                                        <div className="lawfirm-form-group">
                                            <label className="lawfirm-label required">Firm Experience (Years)</label>
                                            <select
                                                name="experience"
                                                className={`lawfirm-select ${validationErrors.experience ? 'error' : ''}`}
                                                value={formData.experience}
                                                onChange={handleChange}
                                                required
                                            >
                                                <option value="">Select years of experience</option>
                                                {experienceOptions.map(opt => (
                                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                                ))}
                                            </select>
                                            {validationErrors.experience && <div className="lawfirm-error">{validationErrors.experience}</div>}
                                        </div>
                                        
                                        <div className="lawfirm-form-group full-width">
                                            <label className="lawfirm-label required">Firm Specialization</label>
                                            <div className="lawfirm-multi-select">
                                                <div className="lawfirm-multi-select-options">
                                                    {firmSpecializationOptions.map(opt => (
                                                        <div
                                                            key={opt.value}
                                                            className={`lawfirm-multi-select-option ${selectedSpecializations.includes(opt.value) ? 'selected' : ''}`}
                                                            onClick={() => toggleFirmSpecialization(opt.value)}
                                                        >
                                                            {opt.label}
                                                        </div>
                                                    ))}
                                                </div>
                                                {validationErrors.specialization && <div className="lawfirm-error">{validationErrors.specialization}</div>}
                                            </div>
                                        </div>
                                        
                                        <div className="lawfirm-form-group full-width">
                                            <label className="lawfirm-label required">Address</label>
                                            <textarea
                                                name="address"
                                                rows="3"
                                                className={`lawfirm-textarea ${validationErrors.address ? 'error' : ''}`}
                                                value={formData.address}
                                                onChange={handleChange}
                                                placeholder="Full address of your law firm"
                                                required
                                            />
                                            {validationErrors.address && <div className="lawfirm-error">{validationErrors.address}</div>}
                                        </div>
                                        
                                        <div className="lawfirm-form-group">
                                            <label className="lawfirm-label required">City</label>
                                            <input
                                                type="text"
                                                name="city"
                                                className={`lawfirm-input ${validationErrors.city ? 'error' : ''}`}
                                                value={formData.city}
                                                onChange={handleChange}
                                                placeholder="City"
                                                required
                                            />
                                            {validationErrors.city && <div className="lawfirm-error">{validationErrors.city}</div>}
                                        </div>
                                        
                                        <div className="lawfirm-form-group">
                                            <label className="lawfirm-label required">State</label>
                                            <input
                                                type="text"
                                                name="state"
                                                className={`lawfirm-input ${validationErrors.state ? 'error' : ''}`}
                                                value={formData.state}
                                                onChange={handleChange}
                                                placeholder="State"
                                                required
                                            />
                                            {validationErrors.state && <div className="lawfirm-error">{validationErrors.state}</div>}
                                        </div>
                                        
                                        <div className="lawfirm-form-group">
                                            <label className="lawfirm-label">Phone (Optional)</label>
                                            <input
                                                type="tel"
                                                name="phone"
                                                className="lawfirm-input"
                                                value={formData.phone}
                                                onChange={handleChange}
                                                placeholder="Contact number"
                                            />
                                        </div>
                                        
                                        <div className="lawfirm-form-group">
                                            <label className="lawfirm-label">Website (Optional)</label>
                                            <input
                                                type="url"
                                                name="website"
                                                className="lawfirm-input"
                                                value={formData.website}
                                                onChange={handleChange}
                                                placeholder="https://www.example.com"
                                            />
                                        </div>
                                    </div>
                                </section>
                                
                                {/* Section 2: Primary Lawyer Details */}
                                <section className="lawfirm-form-section">
                                    <div className="lawfirm-section-header">
                                        <div className="lawfirm-section-number">2</div>
                                        <h2 className="lawfirm-section-title">Primary Lawyer Details</h2>
                                    </div>
                                    
                                    <div className="lawfirm-form-grid">
                                        <div className="lawfirm-form-group">
                                            <label className="lawfirm-label required">Full Name</label>
                                            <input
                                                type="text"
                                                name="primary_lawyer_name"
                                                className={`lawfirm-input ${validationErrors.primary_lawyer_name ? 'error' : ''}`}
                                                value={formData.primary_lawyer_name || userData.full_name}
                                                onChange={handleChange}
                                                placeholder="Primary lawyer's full name"
                                                required
                                            />
                                            {validationErrors.primary_lawyer_name && <div className="lawfirm-error">{validationErrors.primary_lawyer_name}</div>}
                                        </div>
                                        
                                        <div className="lawfirm-form-group">
                                            <label className="lawfirm-label required">Bar Council ID</label>
                                            <input
                                                type="text"
                                                name="primary_lawyer_bar_council_id"
                                                className={`lawfirm-input ${validationErrors.primary_lawyer_bar_council_id ? 'error' : ''}`}
                                                value={formData.primary_lawyer_bar_council_id}
                                                onChange={handleChange}
                                                placeholder="Bar council registration ID"
                                                required
                                            />
                                            {validationErrors.primary_lawyer_bar_council_id && <div className="lawfirm-error">{validationErrors.primary_lawyer_bar_council_id}</div>}
                                        </div>
                                        
                                        <div className="lawfirm-form-group">
                                            <label className="lawfirm-label required">Years of Experience</label>
                                            <select
                                                name="primary_lawyer_years_experience"
                                                className={`lawfirm-select ${validationErrors.primary_lawyer_years_experience ? 'error' : ''}`}
                                                value={formData.primary_lawyer_years_experience}
                                                onChange={handleChange}
                                                required
                                            >
                                                <option value="">Select years</option>
                                                {experienceOptions.map(opt => (
                                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                                ))}
                                            </select>
                                            {validationErrors.primary_lawyer_years_experience && <div className="lawfirm-error">{validationErrors.primary_lawyer_years_experience}</div>}
                                        </div>
                                        
                                        <div className="lawfirm-form-group">
                                            <label className="lawfirm-label required">Specialization</label>
                                            <select
                                                name="primary_lawyer_specialization"
                                                className={`lawfirm-select ${validationErrors.primary_lawyer_specialization ? 'error' : ''}`}
                                                value={formData.primary_lawyer_specialization}
                                                onChange={handleLawyerSpecialization}
                                                required
                                            >
                                                <option value="">Select specialization</option>
                                                {lawyerSpecializationOptions.map(opt => (
                                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                                ))}
                                            </select>
                                            {validationErrors.primary_lawyer_specialization && <div className="lawfirm-error">{validationErrors.primary_lawyer_specialization}</div>}
                                        </div>
                                    </div>
                                </section>
                                
                                {/* Section 3: Team Members */}
                                <section className="lawfirm-form-section">
                                    <div className="lawfirm-section-header">
                                        <div className="lawfirm-section-number">3</div>
                                        <h2 className="lawfirm-section-title">Team Members</h2>
                                    </div>
                                    
                                    <div id="team-members-container">
                                        {teamMembers.map((member, index) => (
                                            <div key={member.id} className="lawfirm-team-member">
                                                <div className="lawfirm-team-member-header">
                                                    <h3>Team Member #{index + 1}</h3>
                                                    {teamMembers.length > 1 && (
                                                        <button type="button" className="lawfirm-remove-btn" onClick={() => removeTeamMember(member.id)}>
                                                            <i className="fas fa-times"></i>
                                                        </button>
                                                    )}
                                                </div>
                                                <div className="lawfirm-form-grid">
                                                    <div className="lawfirm-form-group">
                                                        <label className="lawfirm-label required">Name</label>
                                                        <input
                                                            type="text"
                                                            className={`lawfirm-input ${validationErrors[`member_name_${index}`] ? 'error' : ''}`}
                                                            value={member.name}
                                                            onChange={(e) => handleTeamMemberChange(member.id, 'name', e.target.value)}
                                                            placeholder="Team member's full name"
                                                            required
                                                        />
                                                    </div>
                                                    
                                                    <div className="lawfirm-form-group">
                                                        <label className="lawfirm-label required">Email</label>
                                                        <input
                                                            type="email"
                                                            className={`lawfirm-input ${validationErrors[`member_email_${index}`] ? 'error' : ''}`}
                                                            value={member.email}
                                                            onChange={(e) => handleTeamMemberChange(member.id, 'email', e.target.value)}
                                                            placeholder="Team member's email"
                                                            required
                                                        />
                                                    </div>
                                                    
                                                    <div className="lawfirm-form-group">
                                                        <label className="lawfirm-label required">Role</label>
                                                        <select
                                                            className={`lawfirm-select ${validationErrors[`member_role_${index}`] ? 'error' : ''}`}
                                                            value={member.role}
                                                            onChange={(e) => handleTeamMemberChange(member.id, 'role', e.target.value)}
                                                            required
                                                        >
                                                            <option value="">Select role</option>
                                                            {roleOptions.map(opt => (
                                                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                                                            ))}
                                                        </select>
                                                    </div>
                                                    
                                                    <div className="lawfirm-form-group">
                                                        <label className="lawfirm-label required">Experience (Years)</label>
                                                        <input
                                                            type="number"
                                                            className={`lawfirm-input ${validationErrors[`member_exp_${index}`] ? 'error' : ''}`}
                                                            value={member.experience}
                                                            onChange={(e) => handleTeamMemberChange(member.id, 'experience', e.target.value)}
                                                            placeholder="Years of experience"
                                                            min="0"
                                                            max="50"
                                                            required
                                                        />
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    
                                    <button type="button" className="lawfirm-add-btn" onClick={addTeamMember}>
                                        <i className="fas fa-plus"></i> Add Team Member
                                    </button>
                                </section>
                                
                                {/* Section 4: Documents */}
                                <section className="lawfirm-form-section">
                                    <div className="lawfirm-section-header">
                                        <div className="lawfirm-section-number">4</div>
                                        <h2 className="lawfirm-section-title">Documents Upload</h2>
                                    </div>
                                    
                                    <p className="lawfirm-documents-info">
                                        Upload the required documents for verification. All documents should be clear and legible.
                                    </p>
                                    
                                    <div 
                                        ref={dropAreaRef}
                                        className="lawfirm-file-drop-area"
                                        onClick={() => fileInputRef.current?.click()}
                                        onDragOver={handleDragOver}
                                        onDragLeave={handleDragLeave}
                                        onDrop={handleDrop}
                                    >
                                        <div className="lawfirm-file-upload-icon">
                                            <i className="fas fa-cloud-upload-alt"></i>
                                        </div>
                                        <h3>Drag & Drop Files Here</h3>
                                        <p>or click to browse files</p>
                                        <input
                                            type="file"
                                            ref={fileInputRef}
                                            multiple
                                            style={{ display: 'none' }}
                                            onChange={handleFileSelect}
                                        />
                                        <button type="button" className="lawfirm-browse-btn">
                                            <i className="fas fa-folder-open"></i> Browse Files
                                        </button>
                                    </div>
                                    
                                    <div>
                                        <h3 className="lawfirm-documents-title">Required Documents:</h3>
                                        <ul className="lawfirm-file-list">
                                            <li className="lawfirm-file-item">
                                                <div className="lawfirm-file-info">
                                                    <div className="lawfirm-file-icon">
                                                        <i className="fas fa-file-certificate"></i>
                                                    </div>
                                                    <div>
                                                        <div style={{ fontWeight: 500 }}>Bar Council Certificate</div>
                                                        <div className="lawfirm-file-hint">Upload certificate of primary lawyer</div>
                                                    </div>
                                                </div>
                                                <div className={`lawfirm-doc-status ${docStatus.bar_certificate ? 'uploaded' : ''}`}>
                                                    {docStatus.bar_certificate ? 'Uploaded' : 'Not uploaded'}
                                                </div>
                                            </li>
                                            <li className="lawfirm-file-item">
                                                <div className="lawfirm-file-info">
                                                    <div className="lawfirm-file-icon">
                                                        <i className="fas fa-file-contract"></i>
                                                    </div>
                                                    <div>
                                                        <div style={{ fontWeight: 500 }}>Firm Registration Proof</div>
                                                        <div className="lawfirm-file-hint">Upload firm registration document</div>
                                                    </div>
                                                </div>
                                                <div className={`lawfirm-doc-status ${docStatus.firm_registration ? 'uploaded' : ''}`}>
                                                    {docStatus.firm_registration ? 'Uploaded' : 'Not uploaded'}
                                                </div>
                                            </li>
                                            <li className="lawfirm-file-item">
                                                <div className="lawfirm-file-info">
                                                    <div className="lawfirm-file-icon">
                                                        <i className="fas fa-id-card"></i>
                                                    </div>
                                                    <div>
                                                        <div style={{ fontWeight: 500 }}>ID Proof</div>
                                                        <div className="lawfirm-file-hint">Government-issued ID of primary lawyer</div>
                                                    </div>
                                                </div>
                                                <div className={`lawfirm-doc-status ${docStatus.id_proof ? 'uploaded' : ''}`}>
                                                    {docStatus.id_proof ? 'Uploaded' : 'Not uploaded'}
                                                </div>
                                            </li>
                                        </ul>
                                    </div>
                                    
                                    {uploadedFiles.length > 0 && (
                                        <div className="lawfirm-uploaded-files">
                                            <h3>Uploaded Files:</h3>
                                            <ul className="lawfirm-file-list">
                                                {uploadedFiles.map(file => (
                                                    <li key={file.id} className="lawfirm-file-item">
                                                        <div className="lawfirm-file-info">
                                                            <div className="lawfirm-file-icon">
                                                                <i className={`fas ${getFileIcon(file.type)}`}></i>
                                                            </div>
                                                            <div>
                                                                <div style={{ fontWeight: 500 }}>{file.name}</div>
                                                                <div className="lawfirm-file-hint">{file.size}</div>
                                                            </div>
                                                        </div>
                                                        <button type="button" className="lawfirm-remove-doc" onClick={() => removeUploadedFile(file.id)}>
                                                            <i className="fas fa-times"></i>
                                                        </button>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </section>
                                
                                <button type="submit" className="lawfirm-submit-btn" disabled={loading}>
                                    <i className={`fas ${loading ? 'fa-spinner fa-spin' : 'fa-check-circle'}`}></i>
                                    {loading ? ' Submitting...' : ' Submit for Verification'}
                                </button>
                            </form>
                        </div>
                        
                        {/* Sidebar */}
                        <div className="lawfirm-sidebar">
                            <div className="lawfirm-progress-card">
                                <h3 className="lawfirm-progress-title">
                                    <i className="fas fa-tasks"></i> Onboarding Progress
                                </h3>
                                <div className="lawfirm-progress-bar">
                                    <div className="lawfirm-progress-fill" style={{ width: `${progress}%` }}></div>
                                </div>
                                <ul className="lawfirm-progress-steps">
                                    <li className={`lawfirm-progress-step ${progress >= 25 ? 'completed' : 'active'}`}>
                                        <div className="lawfirm-step-icon">1</div>
                                        <div>Firm Details</div>
                                    </li>
                                    <li className={`lawfirm-progress-step ${progress >= 50 ? 'completed' : progress >= 25 ? 'active' : ''}`}>
                                        <div className="lawfirm-step-icon">2</div>
                                        <div>Primary Lawyer</div>
                                    </li>
                                    <li className={`lawfirm-progress-step ${progress >= 75 ? 'completed' : progress >= 50 ? 'active' : ''}`}>
                                        <div className="lawfirm-step-icon">3</div>
                                        <div>Team Members</div>
                                    </li>
                                    <li className={`lawfirm-progress-step ${progress >= 100 ? 'completed' : progress >= 75 ? 'active' : ''}`}>
                                        <div className="lawfirm-step-icon">4</div>
                                        <div>Documents</div>
                                    </li>
                                </ul>
                            </div>
                            
                            <div className="lawfirm-status-card">
                                <div className="lawfirm-status-icon">
                                    <i className="fas fa-hourglass-half"></i>
                                </div>
                                <h3 className="lawfirm-status-title">Pending Verification</h3>
                                <p className="lawfirm-status-text">
                                    After submission, your firm details will be reviewed by our admin team. This process typically takes 2-3 business days.
                                </p>
                                <div className="lawfirm-status-warning">
                                    <div className="lawfirm-status-warning-item">
                                        <i className="fas fa-lock"></i> Dashboard will be read-only
                                    </div>
                                    <div className="lawfirm-status-warning-item">
                                        <i className="fas fa-ban"></i> Cannot accept new cases
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Success Modal (kept for backward compatibility) */}
            {showSuccessModal && (
                <div className="lawfirm-modal-overlay">
                    <div className="lawfirm-modal-content">
                        <div className="lawfirm-modal-icon">
                            <i className="fas fa-check-circle"></i>
                        </div>
                        <h2 className="lawfirm-modal-title">Submission Successful!</h2>
                        <p className="lawfirm-modal-text">
                            Your law firm onboarding details have been submitted successfully for verification.
                            Our admin team will review your submission and you will be notified once the verification is complete.
                        </p>
                        <p className="lawfirm-modal-status">
                            <i className="fas fa-info-circle"></i> Status: Pending Admin Approval
                        </p>
                        <button className="lawfirm-modal-btn" onClick={handleModalClose}>
                            Go to Dashboard
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}

export default LawfirmOnboarding;