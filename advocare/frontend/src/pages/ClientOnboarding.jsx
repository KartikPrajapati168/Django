import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';
import styles from '../assets/styles/onboarding.module.css';

function ClientOnboarding() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [userData, setUserData] = useState({
    full_name: '',
    email: '',
    phone: '',
    city: '',
  });

  // Form fields
  const [profileData, setProfileData] = useState({
    date_of_birth: '',
    occupation: '',
    occupation_other: '',
    address_line1: '',
    address_line2: '',
    landmark: '',
    pincode: '',
  });

  const [idProof, setIdProof] = useState({
    type: '',
    type_other: '',
    number: '',
    issue_date: '',
    expiry_date: '',
    file: null,
  });

  const [caseDetails, setCaseDetails] = useState({
    title: '',
    description: '',
    type: '',
    urgency: 'normal',
    court_location: '',
    opposing_party: '',
    filing_deadline: '',
  });

  // Documents
  const [documents, setDocuments] = useState({
    fir: [],
    notice: [],
    evidence: [],
    correspondence: [],
    other: [],
  });

  const [consent, setConsent] = useState({
    terms: false,
    data: false,
    marketing: false,
  });

  const [showModal, setShowModal] = useState(false);

  // Load user data
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Please login first');
      navigate('/');
      return;
    }

    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      const user = JSON.parse(storedUser);
      setUserData({
        full_name: user.full_name || '',
        email: user.email || '',
        phone: user.phone || '',
        city: user.city || '',
      });
    } else {
      API.get('users/profile/')
        .then((res) => {
          setUserData({
            full_name: res.data.full_name || '',
            email: res.data.email || '',
            phone: res.data.phone || '',
            city: res.data.city || '',
          });
        })
        .catch((err) => console.warn('Could not load profile', err));
    }
  }, [navigate]);

  // Handlers
  const handleProfileChange = (e) => {
    setProfileData({ ...profileData, [e.target.name]: e.target.value });
  };

  const handleIdProofChange = (e) => {
    setIdProof({ ...idProof, [e.target.name]: e.target.value });
  };

  const handleCaseChange = (e) => {
    const { name, value } = e.target;
    setCaseDetails({ ...caseDetails, [name]: value });
  };

  const handleConsentChange = (e) => {
    setConsent({ ...consent, [e.target.name]: e.target.checked });
  };

  const handleFileSelect = (docType, files) => {
    const fileList = Array.from(files);
    setDocuments((prev) => ({
      ...prev,
      [docType]: [...prev[docType], ...fileList],
    }));
  };

  const removeFile = (docType, index) => {
    setDocuments((prev) => ({
      ...prev,
      [docType]: prev[docType].filter((_, i) => i !== index),
    }));
  };

  const handleIdProofTypeChange = (e) => {
    const val = e.target.value;
    setIdProof({ ...idProof, type: val });
  };

  const handleOccupationChange = (e) => {
    const val = e.target.value;
    setProfileData({ ...profileData, occupation: val });
  };

  // Validation
  const validateForm = () => {
    if (!idProof.type) {
      alert('Please select ID proof type');
      return false;
    }
    if (!idProof.number) {
      alert('Please enter ID proof number');
      return false;
    }
    if (!idProof.file) {
      alert('Please upload ID proof document');
      return false;
    }
    if (profileData.pincode && !/^\d{6}$/.test(profileData.pincode)) {
      alert('Pincode must be 6 digits');
      return false;
    }
    if (!caseDetails.type) {
      alert('Please select case type');
      return false;
    }
    if (!caseDetails.title.trim()) {
      alert('Please enter case title');
      return false;
    }
    if (!caseDetails.description.trim()) {
      alert('Please describe your case');
      return false;
    }
    if (documents.fir.length === 0 && documents.notice.length === 0) {
      alert('Please upload at least one primary document (FIR or Notice/Agreement)');
      return false;
    }
    if (!consent.terms) {
      alert('You must accept the terms');
      return false;
    }
    return true;
  };

  // Submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    const formData = new FormData();

    // Append all fields
    formData.append('full_name', userData.full_name);
    formData.append('email', userData.email);
    formData.append('phone', userData.phone);
    formData.append('city', userData.city);
    formData.append('date_of_birth', profileData.date_of_birth);
    let occupation = profileData.occupation;
    if (occupation === 'other') occupation = profileData.occupation_other;
    formData.append('occupation', occupation);
    formData.append('address', `${profileData.address_line1} ${profileData.address_line2}`.trim());
    formData.append('landmark', profileData.landmark);
    formData.append('pincode', profileData.pincode);

    formData.append('id_proof_type', idProof.type === 'other' ? idProof.type_other : idProof.type);
    formData.append('id_proof_number', idProof.number);
    formData.append('id_proof_issue_date', idProof.issue_date);
    formData.append('id_proof_expiry_date', idProof.expiry_date);
    if (idProof.file) formData.append('id_proof_document', idProof.file);

    formData.append('case_title', caseDetails.title);
    formData.append('case_description', caseDetails.description);
    formData.append('case_type', caseDetails.type);
    formData.append('case_urgency', caseDetails.urgency);
    formData.append('court_location', caseDetails.court_location);
    formData.append('opposing_party', caseDetails.opposing_party);
    formData.append('filing_deadline', caseDetails.filing_deadline);

    Object.entries(documents).forEach(([docType, files]) => {
      files.forEach((file) => {
        formData.append(`documents_${docType}`, file);
      });
    });

    formData.append('terms_accepted', consent.terms);
    formData.append('data_consent', consent.data);
    formData.append('marketing_consent', consent.marketing);

    try {
      const token = localStorage.getItem('access_token');
      const response = await API.post('clients/onboarding/', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      if (response.data.success) {
        setShowModal(true);
      } else {
        alert('Submission failed: ' + (response.data.message || 'Unknown error'));
      }
    } catch (err) {
      console.error('Onboarding error:', err);
      alert('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToHome = () => {
    setShowModal(false);
    navigate('/');
  };

  const handleStay = () => {
    setShowModal(false);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <>
      <header className={styles.header}>
        <div className={styles.headerContainer}>
          <div className={styles.logo}>
            <div className={styles.logoIcon}>
              <i className="fas fa-balance-scale"></i>
            </div>
            <div className={styles.logoText}>Advocare</div>
          </div>
          <div className={styles.userInfo}>
            <div className={styles.userAvatar}>
              {userData.full_name ? userData.full_name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div>
              <div id="userName">{userData.full_name || 'Loading...'}</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>Client</div>
            </div>
          </div>
        </div>
      </header>

      <div className={styles.onboardingContainer}>
        <h1 className={styles.pageTitle}>Client Onboarding</h1>
        <p className={styles.pageSubtitle}>Complete your profile, ID verification, and case details</p>

        <div className={styles.progressIndicator}>
          <div className={styles.progressStep}>
            <div className={`${styles.stepCircle} ${styles.completed}`}>1</div>
            <div className={styles.stepLabel}>Profile</div>
          </div>
          <div className={styles.progressStep}>
            <div className={`${styles.stepCircle} ${styles.completed}`}>2</div>
            <div className={styles.stepLabel}>ID Proof</div>
          </div>
          <div className={styles.progressStep}>
            <div className={`${styles.stepCircle} ${styles.active}`}>3</div>
            <div className={`${styles.stepLabel} ${styles.active}`}>Case Details</div>
          </div>
          <div className={styles.progressStep}>
            <div className={styles.stepCircle}>4</div>
            <div className={styles.stepLabel}>Documents</div>
          </div>
          <div className={styles.progressStep}>
            <div className={styles.stepCircle}>5</div>
            <div className={styles.stepLabel}>Review</div>
          </div>
        </div>

        <form id="onboardingForm" className={styles.formContainer} onSubmit={handleSubmit}>
          {/* Section 1: Profile Information (read-only) */}
          <section className={styles.formSection}>
            <h2 className={styles.sectionTitle}><i className="fas fa-id-card"></i> Your Profile Information</h2>
            <div className={styles.infoBox}>
              <i className="fas fa-info-circle"></i>
              <div className={styles.infoContent}>
                <p>This information is from your registration and cannot be changed here.</p>
                <small>To update these details, go to your profile settings after onboarding.</small>
              </div>
            </div>
            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label>Username</label>
                <input type="text" className={styles.autoFilled} readOnly value={userData.full_name} />
              </div>
              <div className={styles.formGroup}>
                <label>Email Address</label>
                <input type="email" className={styles.autoFilled} readOnly value={userData.email} />
              </div>
            </div>
            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label>Phone Number</label>
                <input type="tel" className={styles.autoFilled} readOnly value={userData.phone} />
              </div>
              <div className={styles.formGroup}>
                <label>City</label>
                <input type="text" className={styles.autoFilled} readOnly value={userData.city} />
              </div>
            </div>
          </section>

          {/* Section 2: Identity Proof Documents */}
          <section className={styles.formSection}>
            <h2 className={styles.sectionTitle}><i className="fas fa-id-card"></i> Identity Proof Documents</h2>
            <div className={styles.infoBox}>
              <i className="fas fa-shield-alt"></i>
              <div className={styles.infoContent}>
                <p><strong>Why we need this?</strong> To verify your identity as per legal requirements.</p>
                <small>Your documents are encrypted and securely stored.</small>
              </div>
            </div>

            <div className={styles.documentSection}>
              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label htmlFor="idProofType" className={styles.required}>ID Proof Type</label>
                  <select id="idProofType" name="type" value={idProof.type} onChange={handleIdProofTypeChange} required>
                    <option value="" disabled>Select ID proof type</option>
                    <option value="aadhar">Aadhar Card</option>
                    <option value="pan">PAN Card</option>
                    <option value="passport">Passport</option>
                    <option value="voter">Voter ID</option>
                    <option value="driving">Driving License</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div className={styles.formGroup}>
                  <label htmlFor="idProofNumber" className={styles.required}>ID Proof Number</label>
                  <input type="text" id="idProofNumber" name="number" value={idProof.number} onChange={handleIdProofChange} placeholder="Enter your ID number" required />
                </div>
              </div>

              {idProof.type === 'other' && (
                <div className={styles.formGroup} id="otherIdProofGroup">
                  <label htmlFor="idProofOther">Please specify ID proof type</label>
                  <input type="text" id="idProofOther" name="type_other" value={idProof.type_other} onChange={handleIdProofChange} placeholder="e.g., Ration Card, Birth Certificate" />
                </div>
              )}

              <div className={styles.formGroup}>
                <label className={styles.required}>Upload ID Proof Document</label>
                <div className={styles.documentCard} onClick={() => document.getElementById('idProofFile').click()}>
                  <span className={`${styles.documentBadge} ${styles.badgeRequired}`}>Required</span>
                  <i className={`fas fa-cloud-upload-alt ${styles.documentIcon}`}></i>
                  <div className={styles.documentTitle}>Click to upload ID proof</div>
                  <div className={styles.documentHint}>PDF, JPG, PNG (Max 10MB)</div>
                  <input type="file" id="idProofFile" accept=".pdf,.jpg,.jpeg,.png" className={styles.fileInput} onChange={(e) => setIdProof({ ...idProof, file: e.target.files[0] })} />
                  {idProof.file && (
                    <div className={`${styles.filePreview} ${styles.active}`}>
                      <div className={styles.filePreviewItem}>
                        <div className={styles.fileInfo}>
                          <i className="fas fa-file-pdf"></i>
                          <div>
                            <div className={styles.fileName}>{idProof.file.name}</div>
                            <div className={styles.fileSize}>{formatFileSize(idProof.file.size)}</div>
                          </div>
                        </div>
                        <div className={styles.fileRemove} onClick={(e) => { e.stopPropagation(); setIdProof({ ...idProof, file: null }); }}>
                          <i className="fas fa-times"></i>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label htmlFor="idProofIssueDate">Issue Date (if available)</label>
                  <input type="date" id="idProofIssueDate" name="issue_date" value={idProof.issue_date} onChange={handleIdProofChange} />
                </div>
                <div className={styles.formGroup}>
                  <label htmlFor="idProofExpiryDate">Expiry Date (if applicable)</label>
                  <input type="date" id="idProofExpiryDate" name="expiry_date" value={idProof.expiry_date} onChange={handleIdProofChange} />
                </div>
              </div>
            </div>
          </section>

          {/* Section 3: Additional Personal Details */}
          <section className={styles.formSection}>
            <h2 className={styles.sectionTitle}><i className="fas fa-user-plus"></i> Additional Personal Details</h2>
            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="dateOfBirth">Date of Birth</label>
                <input type="date" id="dateOfBirth" name="date_of_birth" value={profileData.date_of_birth} onChange={handleProfileChange} />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="occupation">Occupation</label>
                <select id="occupation" name="occupation" value={profileData.occupation} onChange={handleOccupationChange}>
                  <option value="">Select occupation</option>
                  <option value="salaried">Salaried Employee</option>
                  <option value="business">Business Owner</option>
                  <option value="self_employed">Self Employed</option>
                  <option value="student">Student</option>
                  <option value="homemaker">Homemaker</option>
                  <option value="retired">Retired</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            {profileData.occupation === 'other' && (
              <div className={styles.formGroup} id="otherOccupationGroup">
                <label htmlFor="occupationOther">Please specify occupation</label>
                <input type="text" id="occupationOther" name="occupation_other" value={profileData.occupation_other} onChange={handleProfileChange} placeholder="Enter your occupation" />
              </div>
            )}

            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="addressLine1">Address Line 1</label>
                <input type="text" id="addressLine1" name="address_line1" value={profileData.address_line1} onChange={handleProfileChange} placeholder="House/Flat number, Building name" />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="addressLine2">Address Line 2</label>
                <input type="text" id="addressLine2" name="address_line2" value={profileData.address_line2} onChange={handleProfileChange} placeholder="Street, Area, Locality" />
              </div>
            </div>

            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="landmark">Landmark (Optional)</label>
                <input type="text" id="landmark" name="landmark" value={profileData.landmark} onChange={handleProfileChange} placeholder="Nearby landmark" />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="pincode">Pincode</label>
                <input type="text" id="pincode" name="pincode" value={profileData.pincode} onChange={handleProfileChange} placeholder="6-digit pincode" maxLength="6" />
              </div>
            </div>
          </section>

          {/* Section 4: Case Details */}
          <section className={styles.formSection}>
            <h2 className={styles.sectionTitle}><i className="fas fa-gavel"></i> Case Details</h2>
            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="caseType" className={styles.required}>Case Type</label>
                <select id="caseType" name="type" value={caseDetails.type} onChange={handleCaseChange} required>
                  <option value="" disabled>Select case type</option>
                  <option value="criminal">Criminal Law</option>
                  <option value="civil">Civil Law</option>
                  <option value="family">Family Law</option>
                  <option value="corporate">Corporate Law</option>
                  <option value="property">Property Law</option>
                  <option value="tax">Tax Law</option>
                  <option value="employment">Employment Law</option>
                  <option value="intellectual">Intellectual Property</option>
                </select>
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="caseTitle" className={styles.required}>Short Case Title</label>
                <input type="text" id="caseTitle" name="title" value={caseDetails.title} onChange={handleCaseChange} placeholder="e.g., Property Dispute with Neighbor" required />
              </div>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="caseDescription" className={styles.required}>Case Description</label>
              <textarea id="caseDescription" name="description" rows="4" value={caseDetails.description} onChange={handleCaseChange} placeholder="Describe your case in detail. Include important dates, parties involved, and what you hope to achieve." required></textarea>
            </div>

            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label className={styles.required}>Case Urgency</label>
                <div className={styles.radioGroup}>
                  <label className={styles.radioOption}>
                    <input type="radio" name="urgency" value="normal" checked={caseDetails.urgency === 'normal'} onChange={handleCaseChange} />
                    <span className={styles.urgencyNormal}>Normal (within 30 days)</span>
                  </label>
                  <label className={styles.radioOption}>
                    <input type="radio" name="urgency" value="high" checked={caseDetails.urgency === 'high'} onChange={handleCaseChange} />
                    <span style={{ color: '#e67e22', fontWeight: 600 }}>High (within 7 days)</span>
                  </label>
                  <label className={styles.radioOption}>
                    <input type="radio" name="urgency" value="urgent" checked={caseDetails.urgency === 'urgent'} onChange={handleCaseChange} />
                    <span className={styles.urgencyHigh}>Urgent (within 24-48 hours)</span>
                  </label>
                </div>
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="courtLocation">Preferred Court/Location</label>
                <input type="text" id="courtLocation" name="court_location" value={caseDetails.court_location} onChange={handleCaseChange} placeholder="e.g., Delhi High Court, Saket Court" />
              </div>
            </div>

            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label htmlFor="opposingParty">Opposing Party (if any)</label>
                <input type="text" id="opposingParty" name="opposing_party" value={caseDetails.opposing_party} onChange={handleCaseChange} placeholder="Name of person/company you're filing against" />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="filingDeadline">Filing Deadline (if any)</label>
                <input type="date" id="filingDeadline" name="filing_deadline" value={caseDetails.filing_deadline} onChange={handleCaseChange} />
              </div>
            </div>
          </section>

          {/* Section 5: Case Documents */}
          <section className={styles.formSection}>
            <h2 className={styles.sectionTitle}><i className="fas fa-file-alt"></i> Case Documents</h2>
            <div className={styles.infoBox}>
              <i className="fas fa-file-pdf"></i>
              <div className={styles.infoContent}>
                <p><strong>Required:</strong> FIR / Notice / Agreement (Primary document)</p>
                <small>Supporting documents help strengthen your case.</small>
              </div>
            </div>

            <div className={styles.documentGrid}>
              {['fir', 'notice', 'evidence', 'correspondence', 'other'].map((docType) => {
                const labels = {
                  fir: { title: 'FIR Document', hint: 'First Information Report (if filed)', required: true },
                  notice: { title: 'Notice / Agreement', hint: 'Legal notice, agreement, or contract', required: true },
                  evidence: { title: 'Evidence Documents', hint: 'Photos, screenshots, proof', required: false },
                  correspondence: { title: 'Correspondence', hint: 'Emails, letters, WhatsApp chats', required: false },
                  other: { title: 'Other Documents', hint: 'Any other relevant documents', required: false },
                };
                const l = labels[docType];
                return (
                  <div key={docType} className={styles.documentCard} onClick={() => document.getElementById(`${docType}FileInput`).click()}>
                    <span className={`${styles.documentBadge} ${l.required ? styles.badgeRequired : styles.badgeOptional}`}>
                      {l.required ? 'Required' : 'Optional'}
                    </span>
                    <i className={`fas ${docType === 'fir' ? 'fa-file-alt' : docType === 'notice' ? 'fa-file-contract' : docType === 'evidence' ? 'fa-image' : docType === 'correspondence' ? 'fa-envelope' : 'fa-folder-open'} ${styles.documentIcon}`}></i>
                    <div className={styles.documentTitle}>{l.title}</div>
                    <div className={styles.documentHint}>{l.hint}</div>
                    <input type="file" id={`${docType}FileInput`} accept=".pdf,.jpg,.jpeg,.png" multiple className={styles.fileInput} onChange={(e) => handleFileSelect(docType, e.target.files)} />
                    {documents[docType].length > 0 && (
                      <div className={`${styles.filePreview} ${styles.active}`}>
                        {documents[docType].map((file, idx) => (
                          <div key={idx} className={styles.filePreviewItem}>
                            <div className={styles.fileInfo}>
                              <i className="fas fa-file-pdf"></i>
                              <div>
                                <div className={styles.fileName}>{file.name}</div>
                                <div className={styles.fileSize}>{formatFileSize(file.size)}</div>
                              </div>
                            </div>
                            <div className={styles.fileRemove} onClick={(e) => { e.stopPropagation(); removeFile(docType, idx); }}>
                              <i className="fas fa-times"></i>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {Object.values(documents).some(arr => arr.length > 0) && (
              <div className={styles.documentList} id="documentList">
                <div className={styles.documentListTitle}>
                  <i className="fas fa-list"></i>
                  <span>Uploaded Documents Summary</span>
                </div>
                <div id="documentListItems">
                  {Object.entries(documents).map(([docType, files]) =>
                    files.map((file, idx) => (
                      <div key={`${docType}-${idx}`} className={styles.filePreviewItem} style={{ marginBottom: '5px' }}>
                        <div className={styles.fileInfo}>
                          <i className="fas fa-file-pdf"></i>
                          <span className={styles.fileName}>
                            {docType === 'fir' ? 'FIR' : docType === 'notice' ? 'Notice/Agreement' : docType === 'evidence' ? 'Evidence' : docType === 'correspondence' ? 'Correspondence' : 'Other'}: {file.name}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </section>

          {/* Section 6: Terms & Consent */}
          <section className={styles.formSection}>
            <h2 className={styles.sectionTitle}><i className="fas fa-file-signature"></i> Terms & Consent</h2>
            <div className={styles.formGroup}>
              <label className={styles.checkboxOption}>
                <span>I confirm that all information provided is true and correct to the best of my knowledge.</span>
                <input type="checkbox" name="terms" checked={consent.terms} onChange={handleConsentChange} required />
              </label>
            </div>
            <div className={styles.formGroup}>
              <label className={styles.checkboxOption}>
                <span>I consent to the processing of my personal data as per the privacy policy.</span>
                <input type="checkbox" name="data" checked={consent.data} onChange={handleConsentChange} required />
              </label>
            </div>
            <div className={styles.formGroup}>
              <label className={styles.checkboxOption}>
                <span>I would like to receive updates and marketing communications (optional).</span>
                <input type="checkbox" name="marketing" checked={consent.marketing} onChange={handleConsentChange} />
              </label>
            </div>
          </section>

          <div className={styles.submitSection}>
            <button type="submit" className={styles.submitBtn} disabled={loading}>
              <i className={`fas ${loading ? 'fa-spinner fa-spin' : 'fa-paper-plane'}`}></i>
              {loading ? ' Submitting...' : ' Submit for Verification'}
            </button>
            <p style={{ marginTop: '1rem', color: '#718096', fontSize: '0.9rem' }}>
              Your documents will be verified by our team within 24-48 hours.
            </p>
          </div>
        </form>

      </div>
        <footer className={styles.footer}>
          <p>© 2025 Advocate Legal Case Management System. All rights reserved.</p>
          <p style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>This information is confidential and protected by attorney-client privilege.</p>
        </footer>

      {/* Modal */}
      {showModal && (
        <div className={styles.statusModal} style={{ display: 'flex' }}>
          <div className={styles.modalContent}>
            <div className={styles.modalIcon}>
              <i className="fas fa-check-circle"></i>
            </div>
            <h2 className={styles.modalTitle}>Submission Successful!</h2>
            <p className={styles.modalText}>
              Your case has been submitted successfully. Our team will verify your documents and get back to you within 24-48 hours.
            </p>
            <p className={styles.modalText} style={{ fontWeight: 600, color: 'var(--primary-color)' }}>
              Status: <span style={{ color: 'var(--warning-color)' }}>Pending Verification</span>
            </p>
            <div className={styles.modalBtnGroup}>
              <button className={styles.modalBtn} onClick={handleBackToHome}>
                <i className="fas fa-home"></i> Back to Home
              </button>
              <button className={styles.modalBtnSecondary} onClick={handleStay}>
                Stay on this page
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default ClientOnboarding;