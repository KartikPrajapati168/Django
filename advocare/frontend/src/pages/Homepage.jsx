import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';   // assuming your API service exists

function Homepage() {
    const navigate = useNavigate();
    const [scrolled, setScrolled] = useState(false);
    const [currentSlide, setCurrentSlide] = useState(0);
    const [modalOpen, setModalOpen] = useState(false);
    const [aiCaseDesc, setAiCaseDesc] = useState('');
    const [aiSuggestion, setAiSuggestion] = useState('');
    const [contactForm, setContactForm] = useState({
        fullName: '',
        email: '',
        phone: '',
        subject: '',
        message: ''
    });
    const [formSubmitting, setFormSubmitting] = useState(false);
    const [formMessage, setFormMessage] = useState('');
    
    const sliderRef = useRef(null);
    const slideInterval = useRef(null);
    const totalSlides = 3;

    // Law firms data
    const lawFirms = [
        {
            id: 1,
            name: "Hale & Associates - Global Criminal Defense",
            image: "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&h=500&fit=crop",
            description: "Leading firm specializing in high-profile criminal cases, with a track record of defending clients in international courts. Focus on evidence analysis and plea bargaining.",
            lawyers: [
                { name: "John Hale", desc: "Senior Advocate, 20+ years in criminal law, expert in fraud and white-collar crimes." },
                { name: "Sarah Mitchell", desc: "Junior Lawyer, specializes in juvenile justice and rehabilitation programs." }
            ]
        },
        {
            id: 2,
            name: "Vasquez Litigation Partners - Civil Experts",
            image: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=500&fit=crop",
            description: "Renowned for civil litigation, contract disputes, and property law. They provide comprehensive strategies for dispute resolution and mediation.",
            lawyers: [
                { name: "Maria Vasquez", desc: "Lead Advocate, 15 years experience in civil suits, known for innovative settlement tactics." },
                { name: "David Chen", desc: "Associate Lawyer, focuses on intellectual property and commercial disputes." }
            ]
        },
        {
            id: 3,
            name: "Reed Family Law Group - Authority in Matrimonial",
            image: "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&h=500&fit=crop",
            description: "Experts in family law, including divorce, custody, and adoption. Committed to compassionate representation and child welfare.",
            lawyers: [
                { name: "Emily Reed", desc: "Principal Advocate, 18 years in family matters, mediator certified by international bodies." },
                { name: "Robert Kline", desc: "Family Lawyer, specializes in domestic violence and asset division." }
            ]
        }
    ];

    // Feature slides data
    const featureSlides = [
        [
            { title: "Case Matching", desc: "AI suggestions for multiple law firms based on your case. Advanced algorithms match your specific legal needs with the most qualified firms.", icon: "https://images.unsplash.com/photo-1555374018-13a8994ab246?w=300&h=300&fit=crop" },
            { title: "Law Firm Onboarding", desc: "Law firms can easily register, create profiles, and find cases. Streamlined process with verification and approval systems.", icon: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=300&h=300&fit=crop" },
            { title: "Document Management", desc: "Upload and share case files with secure cloud storage. Organized filing system with version control and access permissions.", icon: "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=300&h=300&fit=crop" }
        ],
        [
            { title: "Select Desired Law Firms", desc: "Users can browse and select preferred law firms based on expertise, ratings, and location for personalized case matching.", icon: "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=300&h=300&fit=crop" },
            { title: "Centralized Data Management", desc: "Law firms manage all their data in one secure dashboard, including cases, clients, and analytics across multiple practices.", icon: "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=300&h=300&fit=crop" },
            { title: "AI Assistance System", desc: "Intelligent AI chatbots and predictive analytics provide real-time legal advice, case predictions, and workflow automation.", icon: "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=300&h=300&fit=crop" }
        ],
        [
            { title: "Rights Management", desc: "Granular role-based permissions ensure data privacy with advanced encryption, audit trails, and multi-factor authentication.", icon: "https://images.unsplash.com/photo-1552664730-d307ca884978?w=300&h=300&fit=crop" },
            { title: "Advanced Analytics", desc: "Comprehensive reporting and analytics tools to track case progress, firm performance, and client satisfaction metrics.", icon: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=300&h=300&fit=crop" },
            { title: "Mobile Access", desc: "Access your case management system on-the-go with our mobile-responsive design and dedicated mobile applications.", icon: "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop" }
        ]
    ];

    // Handle scroll effect
    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 50);
            
            const sections = document.querySelectorAll('.homepage-section, .homepage-feature-hero, .homepage-lawfirms');
            sections.forEach(section => {
                const rect = section.getBoundingClientRect();
                if (rect.top < window.innerHeight * 0.9 && rect.bottom > 0) {
                    section.classList.add('visible');
                }
            });
        };
        
        window.addEventListener('scroll', handleScroll);
        handleScroll();
        
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    // Auto slide for feature slider
    useEffect(() => {
        startAutoSlide();
        return () => {
            if (slideInterval.current) clearInterval(slideInterval.current);
        };
    }, []);

    const startAutoSlide = () => {
        if (slideInterval.current) clearInterval(slideInterval.current);
        slideInterval.current = setInterval(() => {
            setCurrentSlide(prev => (prev + 1) % totalSlides);
        }, 5000);
    };

    const pauseAutoSlide = () => {
        if (slideInterval.current) clearInterval(slideInterval.current);
    };

    const resumeAutoSlide = () => {
        startAutoSlide();
    };

    const goToSlide = (index) => {
        setCurrentSlide(index);
    };

    const scrollToSection = (sectionId) => {
        const element = document.getElementById(sectionId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    };

    const handleAISuggestion = () => {
        if (aiCaseDesc.trim()) {
            let suggestion = "Based on your case description, we recommend approaching ";
            const desc = aiCaseDesc.toLowerCase();
            if (desc.includes('criminal') || desc.includes('theft') || desc.includes('assault')) {
                suggestion += "<strong>Hale & Associates</strong> - Experts in criminal defense with a 95% success rate. They specialize in evidence analysis and plea bargaining.";
            } else if (desc.includes('family') || desc.includes('divorce') || desc.includes('custody')) {
                suggestion += "<strong>Reed Family Law Group</strong> - Specializing in matrimonial and family disputes. They offer compassionate representation and mediation services.";
            } else if (desc.includes('civil') || desc.includes('contract') || desc.includes('property')) {
                suggestion += "<strong>Vasquez Litigation Partners</strong> - Leaders in civil litigation and contract disputes. Known for innovative settlement strategies.";
            } else {
                suggestion += "one of our top partner firms for comprehensive legal support. Our AI will match you with the most suitable firm based on your specific needs.";
            }
            setAiSuggestion(suggestion);
        }
    };

    // Contact form submission to backend
    const handleContactSubmit = async (e) => {
        e.preventDefault();
        setFormSubmitting(true);
        setFormMessage('');
        
        try {
            const response = await API.post('/contact/', contactForm);
            if (response.data.success || response.status === 200 || response.status === 201) {
                setFormMessage('Thank you for your message! We will get back to you soon.');
                setContactForm({ fullName: '', email: '', phone: '', subject: '', message: '' });
            } else {
                setFormMessage('Something went wrong. Please try again later.');
            }
        } catch (error) {
            console.error('Contact form error:', error);
            setFormMessage(error.response?.data?.message || 'Failed to send message. Please check your connection.');
        } finally {
            setFormSubmitting(false);
        }
    };

    const handleLogin = () => {
        navigate('/');
    };

    return (
        <div className="homepage-container">
            <header className={`homepage-header ${scrolled ? 'scrolled' : ''}`}>
                <nav className="homepage-nav">
                    <div className="homepage-logo">Advocare</div>
                    <ul className="homepage-nav-links">
                        <li><a href="#home" onClick={(e) => { e.preventDefault(); scrollToSection('home'); }}>Home</a></li>
                        <li><a href="#about" onClick={(e) => { e.preventDefault(); scrollToSection('about'); }}>About</a></li>
                        <li><a href="#features" onClick={(e) => { e.preventDefault(); scrollToSection('features'); }}>Features</a></li>
                        <li className="homepage-dropdown">
                            <a href="#lawfirms" onClick={(e) => { e.preventDefault(); scrollToSection('lawfirms'); }}>Law Firms</a>
                            <div className="homepage-dropdown-menu">
                                <ul>
                                    <li><a href="#">Criminal Law Firms</a></li>
                                    <li><a href="#">Civil Law Firms</a></li>
                                    <li><a href="#">Family Law Firms</a></li>
                                    <li><a href="#">Corporate Law Firms</a></li>
                                    <li><a href="#">Miscellaneous Legal Firms</a></li>
                                </ul>
                            </div>
                        </li>
                        <li><a href="#contact" onClick={(e) => { e.preventDefault(); scrollToSection('contact'); }}>Contact</a></li>
                    </ul>
                    <button className="homepage-login-btn" onClick={handleLogin}>Login</button>
                </nav>
            </header>

            {/* Hero Section */}
            <section id="home" className="homepage-hero">
                <h1>Advocare: Your Smart Legal Case Management System</h1>
                <p>Powered by modern technology, where your case automatically connects with qualified law firms. Our platform, based on trust, faith, and truth, simplifies justice for firms and clients alike.</p>
                <button className="homepage-cta-btn" onClick={() => scrollToSection('about')}>Get Started Now</button>
            </section>

            {/* About Section */}
            <section id="about" className="homepage-section homepage-about">
                <h2>What Our Law Firm Management System Does</h2>
                <div className="homepage-about-grid">
                    <div className="homepage-about-card">
                        <img src="https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=300&h=300&fit=crop" alt="Innovation" />
                        <h3>Innovate Firm Operations</h3>
                        <p>Advocare revolutionizes law firm workflows with AI-driven tools that streamline case handling, client intake, and resource allocation for maximum efficiency.</p>
                    </div>
                    <div className="homepage-about-card">
                        <img src="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=300&h=300&fit=crop" alt="Collaboration" />
                        <h3>Secure Firm Collaboration</h3>
                        <p>Enable seamless collaboration across your law firm with encrypted document sharing, real-time updates, and integrated communication channels tailored for legal teams.</p>
                    </div>
                    <div className="homepage-about-card">
                        <img src="https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=300&h=300&fit=crop" alt="AI Insights" />
                        <h3>AI-Powered Firm Insights</h3>
                        <p>Leverage predictive analytics to forecast case outcomes, optimize billing, and gain actionable insights that drive your law firm's growth and success.</p>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="homepage-section homepage-features">
                <h2>Key Features</h2>
                
                <div className="homepage-feature-hero">
                    <div className="homepage-feature-hero-text">
                        <h3>Intelligent Case Management</h3>
                        <p>Create, manage, track, organize, and assign cases with the highest level of access rights and data security. Convenient access and efficient firm management from anywhere, at any time.</p>
                        <button className="homepage-cta-btn" onClick={() => scrollToSection('how-it-works')}>Learn More</button>
                    </div>
                    <div className="homepage-feature-hero-image">
                        <img src="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&h=500&fit=crop" alt="Intelligent Case Management" />
                    </div>
                </div>

                <div className="homepage-slider-container" 
                     onMouseEnter={pauseAutoSlide} 
                     onMouseLeave={resumeAutoSlide}>
                    <div className="homepage-slider" style={{ transform: `translateX(-${currentSlide * 100}%)` }}>
                        {featureSlides.map((slide, idx) => (
                            <div key={idx} className="homepage-slide">
                                {slide.map((feature, fIdx) => (
                                    <div key={fIdx} className="homepage-feature-card">
                                        <img src={feature.icon} alt={feature.title} />
                                        <h3>{feature.title}</h3>
                                        <p>{feature.desc}</p>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                    <div className="homepage-slider-dots">
                        {[0, 1, 2].map(idx => (
                            <div 
                                key={idx} 
                                className={`homepage-slider-dot ${currentSlide === idx ? 'active' : ''}`}
                                onClick={() => goToSlide(idx)}
                            />
                        ))}
                    </div>
                </div>
            </section>

            {/* Law Firms Section */}
            <section id="lawfirms" className="homepage-section homepage-lawfirms">
                <h2>Our Partner Law Firms</h2>
                <p>Browse our verified law firms, complete with images, descriptions, and details on key lawyers and advocates.</p>
                <div className="homepage-lawfirm-grid">
                    {lawFirms.map(firm => (
                        <div key={firm.id} className="homepage-lawfirm-card">
                            <img className="homepage-lawfirm-image" src={firm.image} alt={firm.name} />
                            <h3>{firm.name}</h3>
                            <p>{firm.description}</p>
                            <ul className="homepage-lawyers-list">
                                {firm.lawyers.map((lawyer, idx) => (
                                    <li key={idx}>
                                        <strong>{lawyer.name}</strong>
                                        <span>{lawyer.desc}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            </section>

            {/* How It Works Section */}
            <section id="how-it-works" className="homepage-section homepage-how-it-works">
                <h2>How It Works</h2>
                <div className="homepage-steps">
                    <div className="homepage-step">
                        <div className="homepage-step-number">1</div>
                        <img src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=200&h=200&fit=crop" alt="Register" />
                        <h3>Register Your Case</h3>
                        <p>Upload your case details and documents through our secure portal. Provide necessary information for accurate matching.</p>
                    </div>
                    <div className="homepage-step">
                        <div className="homepage-step-number">2</div>
                        <img src="https://images.unsplash.com/photo-1552664730-d307ca884978?w=200&h=200&fit=crop" alt="Matching" />
                        <h3>AI Matching</h3>
                        <p>Our AI system matches your case with qualified law firms based on expertise, location, and success rates.</p>
                    </div>
                    <div className="homepage-step">
                        <div className="homepage-step-number">3</div>
                        <img src="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=200&h=200&fit=crop" alt="Choose" />
                        <h3>Choose and Start</h3>
                        <p>Select the best law firm from recommendations and begin your case management with secure communication.</p>
                    </div>
                    <div className="homepage-step">
                        <div className="homepage-step-number">4</div>
                        <img src="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=200&h=200&fit=crop" alt="Track" />
                        <h3>Track Progress</h3>
                        <p>Monitor case progress in real-time, receive updates, and access documents through your personal dashboard.</p>
                    </div>
                </div>
            </section>

            {/* Contact Section */}
            <section id="contact" className="homepage-section homepage-contact">
                <h2>Get in Touch</h2>
                <form className="homepage-contact-form" onSubmit={handleContactSubmit}>
                    {formMessage && <div className="contact-message" style={{ padding: '10px', marginBottom: '20px', borderRadius: '6px', backgroundColor: formMessage.includes('Thank') ? '#d4edda' : '#f8d7da', color: formMessage.includes('Thank') ? '#155724' : '#721c24' }}>{formMessage}</div>}
                    <div className="homepage-form-group">
                        <label>Full Name <span style={{ color: '#FFDC00' }}>*</span></label>
                        <input type="text" value={contactForm.fullName} onChange={(e) => setContactForm({...contactForm, fullName: e.target.value})} required />
                    </div>
                    <div className="homepage-form-group">
                        <label>Email Address <span style={{ color: '#FFDC00' }}>*</span></label>
                        <input type="email" value={contactForm.email} onChange={(e) => setContactForm({...contactForm, email: e.target.value})} required />
                    </div>
                    <div className="homepage-form-group">
                        <label>Phone Number <span style={{ color: '#666' }}>(optional but recommended)</span></label>
                        <input type="tel" value={contactForm.phone} onChange={(e) => setContactForm({...contactForm, phone: e.target.value})} />
                    </div>
                    <div className="homepage-form-group">
                        <label>Subject <span style={{ color: '#FFDC00' }}>*</span></label>
                        <select value={contactForm.subject} onChange={(e) => setContactForm({...contactForm, subject: e.target.value})} required>
                            <option value="">Select Subject</option>
                            <option value="general">General Inquiry</option>
                            <option value="case">Case Related Question</option>
                            <option value="technical">Technical Issue</option>
                            <option value="partnership">Partnership Inquiry</option>
                        </select>
                    </div>
                    <div className="homepage-form-group">
                        <label>Message <span style={{ color: '#FFDC00' }}>*</span></label>
                        <textarea rows="5" value={contactForm.message} onChange={(e) => setContactForm({...contactForm, message: e.target.value})} required placeholder="Please describe your query or message here..."></textarea>
                    </div>
                    <button type="submit" className="homepage-submit-btn" disabled={formSubmitting}>
                        {formSubmitting ? 'Sending...' : 'Submit Message'}
                    </button>
                </form>
            </section>

            {/* Footer */}
            <footer className="homepage-footer">
                <div className="homepage-footer-content">
                    <div className="homepage-footer-section">
                        <h4>Advocare</h4>
                        <p>Smart Legal Case Management System. Empowering law firms with AI-driven tools for efficient case handling, secure collaboration, and insightful analytics.</p>
                        <div className="homepage-social-icons">
                            <a href="#"><i className="fab fa-facebook-f"></i></a>
                            <a href="#"><i className="fab fa-twitter"></i></a>
                            <a href="#"><i className="fab fa-linkedin-in"></i></a>
                        </div>
                    </div>
                    <div className="homepage-footer-section">
                        <h4>Quick Links</h4>
                        <ul>
                            <li><a href="#home" onClick={(e) => { e.preventDefault(); scrollToSection('home'); }}>Home</a></li>
                            <li><a href="#about" onClick={(e) => { e.preventDefault(); scrollToSection('about'); }}>About</a></li>
                            <li><a href="#features" onClick={(e) => { e.preventDefault(); scrollToSection('features'); }}>Features</a></li>
                            <li><a href="#lawfirms" onClick={(e) => { e.preventDefault(); scrollToSection('lawfirms'); }}>Law Firms</a></li>
                            <li><a href="#how-it-works" onClick={(e) => { e.preventDefault(); scrollToSection('how-it-works'); }}>How It Works</a></li>
                            <li><a href="#contact" onClick={(e) => { e.preventDefault(); scrollToSection('contact'); }}>Contact Us</a></li>
                        </ul>
                    </div>
                    <div className="homepage-footer-section">
                        <h4>Contact Us</h4>
                        <ul>
                            <li>Email: info@advocare.com</li>
                            <li>Phone: +91-9876543210</li>
                            <li>Address: 123 Legal Street, Justice City, India 400001</li>
                            <li>Support: Mon-Fri, 9AM-6PM IST</li>
                        </ul>
                    </div>
                    <div className="homepage-footer-section">
                        <h4>Legal</h4>
                        <ul>
                            <li><a href="#">Privacy Policy</a></li>
                            <li><a href="#">Terms of Service</a></li>
                            <li><a href="#">Cookie Policy</a></li>
                            <li><a href="#">GDPR Compliance</a></li>
                        </ul>
                    </div>
                </div>
                <div className="homepage-footer-bottom">
                    <p>&copy; 2026 Advocare. All rights reserved. | Smart Legal Case Management System</p>
                </div>
            </footer>

            {/* AI Modal */}
            {modalOpen && (
                <div className="homepage-modal" onClick={() => setModalOpen(false)}>
                    <div className="homepage-modal-content" onClick={(e) => e.stopPropagation()}>
                        <span className="homepage-modal-close" onClick={() => setModalOpen(false)}>&times;</span>
                        <h3>Get AI-Generated Law Firm Recommendations</h3>
                        <p>Describe your case briefly:</p>
                        <textarea 
                            className="homepage-ai-input" 
                            rows="3" 
                            placeholder="e.g., Criminal defense for theft case..."
                            value={aiCaseDesc}
                            onChange={(e) => setAiCaseDesc(e.target.value)}
                        />
                        <button className="homepage-generate-btn" onClick={handleAISuggestion}>Generate Suggestion</button>
                        {aiSuggestion && (
                            <div className="homepage-ai-suggestion" dangerouslySetInnerHTML={{ __html: aiSuggestion }} />
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default Homepage;





















// import React, { useState, useEffect, useRef } from 'react';
// import { useNavigate } from 'react-router-dom';


// function Homepage() {
//     const navigate = useNavigate();
//     const [scrolled, setScrolled] = useState(false);
//     const [currentSlide, setCurrentSlide] = useState(0);
//     const [modalOpen, setModalOpen] = useState(false);
//     const [aiCaseDesc, setAiCaseDesc] = useState('');
//     const [aiSuggestion, setAiSuggestion] = useState('');
//     const [searchQuery, setSearchQuery] = useState('');
//     const [contactForm, setContactForm] = useState({
//         fullName: '',
//         email: '',
//         phone: '',
//         subject: '',
//         message: ''
//     });
    
//     const sliderRef = useRef(null);
//     const slideInterval = useRef(null);
//     const totalSlides = 3;

//     // Law firms data
//     const lawFirms = [
//         {
//             id: 1,
//             name: "Hale & Associates - Global Criminal Defense",
//             image: "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
//             description: "Leading firm specializing in high-profile criminal cases, with a track record of defending clients in international courts. Focus on evidence analysis and plea bargaining.",
//             lawyers: [
//                 { name: "John Hale", desc: "Senior Advocate, 20+ years in criminal law, expert in fraud and white-collar crimes." },
//                 { name: "Sarah Mitchell", desc: "Junior Lawyer, specializes in juvenile justice and rehabilitation programs." }
//             ]
//         },
//         {
//             id: 2,
//             name: "Vasquez Litigation Partners - Civil Experts",
//             image: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
//             description: "Renowned for civil litigation, contract disputes, and property law. They provide comprehensive strategies for dispute resolution and mediation.",
//             lawyers: [
//                 { name: "Maria Vasquez", desc: "Lead Advocate, 15 years experience in civil suits, known for innovative settlement tactics." },
//                 { name: "David Chen", desc: "Associate Lawyer, focuses on intellectual property and commercial disputes." }
//             ]
//         },
//         {
//             id: 3,
//             name: "Reed Family Law Group - Authority in Matrimonial",
//             image: "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
//             description: "Experts in family law, including divorce, custody, and adoption. Committed to compassionate representation and child welfare.",
//             lawyers: [
//                 { name: "Emily Reed", desc: "Principal Advocate, 18 years in family matters, mediator certified by international bodies." },
//                 { name: "Robert Kline", desc: "Family Lawyer, specializes in domestic violence and asset division." }
//             ]
//         }
//     ];

//     // Feature slides data
//     const featureSlides = [
//         [
//             { title: "Case Matching", desc: "AI suggestions for multiple law firms based on your case. Advanced algorithms match your specific legal needs with the most qualified firms.", icon: "https://images.unsplash.com/photo-1560253021-9b875e2e1e92?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" },
//             { title: "Law Firm Onboarding", desc: "Law firms can easily register, create profiles, and find cases. Streamlined process with verification and approval systems.", icon: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" },
//             { title: "Document Management", desc: "Upload and share case files with secure cloud storage. Organized filing system with version control and access permissions.", icon: "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" }
//         ],
//         [
//             { title: "Select Desired Law Firms", desc: "Users can browse and select preferred law firms based on expertise, ratings, and location for personalized case matching.", icon: "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" },
//             { title: "Centralized Data Management", desc: "Law firms manage all their data in one secure dashboard, including cases, clients, and analytics across multiple practices.", icon: "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" },
//             { title: "AI Assistance System", desc: "Intelligent AI chatbots and predictive analytics provide real-time legal advice, case predictions, and workflow automation.", icon: "https://images.unsplash.com/photo-1541701494587-cb58502866ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" }
//         ],
//         [
//             { title: "Rights Management", desc: "Granular role-based permissions ensure data privacy with advanced encryption, audit trails, and multi-factor authentication.", icon: "https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" },
//             { title: "Advanced Analytics", desc: "Comprehensive reporting and analytics tools to track case progress, firm performance, and client satisfaction metrics.", icon: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" },
//             { title: "Mobile Access", desc: "Access your case management system on-the-go with our mobile-responsive design and dedicated mobile applications.", icon: "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" }
//         ]
//     ];

//     // Handle scroll effect
//     useEffect(() => {
//         const handleScroll = () => {
//             setScrolled(window.scrollY > 50);
            
//             // Reveal sections on scroll
//             const sections = document.querySelectorAll('.homepage-section, .homepage-feature-hero, .homepage-search-section, .homepage-lawfirms');
//             sections.forEach(section => {
//                 const rect = section.getBoundingClientRect();
//                 if (rect.top < window.innerHeight * 0.9 && rect.bottom > 0) {
//                     section.classList.add('visible');
//                 }
//             });
//         };
        
//         window.addEventListener('scroll', handleScroll);
//         handleScroll();
        
//         return () => window.removeEventListener('scroll', handleScroll);
//     }, []);

//     // Auto slide for feature slider
//     useEffect(() => {
//         startAutoSlide();
//         return () => {
//             if (slideInterval.current) clearInterval(slideInterval.current);
//         };
//     }, []);

//     const startAutoSlide = () => {
//         if (slideInterval.current) clearInterval(slideInterval.current);
//         slideInterval.current = setInterval(() => {
//             setCurrentSlide(prev => (prev + 1) % totalSlides);
//         }, 5000);
//     };

//     const pauseAutoSlide = () => {
//         if (slideInterval.current) clearInterval(slideInterval.current);
//     };

//     const resumeAutoSlide = () => {
//         startAutoSlide();
//     };

//     const goToSlide = (index) => {
//         setCurrentSlide(index);
//     };

//     // Handle smooth scroll
//     const scrollToSection = (sectionId) => {
//         const element = document.getElementById(sectionId);
//         if (element) {
//             element.scrollIntoView({ behavior: 'smooth' });
//         }
//     };

//     // Handle search
//     const handleSearch = () => {
//         if (searchQuery.trim()) {
//             const lawfirmsSection = document.getElementById('lawfirms');
//             if (lawfirmsSection) {
//                 lawfirmsSection.scrollIntoView({ behavior: 'smooth' });
//             }
//         }
//     };

//     // Handle AI suggestion
//     const handleAISuggestion = () => {
//         if (aiCaseDesc.trim()) {
//             let suggestion = "Based on your case description, we recommend approaching ";
//             const desc = aiCaseDesc.toLowerCase();
//             if (desc.includes('criminal') || desc.includes('theft') || desc.includes('assault')) {
//                 suggestion += "<strong>Hale & Associates</strong> - Experts in criminal defense with a 95% success rate. They specialize in evidence analysis and plea bargaining.";
//             } else if (desc.includes('family') || desc.includes('divorce') || desc.includes('custody')) {
//                 suggestion += "<strong>Reed Family Law Group</strong> - Specializing in matrimonial and family disputes. They offer compassionate representation and mediation services.";
//             } else if (desc.includes('civil') || desc.includes('contract') || desc.includes('property')) {
//                 suggestion += "<strong>Vasquez Litigation Partners</strong> - Leaders in civil litigation and contract disputes. Known for innovative settlement strategies.";
//             } else {
//                 suggestion += "one of our top partner firms for comprehensive legal support. Our AI will match you with the most suitable firm based on your specific needs.";
//             }
//             setAiSuggestion(suggestion);
//         }
//     };

//     // Handle contact form submit
//     const handleContactSubmit = (e) => {
//         e.preventDefault();
//         alert('Thank you for your message! We will get back to you soon.');
//         setContactForm({ fullName: '', email: '', phone: '', subject: '', message: '' });
//     };

//     // Handle login redirect
//     const handleLogin = () => {
//         navigate('/');
//     };

//     return (
//         <div className="homepage-container">
//             <header className={`homepage-header ${scrolled ? 'scrolled' : ''}`}>
//                 <nav className="homepage-nav">
//                     <div className="homepage-logo">Advocare</div>
//                     <ul className="homepage-nav-links">
//                         <li><a href="#home" onClick={(e) => { e.preventDefault(); scrollToSection('home'); }}>Home</a></li>
//                         <li><a href="#about" onClick={(e) => { e.preventDefault(); scrollToSection('about'); }}>About</a></li>
//                         <li><a href="#features" onClick={(e) => { e.preventDefault(); scrollToSection('features'); }}>Features</a></li>
//                         <li className="homepage-dropdown">
//                             <a href="#lawfirms" onClick={(e) => { e.preventDefault(); scrollToSection('lawfirms'); }}>Law Firms</a>
//                             <div className="homepage-dropdown-menu">
//                                 <ul>
//                                     <li><a href="#">Criminal Law Firms</a></li>
//                                     <li><a href="#">Civil Law Firms</a></li>
//                                     <li><a href="#">Family Law Firms</a></li>
//                                     <li><a href="#">Corporate Law Firms</a></li>
//                                     <li><a href="#">Miscellaneous Legal Firms</a></li>
//                                 </ul>
//                             </div>
//                         </li>
//                         <li><a href="#contact" onClick={(e) => { e.preventDefault(); scrollToSection('contact'); }}>Contact</a></li>
//                     </ul>
//                     <button className="homepage-login-btn" onClick={handleLogin}>Login</button>
//                 </nav>
//             </header>

//             {/* Hero Section */}
//             <section id="home" className="homepage-hero">
//                 <h1>Advocare: Your Smart Legal Case Management System</h1>
//                 <p>Powered by modern technology, where your case automatically connects with qualified law firms. Our platform, based on trust, faith, and truth, simplifies justice for firms and clients alike.</p>
//                 <button className="homepage-cta-btn" onClick={() => scrollToSection('about')}>Get Started Now</button>
//             </section>

//             {/* Search Section */}
//             <section className="homepage-search-section">
//                 <div className="homepage-search-container">
//                     <input 
//                         type="text" 
//                         className="homepage-search-input" 
//                         placeholder="Search for Law Firms, Advocates, or Lawyers..."
//                         value={searchQuery}
//                         onChange={(e) => setSearchQuery(e.target.value)}
//                         onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
//                     />
//                     <button className="homepage-search-btn" onClick={handleSearch}>Search</button>
//                     <button className="homepage-ai-btn" onClick={() => setModalOpen(true)}>AI Case Suggestions</button>
//                 </div>
//             </section>

//             {/* About Section */}
//             <section id="about" className="homepage-section homepage-about">
//                 <h2>What Our Law Firm Management System Does</h2>
//                 <div className="homepage-about-grid">
//                     <div className="homepage-about-card">
//                         <img src="https://images.unsplash.com/photo-1559757148-5c350d0d3c56?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" alt="Innovation" />
//                         <h3>Innovate Firm Operations</h3>
//                         <p>Advocare revolutionizes law firm workflows with AI-driven tools that streamline case handling, client intake, and resource allocation for maximum efficiency.</p>
//                     </div>
//                     <div className="homepage-about-card">
//                         <img src="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" alt="Collaboration" />
//                         <h3>Secure Firm Collaboration</h3>
//                         <p>Enable seamless collaboration across your law firm with encrypted document sharing, real-time updates, and integrated communication channels tailored for legal teams.</p>
//                     </div>
//                     <div className="homepage-about-card">
//                         <img src="https://images.unsplash.com/photo-1541701494587-cb58502866ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" alt="AI Insights" />
//                         <h3>AI-Powered Firm Insights</h3>
//                         <p>Leverage predictive analytics to forecast case outcomes, optimize billing, and gain actionable insights that drive your law firm's growth and success.</p>
//                     </div>
//                 </div>
//             </section>

//             {/* Features Section */}
//             <section id="features" className="homepage-section homepage-features">
//                 <h2>Key Features</h2>
                
//                 <div className="homepage-feature-hero">
//                     <div className="homepage-feature-hero-text">
//                         <h3>Intelligent Case Management</h3>
//                         <p>Create, manage, track, organize, and assign cases with the highest level of access rights and data security. Convenient access and efficient firm management from anywhere, at any time.</p>
//                         <button className="homepage-cta-btn" onClick={() => scrollToSection('how-it-works')}>Learn More</button>
//                     </div>
//                     <div className="homepage-feature-hero-image">
//                         <img src="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" alt="Intelligent Case Management" />
//                     </div>
//                 </div>

//                 <div className="homepage-slider-container" 
//                      onMouseEnter={pauseAutoSlide} 
//                      onMouseLeave={resumeAutoSlide}>
//                     <div className="homepage-slider" style={{ transform: `translateX(-${currentSlide * 100}%)` }}>
//                         {featureSlides.map((slide, idx) => (
//                             <div key={idx} className="homepage-slide">
//                                 {slide.map((feature, fIdx) => (
//                                     <div key={fIdx} className="homepage-feature-card">
//                                         <img src={feature.icon} alt={feature.title} />
//                                         <h3>{feature.title}</h3>
//                                         <p>{feature.desc}</p>
//                                     </div>
//                                 ))}
//                             </div>
//                         ))}
//                     </div>
//                     <div className="homepage-slider-dots">
//                         {[0, 1, 2].map(idx => (
//                             <div 
//                                 key={idx} 
//                                 className={`homepage-slider-dot ${currentSlide === idx ? 'active' : ''}`}
//                                 onClick={() => goToSlide(idx)}
//                             />
//                         ))}
//                     </div>
//                 </div>
//             </section>

//             {/* Law Firms Section */}
//             <section id="lawfirms" className="homepage-section homepage-lawfirms">
//                 <h2>Our Partner Law Firms</h2>
//                 <p>Browse our verified law firms, complete with images, descriptions, and details on key lawyers and advocates.</p>
//                 <div className="homepage-lawfirm-grid">
//                     {lawFirms.map(firm => (
//                         <div key={firm.id} className="homepage-lawfirm-card">
//                             <img className="homepage-lawfirm-image" src={firm.image} alt={firm.name} />
//                             <h3>{firm.name}</h3>
//                             <p>{firm.description}</p>
//                             <ul className="homepage-lawyers-list">
//                                 {firm.lawyers.map((lawyer, idx) => (
//                                     <li key={idx}>
//                                         <strong>{lawyer.name}</strong>
//                                         <span>{lawyer.desc}</span>
//                                     </li>
//                                 ))}
//                             </ul>
//                         </div>
//                     ))}
//                 </div>
//             </section>

//             {/* How It Works Section */}
//             <section id="how-it-works" className="homepage-section homepage-how-it-works">
//                 <h2>How It Works</h2>
//                 <div className="homepage-steps">
//                     <div className="homepage-step">
//                         <div className="homepage-step-number">1</div>
//                         <img src="https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d8?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" alt="Register" />
//                         <h3>Register Your Case</h3>
//                         <p>Upload your case details and documents through our secure portal. Provide necessary information for accurate matching.</p>
//                     </div>
//                     <div className="homepage-step">
//                         <div className="homepage-step-number">2</div>
//                         <img src="https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" alt="Matching" />
//                         <h3>AI Matching</h3>
//                         <p>Our AI system matches your case with qualified law firms based on expertise, location, and success rates.</p>
//                     </div>
//                     <div className="homepage-step">
//                         <div className="homepage-step-number">3</div>
//                         <img src="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" alt="Choose" />
//                         <h3>Choose and Start</h3>
//                         <p>Select the best law firm from recommendations and begin your case management with secure communication.</p>
//                     </div>
//                     <div className="homepage-step">
//                         <div className="homepage-step-number">4</div>
//                         <img src="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" alt="Track" />
//                         <h3>Track Progress</h3>
//                         <p>Monitor case progress in real-time, receive updates, and access documents through your personal dashboard.</p>
//                     </div>
//                 </div>
//             </section>

//             {/* Contact Section */}
//             <section id="contact" className="homepage-section homepage-contact">
//                 <h2>Get in Touch</h2>
//                 <form className="homepage-contact-form" onSubmit={handleContactSubmit}>
//                     <div className="homepage-form-group">
//                         <label>Full Name <span style={{ color: '#FFDC00' }}>*</span></label>
//                         <input type="text" value={contactForm.fullName} onChange={(e) => setContactForm({...contactForm, fullName: e.target.value})} required />
//                     </div>
//                     <div className="homepage-form-group">
//                         <label>Email Address <span style={{ color: '#FFDC00' }}>*</span></label>
//                         <input type="email" value={contactForm.email} onChange={(e) => setContactForm({...contactForm, email: e.target.value})} required />
//                     </div>
//                     <div className="homepage-form-group">
//                         <label>Phone Number <span style={{ color: '#666' }}>(optional but recommended)</span></label>
//                         <input type="tel" value={contactForm.phone} onChange={(e) => setContactForm({...contactForm, phone: e.target.value})} />
//                     </div>
//                     <div className="homepage-form-group">
//                         <label>Subject <span style={{ color: '#FFDC00' }}>*</span></label>
//                         <select value={contactForm.subject} onChange={(e) => setContactForm({...contactForm, subject: e.target.value})} required>
//                             <option value="">Select Subject</option>
//                             <option value="general">General Inquiry</option>
//                             <option value="case">Case Related Question</option>
//                             <option value="technical">Technical Issue</option>
//                             <option value="partnership">Partnership Inquiry</option>
//                         </select>
//                     </div>
//                     <div className="homepage-form-group">
//                         <label>Message <span style={{ color: '#FFDC00' }}>*</span></label>
//                         <textarea rows="5" value={contactForm.message} onChange={(e) => setContactForm({...contactForm, message: e.target.value})} required placeholder="Please describe your query or message here..."></textarea>
//                     </div>
//                     <button type="submit" className="homepage-submit-btn">Submit Message</button>
//                 </form>
//             </section>

//             {/* Footer */}
//             <footer className="homepage-footer">
//                 <div className="homepage-footer-content">
//                     <div className="homepage-footer-section">
//                         <h4>Advocare</h4>
//                         <p>Smart Legal Case Management System. Empowering law firms with AI-driven tools for efficient case handling, secure collaboration, and insightful analytics.</p>
//                         <div className="homepage-social-icons">
//                             <a href="#"><i className="fab fa-facebook-f"></i></a>
//                             <a href="#"><i className="fab fa-twitter"></i></a>
//                             <a href="#"><i className="fab fa-linkedin-in"></i></a>
//                         </div>
//                     </div>
//                     <div className="homepage-footer-section">
//                         <h4>Quick Links</h4>
//                         <ul>
//                             <li><a href="#home" onClick={(e) => { e.preventDefault(); scrollToSection('home'); }}>Home</a></li>
//                             <li><a href="#about" onClick={(e) => { e.preventDefault(); scrollToSection('about'); }}>About</a></li>
//                             <li><a href="#features" onClick={(e) => { e.preventDefault(); scrollToSection('features'); }}>Features</a></li>
//                             <li><a href="#lawfirms" onClick={(e) => { e.preventDefault(); scrollToSection('lawfirms'); }}>Law Firms</a></li>
//                             <li><a href="#how-it-works" onClick={(e) => { e.preventDefault(); scrollToSection('how-it-works'); }}>How It Works</a></li>
//                             <li><a href="#contact" onClick={(e) => { e.preventDefault(); scrollToSection('contact'); }}>Contact Us</a></li>
//                         </ul>
//                     </div>
//                     <div className="homepage-footer-section">
//                         <h4>Contact Us</h4>
//                         <ul>
//                             <li>Email: info@advocare.com</li>
//                             <li>Phone: +91-9876543210</li>
//                             <li>Address: 123 Legal Street, Justice City, India 400001</li>
//                             <li>Support: Mon-Fri, 9AM-6PM IST</li>
//                         </ul>
//                     </div>
//                     <div className="homepage-footer-section">
//                         <h4>Legal</h4>
//                         <ul>
//                             <li><a href="#">Privacy Policy</a></li>
//                             <li><a href="#">Terms of Service</a></li>
//                             <li><a href="#">Cookie Policy</a></li>
//                             <li><a href="#">GDPR Compliance</a></li>
//                         </ul>
//                     </div>
//                 </div>
//                 <div className="homepage-footer-bottom">
//                     <p>&copy; 2026 Advocare. All rights reserved. | Smart Legal Case Management System</p>
//                 </div>
//             </footer>

//             {/* AI Modal */}
//             {modalOpen && (
//                 <div className="homepage-modal" onClick={() => setModalOpen(false)}>
//                     <div className="homepage-modal-content" onClick={(e) => e.stopPropagation()}>
//                         <span className="homepage-modal-close" onClick={() => setModalOpen(false)}>&times;</span>
//                         <h3>Get AI-Generated Law Firm Recommendations</h3>
//                         <p>Describe your case briefly:</p>
//                         <textarea 
//                             className="homepage-ai-input" 
//                             rows="3" 
//                             placeholder="e.g., Criminal defense for theft case..."
//                             value={aiCaseDesc}
//                             onChange={(e) => setAiCaseDesc(e.target.value)}
//                         />
//                         <button className="homepage-generate-btn" onClick={handleAISuggestion}>Generate Suggestion</button>
//                         {aiSuggestion && (
//                             <div className="homepage-ai-suggestion" dangerouslySetInnerHTML={{ __html: aiSuggestion }} />
//                         )}
//                     </div>
//                 </div>
//             )}
//         </div>
//     );
// }

// export default Homepage;