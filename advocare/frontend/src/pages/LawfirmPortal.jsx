import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';
import Chart from 'chart.js/auto';

function LawfirmPortal() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [activePage, setActivePage] = useState('dashboard');
    const [firmData, setFirmData] = useState(null);
    const [editingProfile, setEditingProfile] = useState(false);
    const [profileForm, setProfileForm] = useState({});
    const [stats, setStats] = useState({ totalCases: 0, activeCases: 0, pendingRequests: 0, successRate: 0 });
    const [monthlyStats, setMonthlyStats] = useState({ new_cases: Array(12).fill(0), closed_cases: Array(12).fill(0) });
    
    // Case Requests with tabs
    const [caseRequests, setCaseRequests] = useState([]);
    const [acceptedCases, setAcceptedCases] = useState([]);
    const [caseRequestTab, setCaseRequestTab] = useState('pending');
    
    const [assignedCases, setAssignedCases] = useState([]);
    const [teamMembers, setTeamMembers] = useState([]);
    const [courtUpdates, setCourtUpdates] = useState([]);

    // Chat states
    const [conversations, setConversations] = useState([]);
    const [selectedChat, setSelectedChat] = useState(null);
    const [chatMessages, setChatMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');

    const [showAddTeamMemberForm, setShowAddTeamMemberForm] = useState(false);
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [newTeamMember, setNewTeamMember] = useState({
        name: '',
        email: '',
        role: 'associate',
        experience_years: ''
    });

    const chartRef = useRef(null);
    const chartInstanceRef = useRef(null);
    const chatPollInterval = useRef(null);
    const chatEndRef = useRef(null);

    const roleOptions = [
        { value: 'associate', label: 'Associate' },
        { value: 'partner', label: 'Partner' },
        { value: 'senior_advocate', label: 'Senior Advocate' },
        { value: 'legal_assistant', label: 'Legal Assistant' },
        { value: 'paralegal', label: 'Paralegal' },
    ];

    // ========== CHAT ==========
    const loadConversations = useCallback(async () => {
        try {
            const res = await API.get('chat/conversations/');
            setConversations(res.data);
        } catch (err) { console.error('Failed to load conversations:', err); }
    }, []);

    const loadChatMessages = async (caseId, otherPartyId) => {
        try {
            const res = await API.get(`chat/${caseId}/${otherPartyId}/`);
            setChatMessages(res.data);
        } catch (err) { console.error('Failed to load messages:', err); }
    };

    const sendMessage = async () => {
        if (!newMessage.trim() || !selectedChat) return;
        const msg = newMessage;
        setNewMessage('');
        try {
            await API.post('chat/send/', { case_id: selectedChat.caseId, receiver_id: selectedChat.otherPartyId, content: msg });
            await loadChatMessages(selectedChat.caseId, selectedChat.otherPartyId);
            await loadConversations();
        } catch (err) {
            console.error('Failed to send message:', err);
            setNewMessage(msg);
        }
    };

    const forwardToClient = async (update) => {
        if (!update.case_id || !update.client_id) {
            alert('Cannot forward: missing case or client information');
            return;
        }
        try {
            await API.post('chat/send/', {
                case_id: update.case_id,
                receiver_id: update.client_id,
                content: `📢 COURT UPDATE: ${update.message || update.description}\n\nDate: ${formatDate(update.date)}\nCase: ${update.case_title}\n\nPlease review and let us know if you have any questions.`
            });
            alert('Update forwarded to client via chat');
        } catch (err) {
            console.error('Forward failed:', err);
            alert('Failed to forward update');
        }
    };

    // ========== CASE REQUESTS ==========
    const handleAcceptRequest = async (caseId) => {
        try {
            await API.post(`cases/${caseId}/accept/`);
            alert('Case request accepted successfully!');
            await loadPendingRequests();
            await loadAssignedCases();
            await loadAcceptedCases();
            await loadConversations();
            await loadStatsAndMonthly(); // refresh stats & chart
        } catch (error) { 
            console.error('Accept error:', error);
            alert('Failed to accept request'); 
        }
    };

    const handleRejectRequest = async (caseId) => {
        if (!window.confirm('Are you sure you want to reject this case?')) return;
        try {
            await API.post(`cases/${caseId}/reject/`);
            alert('Case request rejected');
            await loadPendingRequests();
            await loadAssignedCases();
            await loadAcceptedCases();
            await loadStatsAndMonthly();
        } catch (error) { 
            console.error('Reject error:', error);
            alert('Failed to reject request'); 
        }
    };

    // NEW: Close Case (mark as closed)
    const handleCloseCase = async (caseId) => {
        if (!window.confirm('Mark this case as closed? This action cannot be undone.')) return;
        try {
            await API.post(`cases/${caseId}/close/`);
            alert('Case marked as closed');
            await loadAssignedCases();
            await loadStatsAndMonthly();
            // Also refresh pending/accepted if needed
            await loadPendingRequests();
            await loadAcceptedCases();
        } catch (error) {
            console.error('Close case error:', error);
            alert('Failed to close case');
        }
    };

    const loadPendingRequests = async () => {
        try {
            const res = await API.get('cases/pending-requests/');
            setCaseRequests(res.data || []);
        } catch (err) { 
            console.error('Pending requests error:', err);
            setCaseRequests([]);
        }
    };

    const loadAcceptedCases = async () => {
        try {
            const res = await API.get('cases/accepted-cases/');
            setAcceptedCases(res.data || []);
        } catch (err) {
            console.error('Accepted cases error:', err);
            if (assignedCases.length) {
                setAcceptedCases(assignedCases.filter(c => c.status === 'in_progress'));
            } else {
                setAcceptedCases([]);
            }
        }
    };

    const loadAssignedCases = async () => {
        try {
            const res = await API.get('cases/assigned-cases/');
            setAssignedCases(res.data || []);
        } catch (err) { 
            console.error('Assigned cases error:', err);
            setAssignedCases([]);
        }
    };

    // ========== TEAM MEMBERS MANAGEMENT ==========
    const loadTeamMembers = async () => {
        try {
            const res = await API.get('cases/lawfirm-lawyers/');
            setTeamMembers(res.data || []);
        } catch (err) {
            console.error('Failed to load team members:', err);
            setTeamMembers([]);
        }
    };

    const handleAddTeamMember = async (e) => {
        e.preventDefault();
        if (!newTeamMember.name || !newTeamMember.email || !newTeamMember.role || !newTeamMember.experience_years) {
            alert('Please fill all required fields');
            return;
        }
        try {
            await API.post('cases/add-lawyer/', {
                name: newTeamMember.name,
                email: newTeamMember.email,
                role: newTeamMember.role,
                experience_years: parseInt(newTeamMember.experience_years, 10)
            });
            await loadTeamMembers();
            setShowAddTeamMemberForm(false);
            setNewTeamMember({ name: '', email: '', role: 'associate', experience_years: '' });
            alert('Team member added successfully!');
        } catch (error) {
            console.error('Add team member error:', error);
            alert('Failed to add team member');
        }
    };

    // NEW: Delete Team Member
    const handleDeleteTeamMember = async (memberId) => {
        if (!window.confirm('Are you sure you want to remove this team member?')) return;
        try {
            await API.delete(`cases/lawfirm-lawyers/${memberId}/`);
            alert('Team member removed successfully');
            await loadTeamMembers();
        } catch (error) {
            console.error('Delete team member error:', error);
            alert('Failed to remove team member');
        }
    };

    // ========== FIRM PROFILE ==========
    const handleProfileSave = async (e) => {
        e.preventDefault();
        const updatableFields = {
            firm_name: profileForm.firm_name,
            registration_no: profileForm.registration_no,
            phone: profileForm.phone,
            website: profileForm.website,
            address: profileForm.address,
            city: profileForm.city,
            state: profileForm.state,
            primary_lawyer_name: profileForm.primary_lawyer_name,
            primary_lawyer_bar_council_id: profileForm.primary_lawyer_bar_council_id,
            primary_lawyer_years_experience: profileForm.primary_lawyer_years_experience,
            primary_lawyer_specialization: profileForm.primary_lawyer_specialization,
            experience: profileForm.experience,
            specialization: profileForm.specialization,
            bio: profileForm.bio,
        };
        Object.keys(updatableFields).forEach(key => {
            if (updatableFields[key] === undefined || updatableFields[key] === null) {
                delete updatableFields[key];
            }
        });
        try {
            await API.put('profiles/lawfirm-dashboard/', updatableFields);
            setFirmData({ ...firmData, ...updatableFields });
            setEditingProfile(false);
            alert('Profile updated successfully!');
        } catch (error) {
            console.error('Profile update error:', error);
            alert('Failed to update profile');
        }
    };

    // ========== STATS & MONTHLY DATA ==========
    const loadStatsAndMonthly = async () => {
        try {
            const statsRes = await API.get('cases/lawfirm-stats/');
            setStats(statsRes.data);
        } catch (e) {
            console.error('Stats error:', e);
            setStats({ totalCases: 0, activeCases: 0, pendingRequests: 0, successRate: 0 });
        }
        try {
            const monthlyRes = await API.get('cases/monthly-stats/');
            setMonthlyStats(monthlyRes.data);
            return monthlyRes.data;
        } catch (e) {
            console.error('Monthly stats error, using mock:', e);
            const mock = { new_cases: [12, 19, 8, 15, 12, 17, 10, 14, 16, 12, 10, 15], closed_cases: [8, 12, 6, 10, 9, 13, 7, 11, 12, 9, 8, 11] };
            setMonthlyStats(mock);
            return mock;
        }
    };

    // ========== DYNAMIC CHART ==========
    const initChart = useCallback((newData, closedData) => {
        if (!chartRef.current) return;
        if (chartInstanceRef.current) {
            chartInstanceRef.current.destroy();
            chartInstanceRef.current = null;
        }
        const ctx = chartRef.current.getContext('2d');
        chartInstanceRef.current = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'New Cases',
                        data: newData,
                        backgroundColor: 'rgba(26, 60, 139, 0.75)',
                        borderColor: 'rgba(26, 60, 139, 1)',
                        borderWidth: 2,
                        borderRadius: 6,
                    },
                    {
                        label: 'Closed Cases',
                        data: closedData,
                        backgroundColor: 'rgba(212, 175, 55, 0.75)',
                        borderColor: 'rgba(212, 175, 55, 1)',
                        borderWidth: 2,
                        borderRadius: 6,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }, []);

    // ========== UTILITIES ==========
    const handleLogout = () => { localStorage.clear(); navigate('/'); };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
        } catch { return 'Invalid date'; }
    };

    const getStatusBadgeClass = (status) => {
        const map = { pending: 'status-pending', in_progress: 'status-in-court', assigned: 'status-assigned', resolved: 'status-closed', closed: 'status-closed' };
        return map[status] || 'status-pending';
    };

    const getStatusText = (status) => {
        const map = { pending: 'Pending', assigned: 'Assigned', in_progress: 'In Progress', resolved: 'Resolved', closed: 'Closed' };
        return map[status] || status;
    };

    const getRoleBadgeColor = (role) => {
        const map = { partner: '#1a3c8b', senior_advocate: '#7c3aed', associate: '#0891b2', legal_assistant: '#059669', paralegal: '#d97706' };
        return map[role] || '#6b7280';
    };

    // ========== DATA LOADING ==========
    useEffect(() => {
        const loadDashboard = async () => {
            try {
                const token = localStorage.getItem('access_token');
                if (!token) { navigate('/'); return; }
                
                // Load firm profile
                try {
                    const profileRes = await API.get('profiles/lawfirm-dashboard/');
                    if (profileRes.data.status === 'approved') {
                        setFirmData(profileRes.data);
                        const { user, created_at, updated_at, team_members, ...updatable } = profileRes.data;
                        setProfileForm(updatable);
                    } else if (profileRes.data.status === 'pending') {
                        navigate('/lawfirm-pending-onboarding'); return;
                    } else { navigate('/lawfirm-onboarding'); return; }
                } catch (err) { console.error('Profile error:', err); }
                
                await loadStatsAndMonthly();
                await loadPendingRequests();
                await loadAssignedCases();
                await loadAcceptedCases();
                await loadConversations();
                await loadTeamMembers();
                
                try { 
                    const updatesRes = await API.get('cases/court-updates/'); 
                    setCourtUpdates(updatesRes.data || []); 
                } catch (e) { console.error('Court updates error:', e); }
            } catch (error) {
                console.error('Dashboard load error:', error);
                if (error.response?.status === 401) { localStorage.clear(); navigate('/'); }
            } finally { setLoading(false); }
        };
        loadDashboard();
    }, [navigate]);

    // Chart initialization when monthlyStats changes or dashboard becomes active
    useEffect(() => {
        if (activePage === 'dashboard' && chartRef.current && monthlyStats.new_cases.length) {
            if (chartInstanceRef.current) chartInstanceRef.current.destroy();
            initChart(monthlyStats.new_cases, monthlyStats.closed_cases);
        }
        return () => {
            if (activePage !== 'dashboard' && chartInstanceRef.current) {
                chartInstanceRef.current.destroy();
                chartInstanceRef.current = null;
            }
        };
    }, [activePage, monthlyStats, initChart]);

    // Chat polling
    useEffect(() => {
        if (chatPollInterval.current) clearInterval(chatPollInterval.current);
        if (selectedChat && activePage === 'messages') {
            chatPollInterval.current = setInterval(() => loadChatMessages(selectedChat.caseId, selectedChat.otherPartyId), 3000);
        }
        return () => { if (chatPollInterval.current) clearInterval(chatPollInterval.current); };
    }, [selectedChat, activePage]);

    useEffect(() => {
        if (chatEndRef.current) chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }, [chatMessages]);

    if (loading) {
        return (
            <div className="lawfirm-loading-container">
                <div className="lawfirm-loading-card">
                    <div className="lawfirm-spinner"></div>
                    <h2>Loading Dashboard...</h2>
                </div>
            </div>
        );
    }

    const unreadCount = conversations.reduce((sum, c) => sum + (c.unread_count || 0), 0);
    const navItems = [
        { id: 'dashboard', icon: 'tachometer-alt', label: 'Dashboard' },
        { id: 'case-requests', icon: 'file-contract', label: 'Case Requests', badge: caseRequests.length },
        { id: 'assigned-cases', icon: 'briefcase', label: 'Assigned Cases' },
        { id: 'team-members', icon: 'users', label: 'Team Members' },
        { id: 'court-updates', icon: 'gavel', label: 'Court Updates' },
        { id: 'messages', icon: 'comments', label: 'Messages', badge: unreadCount },
        { id: 'profile', icon: 'building', label: 'Firm Profile' },
    ];

    return (
        <div className="lawfirm-portal-wrapper">
            {/* Sidebar */}
            <div className={`lawfirm-portal-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
                <div className="lawfirm-portal-logo">
                    <div className="lawfirm-portal-logo-icon"><i className="fas fa-balance-scale"></i></div>
                    {!sidebarCollapsed && <div className="lawfirm-portal-logo-text">Advocare</div>}
                </div>
                <div className="lawfirm-portal-nav">
                    {navItems.map(item => (
                        <div key={item.id}
                            className={`lawfirm-portal-nav-item ${activePage === item.id ? 'active' : ''}`}
                            onClick={() => {
                                setActivePage(item.id);
                                if (item.id === 'case-requests') {
                                    loadPendingRequests();
                                    loadAcceptedCases();
                                }
                                if (item.id === 'assigned-cases') loadAssignedCases();
                                if (item.id === 'team-members') loadTeamMembers();
                            }}>
                            <i className={`fas fa-${item.icon}`}></i>
                            {!sidebarCollapsed && <span>{item.label}</span>}
                            {item.badge > 0 && <span className="lawfirm-portal-badge">{item.badge}</span>}
                        </div>
                    ))}
                </div>
                {!sidebarCollapsed && (
                    <div className="lawfirm-portal-user">
                        <div className="lawfirm-portal-avatar">{firmData?.firm_name?.charAt(0) || 'F'}</div>
                        <div className="lawfirm-portal-user-info">
                            <h4>{firmData?.firm_name || 'Law Firm'}</h4>
                            <p>Law Firm Admin</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Main Content */}
            <div className="lawfirm-portal-main">
                <div className="lawfirm-portal-header">
                    <div className="lawfirm-portal-title">
                        <button className="lawfirm-portal-toggle" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
                            <i className="fas fa-bars"></i>
                        </button>
                        <span>{navItems.find(n => n.id === activePage)?.label || 'Dashboard'}</span>
                    </div>
                    <div className="lawfirm-portal-actions">
                        <div className="lawfirm-portal-search">
                            <i className="fas fa-search"></i>
                            <input type="text" placeholder="Search..." />
                        </div>
                        <div className="lawfirm-portal-notification">
                            <i className="fas fa-bell"></i>
                            <span className="lawfirm-portal-dot"></span>
                        </div>
                        <button className="lawfirm-portal-logout" onClick={handleLogout}>
                            <i className="fas fa-sign-out-alt"></i> Logout
                        </button>
                    </div>
                </div>

                {/* DASHBOARD with dynamic chart */}
                {activePage === 'dashboard' && (
                    <div className="lawfirm-portal-dashboard">
                        <div className="lawfirm-portal-kpi">
                            {[
                                { icon: 'folder-open', value: stats.totalCases, label: 'Total Cases', color: '#1a3c8b' },
                                { icon: 'gavel', value: stats.activeCases, label: 'Active Cases', color: '#0891b2' },
                                { icon: 'clock', value: stats.pendingRequests, label: 'Pending Requests', color: '#d97706' },
                                { icon: 'chart-line', value: `${stats.successRate || 0}%`, label: 'Success Rate', color: '#059669' },
                            ].map((kpi, i) => (
                                <div key={i} className="lawfirm-portal-kpi-card" style={{ borderTop: `4px solid ${kpi.color}` }}>
                                    <div className="lawfirm-portal-kpi-icon" style={{ background: kpi.color + '18', color: kpi.color }}>
                                        <i className={`fas fa-${kpi.icon}`}></i>
                                    </div>
                                    <div>
                                        <h3 style={{ color: kpi.color, fontSize: '2rem', fontWeight: 700, margin: 0 }}>{kpi.value}</h3>
                                        <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>{kpi.label}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="lawfirm-portal-stats">
                            <div className="lawfirm-portal-chart">
                                <div className="lawfirm-portal-section-title">
                                    <span>Case Statistics (Monthly)</span>
                                    <select><option>Last 12 Months</option><option>Last 6 Months</option><option>Last 3 Months</option></select>
                                </div>
                                <div style={{ height: '280px', position: 'relative' }}>
                                    <canvas ref={chartRef}></canvas>
                                </div>
                            </div>
                            <div className="lawfirm-portal-activity">
                                <div className="lawfirm-portal-section-title">
                                    <span>Recent Activity</span>
                                    <button onClick={() => setActivePage('assigned-cases')}>View All</button>
                                </div>
                                {assignedCases.slice(0, 4).map(c => (
                                    <div key={c.id} className="lawfirm-portal-activity-item">
                                        <div className="lawfirm-portal-activity-icon"><i className="fas fa-landmark"></i></div>
                                        <div>
                                            <h4>{c.title}</h4>
                                            <p>Client: {c.client_name}</p>
                                            <span className={`badge ${getStatusBadgeClass(c.status)}`}>{getStatusText(c.status)}</span>
                                            <small style={{ display: 'block', marginTop: 4 }}>{formatDate(c.updated_at)}</small>
                                        </div>
                                    </div>
                                ))}
                                {assignedCases.length === 0 && <p style={{ color: '#9ca3af', textAlign: 'center', padding: '20px' }}>No recent activity</p>}
                            </div>
                        </div>

                        <div className="lawfirm-portal-actions-grid">
                            <button className="lawfirm-portal-action-card" onClick={() => setActivePage('case-requests')}>
                                <i className="fas fa-file-contract"></i><span>View Case Requests</span>
                            </button>
                            <button className="lawfirm-portal-action-card" onClick={() => { setActivePage('team-members'); setShowAddTeamMemberForm(true); }}>
                                <i className="fas fa-user-plus"></i><span>Add Team Member</span>
                            </button>
                            <button className="lawfirm-portal-action-card" onClick={() => setActivePage('court-updates')}>
                                <i className="fas fa-gavel"></i><span>Court Updates</span>
                            </button>
                            <button className="lawfirm-portal-action-card" onClick={() => setActivePage('messages')}>
                                <i className="fas fa-comment-medical"></i><span>Messages</span>
                            </button>
                        </div>
                    </div>
                )}

                {/* CASE REQUESTS (same as before, no change) */}
                {activePage === 'case-requests' && (
                    <div>
                        <div className="lawfirm-portal-page-header">
                            <h2>Case Requests</h2>
                        </div>
                        <div style={{ display: 'flex', gap: 8, background: '#f3f4f6', padding: 4, borderRadius: 12, width: 'fit-content', marginBottom: 24 }}>
                            {[
                                { key: 'pending', label: 'Pending', count: caseRequests.length, dot: '#f59e0b', activeBadge: { bg: '#fef3c7', color: '#92400e' } },
                                { key: 'accepted', label: 'Accepted', count: acceptedCases.length, dot: '#10b981', activeBadge: { bg: '#d1fae5', color: '#065f46' } },
                                { key: 'denied', label: 'Denied', count: null, dot: '#ef4444', activeBadge: { bg: '#fee2e2', color: '#991b1b' } },
                            ].map(tab => {
                                const isActive = caseRequestTab === tab.key;
                                return (
                                    <button key={tab.key} onClick={() => setCaseRequestTab(tab.key)} style={{
                                        display: 'flex', alignItems: 'center', gap: 7, padding: '8px 18px', borderRadius: 9, border: 'none',
                                        cursor: 'pointer', fontSize: 13, fontWeight: 500, transition: 'all 0.18s',
                                        background: isActive ? '#ffffff' : 'transparent', color: isActive ? '#111827' : '#6b7280',
                                        boxShadow: isActive ? '0 1px 4px rgba(0,0,0,0.08)' : 'none',
                                    }}>
                                        <span style={{ width: 7, height: 7, borderRadius: '50%', background: tab.dot, flexShrink: 0 }} />
                                        {tab.label}
                                        {tab.count !== null && (
                                            <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 20, background: isActive ? tab.activeBadge.bg : '#e5e7eb', color: isActive ? tab.activeBadge.color : '#6b7280' }}>{tab.count}</span>
                                        )}
                                    </button>
                                );
                            })}
                        </div>
                        {caseRequestTab === 'pending' && (
                            <div className="lawfirm-portal-requests-grid">
                                {caseRequests.map(req => (
                                    <div key={req.id} className="lawfirm-portal-request-card">
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                                            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>{req.title}</h3>
                                            <span className="lawfirm-portal-case-type">{req.case_type}</span>
                                        </div>
                                        <p className="lawfirm-portal-case-desc">{req.description?.substring(0, 150)}...</p>
                                        <div className="lawfirm-portal-client">
                                            <div className="lawfirm-portal-client-avatar">{req.client_name?.charAt(0)}</div>
                                            <div>
                                                <h4 style={{ margin: 0 }}>{req.client_name}</h4>
                                                <p style={{ margin: 0, fontSize: '0.8rem', color: '#6b7280' }}>{req.client_email}</p>
                                                <small style={{ color: '#9ca3af' }}>Submitted: {formatDate(req.created_at)}</small>
                                            </div>
                                        </div>
                                        <div className="lawfirm-portal-request-actions">
                                            <button className="lawfirm-portal-btn-accept" onClick={() => handleAcceptRequest(req.id)}><i className="fas fa-check"></i> Accept</button>
                                            <button className="lawfirm-portal-btn-reject" onClick={() => handleRejectRequest(req.id)}><i className="fas fa-times"></i> Reject</button>
                                        </div>
                                    </div>
                                ))}
                                {caseRequests.length === 0 && <div className="lawfirm-portal-no-data"><i className="fas fa-check-circle fa-3x" style={{ color: '#10b981', marginBottom: 12 }}></i><p>No pending case requests</p></div>}
                            </div>
                        )}
                        {caseRequestTab === 'accepted' && (
                            <div className="lawfirm-portal-requests-grid">
                                {acceptedCases.map(c => (
                                    <div key={c.id} className="lawfirm-portal-request-card" style={{ borderLeftColor: '#10b981' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                                            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>{c.title}</h3>
                                            <span className="lawfirm-portal-case-type">{c.case_type}</span>
                                        </div>
                                        <p className="lawfirm-portal-case-desc">{c.description?.substring(0, 150)}...</p>
                                        <div className="lawfirm-portal-client">
                                            <div className="lawfirm-portal-client-avatar" style={{ background: '#d1fae5', color: '#065f46' }}>{c.client_name?.charAt(0)}</div>
                                            <div>
                                                <h4 style={{ margin: 0 }}>{c.client_name}</h4>
                                                <p style={{ margin: 0, fontSize: '0.8rem', color: '#6b7280' }}>{c.client_email}</p>
                                                <small style={{ color: '#9ca3af' }}>Accepted on: {formatDate(c.updated_at)}</small>
                                            </div>
                                        </div>
                                        <div className="lawfirm-portal-request-actions">
                                            <button className="lawfirm-portal-btn-view" onClick={() => setActivePage('assigned-cases')}><i className="fas fa-arrow-right"></i> View Details</button>
                                        </div>
                                    </div>
                                ))}
                                {acceptedCases.length === 0 && <div className="lawfirm-portal-no-data"><i className="fas fa-folder-open fa-3x" style={{ color: '#d1d5db', marginBottom: 12 }}></i><p>No accepted cases yet</p></div>}
                            </div>
                        )}
                        {caseRequestTab === 'denied' && (
                            <div className="lawfirm-portal-no-data"><i className="fas fa-ban fa-3x" style={{ color: '#ef4444', marginBottom: 12 }}></i><p>No denied requests</p><small>Once rejected, cases are no longer associated with your firm.</small></div>
                        )}
                    </div>
                )}

                {/* ASSIGNED CASES - added Close Case button */}
                {activePage === 'assigned-cases' && (
                    <div>
                        <div className="lawfirm-portal-page-header">
                            <h2>Assigned Cases ({assignedCases.length})</h2>
                        </div>
                        <div className="lawfirm-portal-table">
                            <table className="table">
                                <thead>
                                    <tr><th>Case</th><th>Client</th><th>Type</th><th>Status</th><th>Court</th><th>Assigned On</th><th>Actions</th></tr>
                                </thead>
                                <tbody>
                                    {assignedCases.map(c => (
                                        <tr key={c.id}>
                                            <td><strong>{c.title}</strong><br /><small style={{ color: '#9ca3af' }}>#{c.id}</small></td>
                                            <td>{c.client_name}<br /><small style={{ color: '#9ca3af' }}>{c.client_email}</small></td>
                                            <td>{c.case_type || '—'}</td>
                                            <td><span className={`badge ${getStatusBadgeClass(c.status)}`}>{getStatusText(c.status)}</span></td>
                                            <td>{c.court_location || '—'}</td>
                                            <td><small>{formatDate(c.assigned_at || c.created_at)}</small></td>
                                            <td>
                                                <button className="btn-sm btn-outline-primary me-1" onClick={() => { setSelectedChat({ caseId: c.id, caseTitle: c.title, otherPartyId: c.client_id, otherPartyName: c.client_name }); loadChatMessages(c.id, c.client_id); setActivePage('messages'); }}>
                                                    <i className="fas fa-comment"></i> Chat
                                                </button>
                                                {c.status !== 'closed' && (
                                                    <button className="btn-sm btn-outline-success" onClick={() => handleCloseCase(c.id)}>
                                                        <i className="fas fa-check-circle"></i> Mark Closed
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {assignedCases.length === 0 && <div className="lawfirm-portal-no-data"><i className="fas fa-briefcase fa-3x" style={{ color: '#d1d5db', marginBottom: 12 }}></i><p>No assigned cases yet</p></div>}
                        </div>
                    </div>
                )}

                {/* TEAM MEMBERS - added Delete button */}
                {activePage === 'team-members' && (
                    <div>
                        <div className="lawfirm-portal-page-header">
                            <h2>Team Members ({teamMembers.length})</h2>
                            <button className="lawfirm-portal-btn-primary" onClick={() => setShowAddTeamMemberForm(true)}>
                                <i className="fas fa-user-plus"></i> Add Team Member
                            </button>
                        </div>
                        {roleOptions.map(role => {
                            const group = teamMembers.filter(m => m.role === role.value);
                            if (group.length === 0) return null;
                            return (
                                <div key={role.value} style={{ marginBottom: 24 }}>
                                    <h4 style={{ color: '#374151', fontWeight: 600, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <span style={{ background: getRoleBadgeColor(role.value), color: 'white', borderRadius: 20, padding: '2px 12px', fontSize: '0.8rem' }}>{role.label}</span>
                                        <span style={{ fontSize: '0.875rem', color: '#9ca3af' }}>({group.length})</span>
                                    </h4>
                                    <div className="lawfirm-portal-table">
                                        <table className="table">
                                            <thead>
                                                <tr><th>Name</th><th>Email</th><th>Experience (yrs)</th><th>Status</th><th>Action</th></tr>
                                            </thead>
                                            <tbody>
                                                {group.map(m => (
                                                    <tr key={m.id}>
                                                        <td><strong>{m.name}</strong></td>
                                                        <td>{m.email}</td>
                                                        <td>{m.experience_years}</td>
                                                        <td><span style={{ background: '#dcfce7', color: '#166534', borderRadius: 20, padding: '2px 10px', fontSize: '0.75rem' }}>Active</span></td>
                                                        <td>
                                                            <button className="btn-sm btn-outline-danger" onClick={() => handleDeleteTeamMember(m.id)}>
                                                                <i className="fas fa-trash"></i> Delete
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            );
                        })}
                        {teamMembers.length === 0 && <div className="lawfirm-portal-no-data"><i className="fas fa-users fa-3x" style={{ color: '#d1d5db', marginBottom: 12 }}></i><p>No team members added yet. Click "Add Team Member" to get started.</p></div>}
                    </div>
                )}

                {/* COURT UPDATES (unchanged) */}
                {activePage === 'court-updates' && (
                    <div className="lawfirm-portal-court">
                        <div className="lawfirm-portal-page-header">
                            <h2>Court & Hearing Updates</h2>
                        </div>
                        <div className="lawfirm-portal-court-grid">
                            <div>
                                <h3 style={{ fontWeight: 600, marginBottom: 16, color: '#1a3c8b' }}><i className="fas fa-landmark me-2"></i> Upcoming Hearings</h3>
                                {courtUpdates.filter(u => u.update_type === 'hearing').length === 0 ? (
                                    <div style={{ background: '#f9fafb', borderRadius: 10, padding: 24, textAlign: 'center', color: '#9ca3af' }}><i className="fas fa-calendar-alt fa-2x mb-2"></i><p>No upcoming hearings from admin</p></div>
                                ) : courtUpdates.filter(u => u.update_type === 'hearing').map(u => (
                                    <div key={u.id} className="lawfirm-portal-update-item">
                                        <div className="lawfirm-portal-update-icon" style={{ background: '#dbeafe', color: '#1a3c8b' }}><i className="fas fa-landmark"></i></div>
                                        <div>
                                            <h4 style={{ margin: 0, fontWeight: 600 }}>{u.title}</h4>
                                            <p style={{ margin: '4px 0', color: '#6b7280' }}>{u.court_name}</p>
                                            <p style={{ margin: '2px 0', fontSize: '0.875rem', color: '#374151' }}>{u.description}</p>
                                            <small style={{ color: '#9ca3af' }}>{formatDate(u.date)}</small>
                                            <div style={{ marginTop: 8 }}><button className="btn-sm btn-outline-primary" onClick={() => forwardToClient(u)}><i className="fas fa-share me-1"></i> Forward to Client</button></div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <div>
                                <h3 style={{ fontWeight: 600, marginBottom: 16, color: '#1a3c8b' }}><i className="fas fa-file-alt me-2"></i> Court Orders & Updates</h3>
                                {courtUpdates.filter(u => u.update_type !== 'hearing').length === 0 ? (
                                    <div style={{ background: '#f9fafb', borderRadius: 10, padding: 24, textAlign: 'center', color: '#9ca3af' }}><i className="fas fa-file-alt fa-2x mb-2"></i><p>No court orders received from admin yet</p><small>Admin will send court updates for your assigned cases</small></div>
                                ) : courtUpdates.filter(u => u.update_type !== 'hearing').map(u => (
                                    <div key={u.id} className="lawfirm-portal-order-item">
                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                                <h4 style={{ margin: 0, fontWeight: 600 }}>{u.title}</h4>
                                                <span style={{ background: u.priority === 'high' ? '#fee2e2' : '#fef9c3', color: u.priority === 'high' ? '#dc2626' : '#ca8a04', borderRadius: 20, padding: '2px 8px', fontSize: '0.75rem' }}>{u.priority || 'Normal'}</span>
                                            </div>
                                            <p style={{ margin: '4px 0', color: '#374151', fontSize: '0.875rem' }}>{u.description}</p>
                                            <small style={{ color: '#9ca3af' }}>Case: {u.case_title} | {formatDate(u.date)}</small>
                                            <div style={{ marginTop: 8 }}><button className="btn-sm btn-outline-primary" onClick={() => forwardToClient(u)}><i className="fas fa-share me-1"></i> Forward to Client</button></div>
                                        </div>
                                        <button className="lawfirm-portal-btn-view-sm" style={{ marginLeft: 12 }}><i className="fas fa-download"></i></button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* MESSAGES (unchanged) */}
                {activePage === 'messages' && (
                    <div className="lawfirm-messages-container">
                        <div className="lawfirm-conversations-list">
                            <h4><i className="fas fa-comments me-2"></i>Conversations</h4>
                            {conversations.length === 0 ? (
                                <div className="text-center p-4 text-muted"><i className="fas fa-comment-slash fa-3x mb-3"></i><p>No active conversations</p><small>When clients message you, conversations will appear here</small></div>
                            ) : conversations.map(conv => (
                                <div key={conv.case_id} className={`lawfirm-conversation-item ${selectedChat?.caseId === conv.case_id ? 'active' : ''}`} onClick={() => { setSelectedChat({ caseId: conv.case_id, caseTitle: conv.case_title, otherPartyId: conv.other_party_id, otherPartyName: conv.other_party_name }); loadChatMessages(conv.case_id, conv.other_party_id); }}>
                                    <div className="lawfirm-conversation-avatar">{conv.other_party_name?.charAt(0) || 'C'}</div>
                                    <div className="lawfirm-conversation-info">
                                        <div className="lawfirm-conversation-name">{conv.other_party_name}</div>
                                        <div className="lawfirm-conversation-case">{conv.case_title}</div>
                                        <div className="lawfirm-conversation-last-msg">{conv.last_message?.substring(0, 50) || 'No messages yet'}</div>
                                    </div>
                                    {conv.unread_count > 0 && <div className="lawfirm-conversation-unread">{conv.unread_count}</div>}
                                </div>
                            ))}
                        </div>
                        <div className="lawfirm-chat-area">
                            {!selectedChat ? (
                                <div className="lawfirm-chat-placeholder"><i className="fas fa-comments fa-4x mb-3 text-muted"></i><h5>Select a Conversation</h5><p>Choose a case from the left to start messaging with the client</p></div>
                            ) : (
                                <>
                                    <div className="lawfirm-chat-header">
                                        <div className="lawfirm-chat-header-info">
                                            <div className="lawfirm-chat-avatar">{selectedChat.otherPartyName?.charAt(0)}</div>
                                            <div><h5 className="mb-0">{selectedChat.otherPartyName}</h5><small className="text-muted">Case: {selectedChat.caseTitle}</small></div>
                                        </div>
                                    </div>
                                    <div className="lawfirm-chat-messages">
                                        {chatMessages.length === 0 ? (
                                            <div className="text-center text-muted mt-5"><i className="fas fa-comment-dots fa-3x mb-3"></i><p>No messages yet. Start the conversation!</p></div>
                                        ) : chatMessages.map(msg => (
                                            <div key={msg.id} className={`lawfirm-message ${msg.sender_role === 'lawfirm' ? 'sent' : 'received'}`}>
                                                <div className="lawfirm-message-bubble"><p>{msg.content}</p><small>{formatDate(msg.created_at)}</small></div>
                                            </div>
                                        ))}
                                        <div ref={chatEndRef} />
                                    </div>
                                    <div className="lawfirm-chat-input">
                                        <input type="text" className="form-control" placeholder="Type your message..." value={newMessage} onChange={e => setNewMessage(e.target.value)} onKeyPress={e => e.key === 'Enter' && sendMessage()} />
                                        <button className="btn-advocare" onClick={sendMessage}><i className="fas fa-paper-plane"></i> Send</button>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                )}

                {/* FIRM PROFILE (unchanged but works) */}
                {activePage === 'profile' && firmData && (
                    <div className="lawfirm-portal-profile">
                        {!editingProfile ? (
                            <>
                                <div className="lawfirm-portal-profile-header">
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 20, flex: 1 }}>
                                        <div className="lawfirm-portal-profile-avatar">{firmData.firm_name?.charAt(0)}</div>
                                        <div>
                                            <h2 style={{ margin: 0 }}>{firmData.firm_name}</h2>
                                            <p style={{ margin: 0, color: '#6b7280' }}>Registered Law Firm</p>
                                            <span style={{ background: '#dcfce7', color: '#166534', borderRadius: 20, padding: '2px 12px', fontSize: '0.8rem' }}><i className="fas fa-check-circle me-1"></i> Verified & Approved</span>
                                        </div>
                                    </div>
                                    <button className="lawfirm-portal-btn-primary" onClick={() => setEditingProfile(true)}><i className="fas fa-edit"></i> Edit Profile</button>
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20, marginTop: 24 }}>
                                    <div className="lawfirm-portal-profile-section"><h3><i className="fas fa-info-circle me-2" style={{ color: '#1a3c8b' }}></i>Basic Information</h3><div className="profile-field"><label>Firm Name</label><span>{firmData.firm_name}</span></div><div className="profile-field"><label>Registration Number</label><span>{firmData.registration_no || 'N/A'}</span></div><div className="profile-field"><label>Experience (Years)</label><span>{firmData.experience || 'N/A'}</span></div><div className="profile-field"><label>Specialization</label><span>{firmData.specialization || 'N/A'}</span></div></div>
                                    <div className="lawfirm-portal-profile-section"><h3><i className="fas fa-envelope me-2" style={{ color: '#1a3c8b' }}></i>Contact Information</h3><div className="profile-field"><label>Email</label><span>{firmData.email || 'N/A'}</span></div><div className="profile-field"><label>Phone</label><span>{firmData.phone || 'Not provided'}</span></div><div className="profile-field"><label>Website</label><span>{firmData.website || 'Not provided'}</span></div></div>
                                    <div className="lawfirm-portal-profile-section"><h3><i className="fas fa-map-marker-alt me-2" style={{ color: '#1a3c8b' }}></i>Address</h3><div className="profile-field"><label>Street Address</label><span>{firmData.address || 'Not provided'}</span></div><div className="profile-field"><label>City</label><span>{firmData.city || 'Not provided'}</span></div><div className="profile-field"><label>State</label><span>{firmData.state || 'Not provided'}</span></div></div>
                                    <div className="lawfirm-portal-profile-section"><h3><i className="fas fa-gavel me-2" style={{ color: '#1a3c8b' }}></i>Primary Lawyer</h3><div className="profile-field"><label>Name</label><span>{firmData.primary_lawyer_name || 'N/A'}</span></div><div className="profile-field"><label>Bar Council ID</label><span>{firmData.primary_lawyer_bar_council_id || 'N/A'}</span></div><div className="profile-field"><label>Experience (Years)</label><span>{firmData.primary_lawyer_years_experience || 'N/A'}</span></div><div className="profile-field"><label>Specialization</label><span>{firmData.primary_lawyer_specialization || 'N/A'}</span></div></div>
                                    <div className="lawfirm-portal-profile-section"><h3><i className="fas fa-chart-bar me-2" style={{ color: '#1a3c8b' }}></i>Performance</h3><div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}><div style={{ background: '#f8fafc', borderRadius: 8, padding: 12, textAlign: 'center' }}><div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1a3c8b' }}>{stats.totalCases}</div><div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Total Cases</div></div><div style={{ background: '#f8fafc', borderRadius: 8, padding: 12, textAlign: 'center' }}><div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1a3c8b' }}>{stats.successRate || 0}%</div><div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Success Rate</div></div><div style={{ background: '#f8fafc', borderRadius: 8, padding: 12, textAlign: 'center' }}><div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1a3c8b' }}>{stats.activeCases}</div><div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Active Cases</div></div><div style={{ background: '#f8fafc', borderRadius: 8, padding: 12, textAlign: 'center' }}><div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1a3c8b' }}>{firmData.rating || '4.5'} ⭐</div><div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Rating</div></div></div></div>
                                </div>
                                {firmData.bio && (<div className="lawfirm-portal-profile-section" style={{ marginTop: 20 }}><h3><i className="fas fa-file-alt me-2" style={{ color: '#1a3c8b' }}></i>About the Firm</h3><p style={{ color: '#374151', lineHeight: 1.7 }}>{firmData.bio}</p></div>)}
                            </>
                        ) : (
                            <form onSubmit={handleProfileSave}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}><h2 style={{ margin: 0 }}>Edit Firm Profile</h2><div style={{ display: 'flex', gap: 12 }}><button type="button" onClick={() => setEditingProfile(false)} style={{ padding: '8px 20px', borderRadius: 8, border: '1px solid #d1d5db', background: 'white', cursor: 'pointer' }}>Cancel</button><button type="submit" className="lawfirm-portal-btn-primary"><i className="fas fa-save me-2"></i>Save Changes</button></div></div>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
                                    {[ { label: 'Firm Name', key: 'firm_name', type: 'text' }, { label: 'Registration Number', key: 'registration_no', type: 'text' }, { label: 'Phone', key: 'phone', type: 'tel' }, { label: 'Website', key: 'website', type: 'url' }, { label: 'City', key: 'city', type: 'text' }, { label: 'State', key: 'state', type: 'text' }, { label: 'Primary Lawyer Name', key: 'primary_lawyer_name', type: 'text' }, { label: 'Bar Council ID', key: 'primary_lawyer_bar_council_id', type: 'text' }, { label: 'Primary Lawyer Experience (years)', key: 'primary_lawyer_years_experience', type: 'number' }, { label: 'Primary Lawyer Specialization', key: 'primary_lawyer_specialization', type: 'text' }, { label: 'Firm Experience (e.g. 3-5)', key: 'experience', type: 'text' }, { label: 'Specialization (comma-separated)', key: 'specialization', type: 'text' } ].map(field => (
                                        <div key={field.key}><label style={{ fontSize: '0.875rem', fontWeight: 500, color: '#374151', display: 'block', marginBottom: 4 }}>{field.label}</label><input type={field.type} value={profileForm[field.key] || ''} onChange={e => setProfileForm({ ...profileForm, [field.key]: e.target.value })} style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 8, fontSize: '0.875rem', boxSizing: 'border-box' }} /></div>
                                    ))}
                                    <div style={{ gridColumn: '1/-1' }}><label style={{ fontSize: '0.875rem', fontWeight: 500, color: '#374151', display: 'block', marginBottom: 4 }}>Street Address</label><input type="text" value={profileForm.address || ''} onChange={e => setProfileForm({ ...profileForm, address: e.target.value })} style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 8, fontSize: '0.875rem', boxSizing: 'border-box' }} /></div>
                                    <div style={{ gridColumn: '1/-1' }}><label style={{ fontSize: '0.875rem', fontWeight: 500, color: '#374151', display: 'block', marginBottom: 4 }}>About the Firm</label><textarea rows={4} value={profileForm.bio || ''} onChange={e => setProfileForm({ ...profileForm, bio: e.target.value })} style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 8, fontSize: '0.875rem', resize: 'vertical', boxSizing: 'border-box' }} /></div>
                                </div>
                            </form>
                        )}
                    </div>
                )}
            </div>

            {/* ADD TEAM MEMBER MODAL */}
            {showAddTeamMemberForm && (
                <div className="lawfirm-portal-modal" onClick={() => setShowAddTeamMemberForm(false)}>
                    <div className="lawfirm-add-lawyer-modal" onClick={e => e.stopPropagation()}>
                        <div className="lawfirm-portal-modal-header"><div><h3 style={{ margin: 0 }}>Add Team Member</h3><p style={{ margin: 0, fontSize: '0.8rem', color: '#6b7280' }}>Add a new member to your law firm team</p></div><button onClick={() => setShowAddTeamMemberForm(false)} style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#6b7280' }}>&times;</button></div>
                        <form onSubmit={handleAddTeamMember} className="lawfirm-add-lawyer-form">
                            <div className="modal-section"><h4 className="modal-section-title"><i className="fas fa-user me-2"></i>Basic Information</h4><div className="modal-grid-2"><div><label>Full Name *</label><input type="text" value={newTeamMember.name} onChange={e => setNewTeamMember({ ...newTeamMember, name: e.target.value })} required placeholder="Full name" /></div><div><label>Email Address *</label><input type="email" value={newTeamMember.email} onChange={e => setNewTeamMember({ ...newTeamMember, email: e.target.value })} required placeholder="email@example.com" /></div><div><label>Role *</label><select value={newTeamMember.role} onChange={e => setNewTeamMember({ ...newTeamMember, role: e.target.value })} required>{roleOptions.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}</select></div><div><label>Experience (years) *</label><input type="number" value={newTeamMember.experience_years} onChange={e => setNewTeamMember({ ...newTeamMember, experience_years: e.target.value })} required min="0" max="50" placeholder="Years of experience" /></div></div></div>
                            <div className="lawfirm-portal-modal-footer"><button type="button" onClick={() => setShowAddTeamMemberForm(false)}>Cancel</button><button type="submit" style={{ background: '#1a3c8b', color: 'white' }}><i className="fas fa-user-plus me-1"></i> Add Team Member</button></div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default LawfirmPortal;


























// import React, { useState, useEffect, useRef, useCallback } from 'react';
// import { useNavigate } from 'react-router-dom';
// import API from '../services/api';
// import Chart from 'chart.js/auto';

// function LawfirmPortal() {
//     const navigate = useNavigate();
//     const [loading, setLoading] = useState(true);
//     const [activePage, setActivePage] = useState('dashboard');
//     const [firmData, setFirmData] = useState(null);
//     const [editingProfile, setEditingProfile] = useState(false);
//     const [profileForm, setProfileForm] = useState({});
//     const [stats, setStats] = useState({ totalCases: 0, activeCases: 0, pendingRequests: 0, successRate: 0 });
    
//     // Case Requests with tabs
//     const [caseRequests, setCaseRequests] = useState([]);
//     const [acceptedCases, setAcceptedCases] = useState([]);
//     const [caseRequestTab, setCaseRequestTab] = useState('pending');
    
//     const [assignedCases, setAssignedCases] = useState([]);
//     const [teamMembers, setTeamMembers] = useState([]);   // ✅ Team members from backend
//     const [courtUpdates, setCourtUpdates] = useState([]);

//     // Chat states
//     const [conversations, setConversations] = useState([]);
//     const [selectedChat, setSelectedChat] = useState(null);
//     const [chatMessages, setChatMessages] = useState([]);
//     const [newMessage, setNewMessage] = useState('');

//     const [showAddTeamMemberForm, setShowAddTeamMemberForm] = useState(false);
//     const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
//     const [newTeamMember, setNewTeamMember] = useState({
//         name: '',
//         email: '',
//         role: 'associate',
//         experience_years: ''
//     });

//     const chartRef = useRef(null);
//     const chartInstanceRef = useRef(null);
//     const chatPollInterval = useRef(null);
//     const chatEndRef = useRef(null);

//     const roleOptions = [
//         { value: 'associate', label: 'Associate' },
//         { value: 'partner', label: 'Partner' },
//         { value: 'senior_advocate', label: 'Senior Advocate' },
//         { value: 'legal_assistant', label: 'Legal Assistant' },
//         { value: 'paralegal', label: 'Paralegal' },
//     ];

//     // ========== CHAT ==========
//     const loadConversations = useCallback(async () => {
//         try {
//             const res = await API.get('chat/conversations/');
//             setConversations(res.data);
//         } catch (err) { console.error('Failed to load conversations:', err); }
//     }, []);

//     const loadChatMessages = async (caseId, otherPartyId) => {
//         try {
//             const res = await API.get(`chat/${caseId}/${otherPartyId}/`);
//             setChatMessages(res.data);
//         } catch (err) { console.error('Failed to load messages:', err); }
//     };

//     const sendMessage = async () => {
//         if (!newMessage.trim() || !selectedChat) return;
//         const msg = newMessage;
//         setNewMessage('');
//         try {
//             await API.post('chat/send/', { case_id: selectedChat.caseId, receiver_id: selectedChat.otherPartyId, content: msg });
//             await loadChatMessages(selectedChat.caseId, selectedChat.otherPartyId);
//             await loadConversations();
//         } catch (err) {
//             console.error('Failed to send message:', err);
//             setNewMessage(msg);
//         }
//     };

//     const forwardToClient = async (update) => {
//         if (!update.case_id || !update.client_id) {
//             alert('Cannot forward: missing case or client information');
//             return;
//         }
//         try {
//             await API.post('chat/send/', {
//                 case_id: update.case_id,
//                 receiver_id: update.client_id,
//                 content: `📢 COURT UPDATE: ${update.message || update.description}\n\nDate: ${formatDate(update.date)}\nCase: ${update.case_title}\n\nPlease review and let us know if you have any questions.`
//             });
//             alert('Update forwarded to client via chat');
//         } catch (err) {
//             console.error('Forward failed:', err);
//             alert('Failed to forward update');
//         }
//     };

//     // ========== CASE REQUESTS ==========
//     const handleAcceptRequest = async (caseId) => {
//         try {
//             await API.post(`cases/${caseId}/accept/`);
//             alert('Case request accepted successfully!');
//             await loadPendingRequests();
//             await loadAssignedCases();
//             await loadAcceptedCases();
//             await loadConversations();
//         } catch (error) { 
//             console.error('Accept error:', error);
//             alert('Failed to accept request'); 
//         }
//     };

//     const handleRejectRequest = async (caseId) => {
//         if (!window.confirm('Are you sure you want to reject this case?')) return;
//         try {
//             await API.post(`cases/${caseId}/reject/`);
//             alert('Case request rejected');
//             await loadPendingRequests();
//             await loadAssignedCases();
//             await loadAcceptedCases();
//         } catch (error) { 
//             console.error('Reject error:', error);
//             alert('Failed to reject request'); 
//         }
//     };

//     const loadPendingRequests = async () => {
//         try {
//             const res = await API.get('cases/pending-requests/');
//             setCaseRequests(res.data || []);
//         } catch (err) { 
//             console.error('Pending requests error:', err);
//             setCaseRequests([]);
//         }
//     };

//     const loadAcceptedCases = async () => {
//         try {
//             const res = await API.get('cases/accepted-cases/');
//             setAcceptedCases(res.data || []);
//         } catch (err) {
//             console.error('Accepted cases error:', err);
//             if (assignedCases.length) {
//                 setAcceptedCases(assignedCases.filter(c => c.status === 'in_progress'));
//             } else {
//                 setAcceptedCases([]);
//             }
//         }
//     };

//     const loadAssignedCases = async () => {
//         try {
//             const res = await API.get('cases/assigned-cases/');
//             setAssignedCases(res.data || []);
//         } catch (err) { 
//             console.error('Assigned cases error:', err);
//             setAssignedCases([]);
//         }
//     };

//     // ========== TEAM MEMBERS MANAGEMENT ==========
//     const loadTeamMembers = async () => {
//         try {
//             const res = await API.get('cases/lawfirm-lawyers/'); // returns TeamMember list
//             setTeamMembers(res.data || []);
//         } catch (err) {
//             console.error('Failed to load team members:', err);
//             setTeamMembers([]);
//         }
//     };

//     const handleAddTeamMember = async (e) => {
//         e.preventDefault();
//         if (!newTeamMember.name || !newTeamMember.email || !newTeamMember.role || !newTeamMember.experience_years) {
//             alert('Please fill all required fields');
//             return;
//         }
//         try {
//             await API.post('cases/add-lawyer/', {
//                 name: newTeamMember.name,
//                 email: newTeamMember.email,
//                 role: newTeamMember.role,
//                 experience_years: parseInt(newTeamMember.experience_years, 10)
//             });
//             await loadTeamMembers();
//             setShowAddTeamMemberForm(false);
//             setNewTeamMember({ name: '', email: '', role: 'associate', experience_years: '' });
//             alert('Team member added successfully!');
//         } catch (error) {
//             console.error('Add team member error:', error);
//             alert('Failed to add team member');
//         }
//     };

//     // ========== FIRM PROFILE ==========
//     const handleProfileSave = async (e) => {
//         e.preventDefault();
//         try {
//             await API.put('profiles/lawfirm-dashboard/', profileForm);
//             setFirmData({ ...firmData, ...profileForm });
//             setEditingProfile(false);
//             alert('Profile updated successfully!');
//         } catch (error) {
//             console.error('Profile update error:', error);
//             alert('Failed to update profile');
//         }
//     };

//     // ========== DASHBOARD CHART ==========
//     const initChart = useCallback(() => {
//         if (!chartRef.current) return;
//         if (chartInstanceRef.current) {
//             chartInstanceRef.current.destroy();
//             chartInstanceRef.current = null;
//         }
//         const ctx = chartRef.current.getContext('2d');
//         chartInstanceRef.current = new Chart(ctx, {
//             type: 'bar',
//             data: {
//                 labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
//                 datasets: [
//                     {
//                         label: 'New Cases',
//                         data: [12, 19, 8, 15, 12, 17, 10, 14, 16, 12, 10, 15],
//                         backgroundColor: 'rgba(26, 60, 139, 0.75)',
//                         borderColor: 'rgba(26, 60, 139, 1)',
//                         borderWidth: 2,
//                         borderRadius: 6,
//                     },
//                     {
//                         label: 'Closed Cases',
//                         data: [8, 12, 6, 10, 9, 13, 7, 11, 12, 9, 8, 11],
//                         backgroundColor: 'rgba(212, 175, 55, 0.75)',
//                         borderColor: 'rgba(212, 175, 55, 1)',
//                         borderWidth: 2,
//                         borderRadius: 6,
//                     }
//                 ]
//             },
//             options: {
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 plugins: {
//                     legend: { position: 'top' },
//                     tooltip: { mode: 'index', intersect: false }
//                 },
//                 scales: {
//                     y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
//                     x: { grid: { display: false } }
//                 }
//             }
//         });
//     }, []);

//     // ========== UTILITIES ==========
//     const handleLogout = () => { localStorage.clear(); navigate('/'); };

//     const formatDate = (dateString) => {
//         if (!dateString) return 'N/A';
//         try {
//             return new Date(dateString).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
//         } catch { return 'Invalid date'; }
//     };

//     const getStatusBadgeClass = (status) => {
//         const map = { pending: 'status-pending', in_progress: 'status-in-court', assigned: 'status-assigned', resolved: 'status-closed', closed: 'status-closed' };
//         return map[status] || 'status-pending';
//     };

//     const getStatusText = (status) => {
//         const map = { pending: 'Pending', assigned: 'Assigned', in_progress: 'In Progress', resolved: 'Resolved', closed: 'Closed' };
//         return map[status] || status;
//     };

//     const getRoleBadgeColor = (role) => {
//         const map = { partner: '#1a3c8b', senior_advocate: '#7c3aed', associate: '#0891b2', legal_assistant: '#059669', paralegal: '#d97706' };
//         return map[role] || '#6b7280';
//     };

//     // ========== DATA LOADING ==========
//     useEffect(() => {
//         const loadDashboard = async () => {
//             try {
//                 const token = localStorage.getItem('access_token');
//                 if (!token) { navigate('/'); return; }
                
//                 // Load firm profile
//                 try {
//                     const profileRes = await API.get('profiles/lawfirm-dashboard/');
//                     if (profileRes.data.status === 'approved') {
//                         setFirmData(profileRes.data);
//                         setProfileForm(profileRes.data);
//                     } else if (profileRes.data.status === 'pending') {
//                         navigate('/lawfirm-pending-onboarding'); return;
//                     } else { navigate('/lawfirm-onboarding'); return; }
//                 } catch (err) { console.error('Profile error:', err); }
                
//                 // Load stats
//                 try { 
//                     const statsRes = await API.get('cases/lawfirm-stats/'); 
//                     setStats(statsRes.data);
//                 } catch (e) { 
//                     console.error('Stats error:', e);
//                     setStats({ totalCases: 0, activeCases: 0, pendingRequests: 0, successRate: 0 });
//                 }
                
//                 await loadPendingRequests();
//                 await loadAssignedCases();
//                 await loadAcceptedCases();
//                 await loadConversations();
//                 await loadTeamMembers();
                
//                 // Load court updates
//                 try { 
//                     const updatesRes = await API.get('cases/court-updates/'); 
//                     setCourtUpdates(updatesRes.data || []); 
//                 } catch (e) { console.error('Court updates error:', e); }
//             } catch (error) {
//                 console.error('Dashboard load error:', error);
//                 if (error.response?.status === 401) { localStorage.clear(); navigate('/'); }
//             } finally { setLoading(false); }
//         };
//         loadDashboard();
//     }, [navigate]);

//     // Chart initialization
//     useEffect(() => {
//         if (activePage === 'dashboard') {
//             const timer = setTimeout(() => { if (chartRef.current) initChart(); }, 100);
//             return () => clearTimeout(timer);
//         }
//         return () => {
//             if (chartInstanceRef.current) { chartInstanceRef.current.destroy(); chartInstanceRef.current = null; }
//         };
//     }, [activePage, initChart]);

//     // Chat polling
//     useEffect(() => {
//         if (chatPollInterval.current) clearInterval(chatPollInterval.current);
//         if (selectedChat && activePage === 'messages') {
//             chatPollInterval.current = setInterval(() => loadChatMessages(selectedChat.caseId, selectedChat.otherPartyId), 3000);
//         }
//         return () => { if (chatPollInterval.current) clearInterval(chatPollInterval.current); };
//     }, [selectedChat, activePage]);

//     useEffect(() => {
//         if (chatEndRef.current) chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
//     }, [chatMessages]);

//     if (loading) {
//         return (
//             <div className="lawfirm-loading-container">
//                 <div className="lawfirm-loading-card">
//                     <div className="lawfirm-spinner"></div>
//                     <h2>Loading Dashboard...</h2>
//                 </div>
//             </div>
//         );
//     }

//     const unreadCount = conversations.reduce((sum, c) => sum + (c.unread_count || 0), 0);
//     const navItems = [
//         { id: 'dashboard', icon: 'tachometer-alt', label: 'Dashboard' },
//         { id: 'case-requests', icon: 'file-contract', label: 'Case Requests', badge: caseRequests.length },
//         { id: 'assigned-cases', icon: 'briefcase', label: 'Assigned Cases' },
//         { id: 'team-members', icon: 'users', label: 'Team Members' },
//         { id: 'court-updates', icon: 'gavel', label: 'Court Updates' },
//         { id: 'messages', icon: 'comments', label: 'Messages', badge: unreadCount },
//         { id: 'profile', icon: 'building', label: 'Firm Profile' },
//     ];

//     return (
//         <div className="lawfirm-portal-wrapper">
//             {/* Sidebar */}
//             <div className={`lawfirm-portal-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
//                 <div className="lawfirm-portal-logo">
//                     <div className="lawfirm-portal-logo-icon"><i className="fas fa-balance-scale"></i></div>
//                     {!sidebarCollapsed && <div className="lawfirm-portal-logo-text">Advocare</div>}
//                 </div>
//                 <div className="lawfirm-portal-nav">
//                     {navItems.map(item => (
//                         <div key={item.id}
//                             className={`lawfirm-portal-nav-item ${activePage === item.id ? 'active' : ''}`}
//                             onClick={() => {
//                                 setActivePage(item.id);
//                                 if (item.id === 'case-requests') {
//                                     loadPendingRequests();
//                                     loadAcceptedCases();
//                                 }
//                                 if (item.id === 'assigned-cases') loadAssignedCases();
//                                 if (item.id === 'team-members') loadTeamMembers();
//                             }}>
//                             <i className={`fas fa-${item.icon}`}></i>
//                             {!sidebarCollapsed && <span>{item.label}</span>}
//                             {item.badge > 0 && <span className="lawfirm-portal-badge">{item.badge}</span>}
//                         </div>
//                     ))}
//                 </div>
//                 {!sidebarCollapsed && (
//                     <div className="lawfirm-portal-user">
//                         <div className="lawfirm-portal-avatar">{firmData?.firm_name?.charAt(0) || 'F'}</div>
//                         <div className="lawfirm-portal-user-info">
//                             <h4>{firmData?.firm_name || 'Law Firm'}</h4>
//                             <p>Law Firm Admin</p>
//                         </div>
//                     </div>
//                 )}
//             </div>

//             {/* Main Content */}
//             <div className="lawfirm-portal-main">
//                 <div className="lawfirm-portal-header">
//                     <div className="lawfirm-portal-title">
//                         <button className="lawfirm-portal-toggle" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
//                             <i className="fas fa-bars"></i>
//                         </button>
//                         <span>{navItems.find(n => n.id === activePage)?.label || 'Dashboard'}</span>
//                     </div>
//                     <div className="lawfirm-portal-actions">
//                         <div className="lawfirm-portal-search">
//                             <i className="fas fa-search"></i>
//                             <input type="text" placeholder="Search..." />
//                         </div>
//                         <div className="lawfirm-portal-notification">
//                             <i className="fas fa-bell"></i>
//                             <span className="lawfirm-portal-dot"></span>
//                         </div>
//                         <button className="lawfirm-portal-logout" onClick={handleLogout}>
//                             <i className="fas fa-sign-out-alt"></i> Logout
//                         </button>
//                     </div>
//                 </div>

//                 {/* DASHBOARD */}
//                 {activePage === 'dashboard' && (
//                     <div className="lawfirm-portal-dashboard">
//                         <div className="lawfirm-portal-kpi">
//                             {[
//                                 { icon: 'folder-open', value: stats.totalCases, label: 'Total Cases', color: '#1a3c8b' },
//                                 { icon: 'gavel', value: stats.activeCases, label: 'Active Cases', color: '#0891b2' },
//                                 { icon: 'clock', value: stats.pendingRequests, label: 'Pending Requests', color: '#d97706' },
//                                 { icon: 'chart-line', value: `${stats.successRate || 0}%`, label: 'Success Rate', color: '#059669' },
//                             ].map((kpi, i) => (
//                                 <div key={i} className="lawfirm-portal-kpi-card" style={{ borderTop: `4px solid ${kpi.color}` }}>
//                                     <div className="lawfirm-portal-kpi-icon" style={{ background: kpi.color + '18', color: kpi.color }}>
//                                         <i className={`fas fa-${kpi.icon}`}></i>
//                                     </div>
//                                     <div>
//                                         <h3 style={{ color: kpi.color, fontSize: '2rem', fontWeight: 700, margin: 0 }}>{kpi.value}</h3>
//                                         <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>{kpi.label}</p>
//                                     </div>
//                                 </div>
//                             ))}
//                         </div>

//                         <div className="lawfirm-portal-stats">
//                             <div className="lawfirm-portal-chart">
//                                 <div className="lawfirm-portal-section-title">
//                                     <span>Case Statistics (Monthly)</span>
//                                     <select><option>Last 12 Months</option><option>Last 6 Months</option><option>Last 3 Months</option></select>
//                                 </div>
//                                 <div style={{ height: '280px', position: 'relative' }}>
//                                     <canvas ref={chartRef}></canvas>
//                                 </div>
//                             </div>
//                             <div className="lawfirm-portal-activity">
//                                 <div className="lawfirm-portal-section-title">
//                                     <span>Recent Activity</span>
//                                     <button onClick={() => setActivePage('assigned-cases')}>View All</button>
//                                 </div>
//                                 {assignedCases.slice(0, 4).map(c => (
//                                     <div key={c.id} className="lawfirm-portal-activity-item">
//                                         <div className="lawfirm-portal-activity-icon"><i className="fas fa-landmark"></i></div>
//                                         <div>
//                                             <h4>{c.title}</h4>
//                                             <p>Client: {c.client_name}</p>
//                                             <span className={`badge ${getStatusBadgeClass(c.status)}`}>{getStatusText(c.status)}</span>
//                                             <small style={{ display: 'block', marginTop: 4 }}>{formatDate(c.updated_at)}</small>
//                                         </div>
//                                     </div>
//                                 ))}
//                                 {assignedCases.length === 0 && <p style={{ color: '#9ca3af', textAlign: 'center', padding: '20px' }}>No recent activity</p>}
//                             </div>
//                         </div>

//                         <div className="lawfirm-portal-actions-grid">
//                             <button className="lawfirm-portal-action-card" onClick={() => setActivePage('case-requests')}>
//                                 <i className="fas fa-file-contract"></i><span>View Case Requests</span>
//                             </button>
//                             <button className="lawfirm-portal-action-card" onClick={() => { setActivePage('team-members'); setShowAddTeamMemberForm(true); }}>
//                                 <i className="fas fa-user-plus"></i><span>Add Team Member</span>
//                             </button>
//                             <button className="lawfirm-portal-action-card" onClick={() => setActivePage('court-updates')}>
//                                 <i className="fas fa-gavel"></i><span>Court Updates</span>
//                             </button>
//                             <button className="lawfirm-portal-action-card" onClick={() => setActivePage('messages')}>
//                                 <i className="fas fa-comment-medical"></i><span>Messages</span>
//                             </button>
//                         </div>
//                     </div>
//                 )}

//                 {/* CASE REQUESTS */}
//                 {activePage === 'case-requests' && (
//                     <div>
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Case Requests</h2>
//                         </div>

//                         <div style={{
//                             display: 'flex', gap: 8,
//                             background: '#f3f4f6', padding: 4,
//                             borderRadius: 12, width: 'fit-content', marginBottom: 24
//                         }}>
//                             {[
//                                 { key: 'pending', label: 'Pending', count: caseRequests.length, dot: '#f59e0b', activeBadge: { bg: '#fef3c7', color: '#92400e' } },
//                                 { key: 'accepted', label: 'Accepted', count: acceptedCases.length, dot: '#10b981', activeBadge: { bg: '#d1fae5', color: '#065f46' } },
//                                 { key: 'denied', label: 'Denied', count: null, dot: '#ef4444', activeBadge: { bg: '#fee2e2', color: '#991b1b' } },
//                             ].map(tab => {
//                                 const isActive = caseRequestTab === tab.key;
//                                 return (
//                                     <button
//                                         key={tab.key}
//                                         onClick={() => setCaseRequestTab(tab.key)}
//                                         style={{
//                                             display: 'flex', alignItems: 'center', gap: 7,
//                                             padding: '8px 18px', borderRadius: 9, border: 'none',
//                                             cursor: 'pointer', fontSize: 13, fontWeight: 500,
//                                             transition: 'all 0.18s',
//                                             background: isActive ? '#ffffff' : 'transparent',
//                                             color: isActive ? '#111827' : '#6b7280',
//                                             boxShadow: isActive ? '0 1px 4px rgba(0,0,0,0.08)' : 'none',
//                                         }}>
//                                         <span style={{ width: 7, height: 7, borderRadius: '50%', background: tab.dot, flexShrink: 0 }} />
//                                         {tab.label}
//                                         {tab.count !== null && (
//                                             <span style={{
//                                                 fontSize: 11, fontWeight: 600,
//                                                 padding: '2px 8px', borderRadius: 20,
//                                                 background: isActive ? tab.activeBadge.bg : '#e5e7eb',
//                                                 color: isActive ? tab.activeBadge.color : '#6b7280',
//                                             }}>
//                                                 {tab.count}
//                                             </span>
//                                         )}
//                                     </button>
//                                 );
//                             })}
//                         </div>

//                         {caseRequestTab === 'pending' && (
//                             <div className="lawfirm-portal-requests-grid">
//                                 {caseRequests.map(req => (
//                                     <div key={req.id} className="lawfirm-portal-request-card">
//                                         <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
//                                             <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>{req.title}</h3>
//                                             <span className="lawfirm-portal-case-type">{req.case_type}</span>
//                                         </div>
//                                         <p className="lawfirm-portal-case-desc">{req.description?.substring(0, 150)}...</p>
//                                         <div className="lawfirm-portal-client">
//                                             <div className="lawfirm-portal-client-avatar">{req.client_name?.charAt(0)}</div>
//                                             <div>
//                                                 <h4 style={{ margin: 0 }}>{req.client_name}</h4>
//                                                 <p style={{ margin: 0, fontSize: '0.8rem', color: '#6b7280' }}>{req.client_email}</p>
//                                                 <small style={{ color: '#9ca3af' }}>Submitted: {formatDate(req.created_at)}</small>
//                                             </div>
//                                         </div>
//                                         <div className="lawfirm-portal-request-actions">
//                                             <button className="lawfirm-portal-btn-accept" onClick={() => handleAcceptRequest(req.id)}>
//                                                 <i className="fas fa-check"></i> Accept
//                                             </button>
//                                             <button className="lawfirm-portal-btn-reject" onClick={() => handleRejectRequest(req.id)}>
//                                                 <i className="fas fa-times"></i> Reject
//                                             </button>
//                                         </div>
//                                     </div>
//                                 ))}
//                                 {caseRequests.length === 0 && (
//                                     <div className="lawfirm-portal-no-data">
//                                         <i className="fas fa-check-circle fa-3x" style={{ color: '#10b981', marginBottom: 12 }}></i>
//                                         <p>No pending case requests</p>
//                                     </div>
//                                 )}
//                             </div>
//                         )}

//                         {caseRequestTab === 'accepted' && (
//                             <div className="lawfirm-portal-requests-grid">
//                                 {acceptedCases.map(c => (
//                                     <div key={c.id} className="lawfirm-portal-request-card" style={{ borderLeftColor: '#10b981' }}>
//                                         <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
//                                             <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>{c.title}</h3>
//                                             <span className="lawfirm-portal-case-type">{c.case_type}</span>
//                                         </div>
//                                         <p className="lawfirm-portal-case-desc">{c.description?.substring(0, 150)}...</p>
//                                         <div className="lawfirm-portal-client">
//                                             <div className="lawfirm-portal-client-avatar" style={{ background: '#d1fae5', color: '#065f46' }}>
//                                                 {c.client_name?.charAt(0)}
//                                             </div>
//                                             <div>
//                                                 <h4 style={{ margin: 0 }}>{c.client_name}</h4>
//                                                 <p style={{ margin: 0, fontSize: '0.8rem', color: '#6b7280' }}>{c.client_email}</p>
//                                                 <small style={{ color: '#9ca3af' }}>Accepted on: {formatDate(c.updated_at)}</small>
//                                             </div>
//                                         </div>
//                                         <div className="lawfirm-portal-request-actions">
//                                             <button className="lawfirm-portal-btn-view" onClick={() => setActivePage('assigned-cases')}>
//                                                 <i className="fas fa-arrow-right"></i> View Details
//                                             </button>
//                                         </div>
//                                     </div>
//                                 ))}
//                                 {acceptedCases.length === 0 && (
//                                     <div className="lawfirm-portal-no-data">
//                                         <i className="fas fa-folder-open fa-3x" style={{ color: '#d1d5db', marginBottom: 12 }}></i>
//                                         <p>No accepted cases yet</p>
//                                     </div>
//                                 )}
//                             </div>
//                         )}

//                         {caseRequestTab === 'denied' && (
//                             <div className="lawfirm-portal-no-data">
//                                 <i className="fas fa-ban fa-3x" style={{ color: '#ef4444', marginBottom: 12 }}></i>
//                                 <p style={{ fontWeight: 500, color: '#374151' }}>No denied requests</p>
//                                 <small style={{ color: '#9ca3af' }}>Once rejected, cases are no longer associated with your firm.</small>
//                             </div>
//                         )}
//                     </div>
//                 )}

//                 {/* ASSIGNED CASES */}
//                 {activePage === 'assigned-cases' && (
//                     <div>
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Assigned Cases ({assignedCases.length})</h2>
//                         </div>
//                         <div className="lawfirm-portal-table">
//                             <table className="table">
//                                 <thead>
//                                     <tr><th>Case</th><th>Client</th><th>Type</th><th>Status</th><th>Court</th><th>Assigned On</th><th>Action</th></tr>
//                                 </thead>
//                                 <tbody>
//                                     {assignedCases.map(c => (
//                                         <tr key={c.id}>
//                                             <td><strong>{c.title}</strong><br /><small style={{ color: '#9ca3af' }}>#{c.id}</small></td>
//                                             <td>{c.client_name}<br /><small style={{ color: '#9ca3af' }}>{c.client_email}</small></td>
//                                             <td>{c.case_type || '—'}</td>
//                                             <td><span className={`badge ${getStatusBadgeClass(c.status)}`}>{getStatusText(c.status)}</span></td>
//                                             <td>{c.court_location || '—'}</td>
//                                             <td><small>{formatDate(c.assigned_at || c.created_at)}</small></td>
//                                             <td>
//                                                 <button className="btn-sm btn-outline-primary me-1"
//                                                     onClick={() => {
//                                                         setSelectedChat({ caseId: c.id, caseTitle: c.title, otherPartyId: c.client_id, otherPartyName: c.client_name });
//                                                         loadChatMessages(c.id, c.client_id);
//                                                         setActivePage('messages');
//                                                     }}>
//                                                     <i className="fas fa-comment"></i> Chat
//                                                 </button>
//                                             </td>
//                                         </tr>
//                                     ))}
//                                 </tbody>
//                             </table>
//                             {assignedCases.length === 0 && (
//                                 <div className="lawfirm-portal-no-data">
//                                     <i className="fas fa-briefcase fa-3x" style={{ color: '#d1d5db', marginBottom: 12 }}></i>
//                                     <p>No assigned cases yet</p>
//                                 </div>
//                             )}
//                         </div>
//                     </div>
//                 )}

//                 {/* TEAM MEMBERS */}
//                 {activePage === 'team-members' && (
//                     <div>
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Team Members ({teamMembers.length})</h2>
//                             <button className="lawfirm-portal-btn-primary" onClick={() => setShowAddTeamMemberForm(true)}>
//                                 <i className="fas fa-user-plus"></i> Add Team Member
//                             </button>
//                         </div>

//                         {roleOptions.map(role => {
//                             const group = teamMembers.filter(m => m.role === role.value);
//                             if (group.length === 0) return null;
//                             return (
//                                 <div key={role.value} style={{ marginBottom: 24 }}>
//                                     <h4 style={{ color: '#374151', fontWeight: 600, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
//                                         <span style={{ background: getRoleBadgeColor(role.value), color: 'white', borderRadius: 20, padding: '2px 12px', fontSize: '0.8rem' }}>{role.label}</span>
//                                         <span style={{ fontSize: '0.875rem', color: '#9ca3af' }}>({group.length})</span>
//                                     </h4>
//                                     <div className="lawfirm-portal-table">
//                                         <table className="table">
//                                             <thead>
//                                                 <tr><th>Name</th><th>Email</th><th>Experience (yrs)</th><th>Status</th> </tr>
//                                             </thead>
//                                             <tbody>
//                                                 {group.map(m => (
//                                                     <tr key={m.id}>
//                                                         <td><strong>{m.name}</strong></td>
//                                                         <td>{m.email}</td>
//                                                         <td>{m.experience_years}</td>
//                                                         <td><span style={{ background: '#dcfce7', color: '#166534', borderRadius: 20, padding: '2px 10px', fontSize: '0.75rem' }}>Active</span></td>
//                                                     </tr>
//                                                 ))}
//                                             </tbody>
//                                         </table>
//                                     </div>
//                                 </div>
//                             );
//                         })}
//                         {teamMembers.length === 0 && (
//                             <div className="lawfirm-portal-no-data">
//                                 <i className="fas fa-users fa-3x" style={{ color: '#d1d5db', marginBottom: 12 }}></i>
//                                 <p>No team members added yet. Click "Add Team Member" to get started.</p>
//                             </div>
//                         )}
//                     </div>
//                 )}

//                 {/* COURT UPDATES */}
//                 {activePage === 'court-updates' && (
//                     <div className="lawfirm-portal-court">
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Court & Hearing Updates</h2>
//                         </div>
//                         <div className="lawfirm-portal-court-grid">
//                             <div>
//                                 <h3 style={{ fontWeight: 600, marginBottom: 16, color: '#1a3c8b' }}>
//                                     <i className="fas fa-landmark me-2"></i> Upcoming Hearings
//                                 </h3>
//                                 {courtUpdates.filter(u => u.update_type === 'hearing').length === 0 ? (
//                                     <div style={{ background: '#f9fafb', borderRadius: 10, padding: 24, textAlign: 'center', color: '#9ca3af' }}>
//                                         <i className="fas fa-calendar-alt fa-2x mb-2"></i>
//                                         <p>No upcoming hearings from admin</p>
//                                     </div>
//                                 ) : courtUpdates.filter(u => u.update_type === 'hearing').map(u => (
//                                     <div key={u.id} className="lawfirm-portal-update-item">
//                                         <div className="lawfirm-portal-update-icon" style={{ background: '#dbeafe', color: '#1a3c8b' }}>
//                                             <i className="fas fa-landmark"></i>
//                                         </div>
//                                         <div>
//                                             <h4 style={{ margin: 0, fontWeight: 600 }}>{u.title}</h4>
//                                             <p style={{ margin: '4px 0', color: '#6b7280' }}>{u.court_name}</p>
//                                             <p style={{ margin: '2px 0', fontSize: '0.875rem', color: '#374151' }}>{u.description}</p>
//                                             <small style={{ color: '#9ca3af' }}>{formatDate(u.date)}</small>
//                                             <div style={{ marginTop: 8 }}>
//                                                 <button className="btn-sm btn-outline-primary" onClick={() => forwardToClient(u)}>
//                                                     <i className="fas fa-share me-1"></i> Forward to Client
//                                                 </button>
//                                             </div>
//                                         </div>
//                                     </div>
//                                 ))}
//                             </div>
//                             <div>
//                                 <h3 style={{ fontWeight: 600, marginBottom: 16, color: '#1a3c8b' }}>
//                                     <i className="fas fa-file-alt me-2"></i> Court Orders & Updates
//                                 </h3>
//                                 {courtUpdates.filter(u => u.update_type !== 'hearing').length === 0 ? (
//                                     <div style={{ background: '#f9fafb', borderRadius: 10, padding: 24, textAlign: 'center', color: '#9ca3af' }}>
//                                         <i className="fas fa-file-alt fa-2x mb-2"></i>
//                                         <p>No court orders received from admin yet</p>
//                                         <small>Admin will send court updates for your assigned cases</small>
//                                     </div>
//                                 ) : courtUpdates.filter(u => u.update_type !== 'hearing').map(u => (
//                                     <div key={u.id} className="lawfirm-portal-order-item">
//                                         <div style={{ flex: 1 }}>
//                                             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
//                                                 <h4 style={{ margin: 0, fontWeight: 600 }}>{u.title}</h4>
//                                                 <span style={{ background: u.priority === 'high' ? '#fee2e2' : '#fef9c3', color: u.priority === 'high' ? '#dc2626' : '#ca8a04', borderRadius: 20, padding: '2px 8px', fontSize: '0.75rem' }}>{u.priority || 'Normal'}</span>
//                                             </div>
//                                             <p style={{ margin: '4px 0', color: '#374151', fontSize: '0.875rem' }}>{u.description}</p>
//                                             <small style={{ color: '#9ca3af' }}>Case: {u.case_title} | {formatDate(u.date)}</small>
//                                             <div style={{ marginTop: 8 }}>
//                                                 <button className="btn-sm btn-outline-primary" onClick={() => forwardToClient(u)}>
//                                                     <i className="fas fa-share me-1"></i> Forward to Client
//                                                 </button>
//                                             </div>
//                                         </div>
//                                         <button className="lawfirm-portal-btn-view-sm" style={{ marginLeft: 12 }}>
//                                             <i className="fas fa-download"></i>
//                                         </button>
//                                     </div>
//                                 ))}
//                             </div>
//                         </div>
//                     </div>
//                 )}

//                 {/* MESSAGES */}
//                 {activePage === 'messages' && (
//                     <div className="lawfirm-messages-container">
//                         <div className="lawfirm-conversations-list">
//                             <h4><i className="fas fa-comments me-2"></i>Conversations</h4>
//                             {conversations.length === 0 ? (
//                                 <div className="text-center p-4 text-muted">
//                                     <i className="fas fa-comment-slash fa-3x mb-3"></i>
//                                     <p>No active conversations</p>
//                                     <small>When clients message you, conversations will appear here</small>
//                                 </div>
//                             ) : conversations.map(conv => (
//                                 <div key={conv.case_id}
//                                     className={`lawfirm-conversation-item ${selectedChat?.caseId === conv.case_id ? 'active' : ''}`}
//                                     onClick={() => {
//                                         setSelectedChat({ caseId: conv.case_id, caseTitle: conv.case_title, otherPartyId: conv.other_party_id, otherPartyName: conv.other_party_name });
//                                         loadChatMessages(conv.case_id, conv.other_party_id);
//                                     }}>
//                                     <div className="lawfirm-conversation-avatar">{conv.other_party_name?.charAt(0) || 'C'}</div>
//                                     <div className="lawfirm-conversation-info">
//                                         <div className="lawfirm-conversation-name">{conv.other_party_name}</div>
//                                         <div className="lawfirm-conversation-case">{conv.case_title}</div>
//                                         <div className="lawfirm-conversation-last-msg">{conv.last_message?.substring(0, 50) || 'No messages yet'}</div>
//                                     </div>
//                                     {conv.unread_count > 0 && <div className="lawfirm-conversation-unread">{conv.unread_count}</div>}
//                                 </div>
//                             ))}
//                         </div>
//                         <div className="lawfirm-chat-area">
//                             {!selectedChat ? (
//                                 <div className="lawfirm-chat-placeholder">
//                                     <i className="fas fa-comments fa-4x mb-3 text-muted"></i>
//                                     <h5>Select a Conversation</h5>
//                                     <p>Choose a case from the left to start messaging with the client</p>
//                                 </div>
//                             ) : (
//                                 <>
//                                     <div className="lawfirm-chat-header">
//                                         <div className="lawfirm-chat-header-info">
//                                             <div className="lawfirm-chat-avatar">{selectedChat.otherPartyName?.charAt(0)}</div>
//                                             <div>
//                                                 <h5 className="mb-0">{selectedChat.otherPartyName}</h5>
//                                                 <small className="text-muted">Case: {selectedChat.caseTitle}</small>
//                                             </div>
//                                         </div>
//                                     </div>
//                                     <div className="lawfirm-chat-messages">
//                                         {chatMessages.length === 0 ? (
//                                             <div className="text-center text-muted mt-5">
//                                                 <i className="fas fa-comment-dots fa-3x mb-3"></i>
//                                                 <p>No messages yet. Start the conversation!</p>
//                                             </div>
//                                         ) : chatMessages.map(msg => (
//                                             <div key={msg.id} className={`lawfirm-message ${msg.sender_role === 'lawfirm' ? 'sent' : 'received'}`}>
//                                                 <div className="lawfirm-message-bubble">
//                                                     <p>{msg.content}</p>
//                                                     <small>{formatDate(msg.created_at)}</small>
//                                                 </div>
//                                             </div>
//                                         ))}
//                                         <div ref={chatEndRef} />
//                                     </div>
//                                     <div className="lawfirm-chat-input">
//                                         <input type="text" className="form-control" placeholder="Type your message..."
//                                             value={newMessage} onChange={e => setNewMessage(e.target.value)}
//                                             onKeyPress={e => e.key === 'Enter' && sendMessage()} />
//                                         <button className="btn-advocare" onClick={sendMessage}>
//                                             <i className="fas fa-paper-plane"></i> Send
//                                         </button>
//                                     </div>
//                                 </>
//                             )}
//                         </div>
//                     </div>
//                 )}

//                 {/* FIRM PROFILE - only fields from LawfirmProfile model */}
//                 {activePage === 'profile' && firmData && (
//                     <div className="lawfirm-portal-profile">
//                         {!editingProfile ? (
//                             <>
//                                 <div className="lawfirm-portal-profile-header">
//                                     <div style={{ display: 'flex', alignItems: 'center', gap: 20, flex: 1 }}>
//                                         <div className="lawfirm-portal-profile-avatar">{firmData.firm_name?.charAt(0)}</div>
//                                         <div>
//                                             <h2 style={{ margin: 0 }}>{firmData.firm_name}</h2>
//                                             <p style={{ margin: 0, color: '#6b7280' }}>Registered Law Firm</p>
//                                             <span style={{ background: '#dcfce7', color: '#166534', borderRadius: 20, padding: '2px 12px', fontSize: '0.8rem' }}>
//                                                 <i className="fas fa-check-circle me-1"></i> Verified & Approved
//                                             </span>
//                                         </div>
//                                     </div>
//                                     <button className="lawfirm-portal-btn-primary" onClick={() => setEditingProfile(true)}>
//                                         <i className="fas fa-edit"></i> Edit Profile
//                                     </button>
//                                 </div>

//                                 <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20, marginTop: 24 }}>
//                                     {/* Basic Information */}
//                                     <div className="lawfirm-portal-profile-section">
//                                         <h3><i className="fas fa-info-circle me-2" style={{ color: '#1a3c8b' }}></i>Basic Information</h3>
//                                         <div className="profile-field"><label>Firm Name</label><span>{firmData.firm_name}</span></div>
//                                         <div className="profile-field"><label>Registration Number</label><span>{firmData.registration_no || 'N/A'}</span></div>
//                                         <div className="profile-field"><label>Experience (Years)</label><span>{firmData.experience || 'N/A'}</span></div>
//                                         <div className="profile-field"><label>Specialization</label><span>{firmData.specialization || 'N/A'}</span></div>
//                                     </div>

//                                     {/* Contact Information */}
//                                     <div className="lawfirm-portal-profile-section">
//                                         <h3><i className="fas fa-envelope me-2" style={{ color: '#1a3c8b' }}></i>Contact Information</h3>
//                                         <div className="profile-field"><label>Email</label><span>{firmData.email || 'N/A'}</span></div>
//                                         <div className="profile-field"><label>Phone</label><span>{firmData.phone || 'Not provided'}</span></div>
//                                         <div className="profile-field"><label>Website</label><span>{firmData.website || 'Not provided'}</span></div>
//                                     </div>

//                                     {/* Address */}
//                                     <div className="lawfirm-portal-profile-section">
//                                         <h3><i className="fas fa-map-marker-alt me-2" style={{ color: '#1a3c8b' }}></i>Address</h3>
//                                         <div className="profile-field"><label>Street Address</label><span>{firmData.address || 'Not provided'}</span></div>
//                                         <div className="profile-field"><label>City</label><span>{firmData.city || 'Not provided'}</span></div>
//                                         <div className="profile-field"><label>State</label><span>{firmData.state || 'Not provided'}</span></div>
//                                     </div>

//                                     {/* Primary Lawyer */}
//                                     <div className="lawfirm-portal-profile-section">
//                                         <h3><i className="fas fa-gavel me-2" style={{ color: '#1a3c8b' }}></i>Primary Lawyer</h3>
//                                         <div className="profile-field"><label>Name</label><span>{firmData.primary_lawyer_name || 'N/A'}</span></div>
//                                         <div className="profile-field"><label>Bar Council ID</label><span>{firmData.primary_lawyer_bar_council_id || 'N/A'}</span></div>
//                                         <div className="profile-field"><label>Experience (Years)</label><span>{firmData.primary_lawyer_years_experience || 'N/A'}</span></div>
//                                         <div className="profile-field"><label>Specialization</label><span>{firmData.primary_lawyer_specialization || 'N/A'}</span></div>
//                                     </div>

//                                     {/* Performance */}
//                                     <div className="lawfirm-portal-profile-section">
//                                         <h3><i className="fas fa-chart-bar me-2" style={{ color: '#1a3c8b' }}></i>Performance</h3>
//                                         <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
//                                             <div style={{ background: '#f8fafc', borderRadius: 8, padding: 12, textAlign: 'center' }}>
//                                                 <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1a3c8b' }}>{stats.totalCases}</div>
//                                                 <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Total Cases</div>
//                                             </div>
//                                             <div style={{ background: '#f8fafc', borderRadius: 8, padding: 12, textAlign: 'center' }}>
//                                                 <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1a3c8b' }}>{stats.successRate || 0}%</div>
//                                                 <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Success Rate</div>
//                                             </div>
//                                             <div style={{ background: '#f8fafc', borderRadius: 8, padding: 12, textAlign: 'center' }}>
//                                                 <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1a3c8b' }}>{stats.activeCases}</div>
//                                                 <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Active Cases</div>
//                                             </div>
//                                             <div style={{ background: '#f8fafc', borderRadius: 8, padding: 12, textAlign: 'center' }}>
//                                                 <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1a3c8b' }}>{firmData.rating || '4.5'} ⭐</div>
//                                                 <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Rating</div>
//                                             </div>
//                                         </div>
//                                     </div>
//                                 </div>

//                                 {firmData.bio && (
//                                     <div className="lawfirm-portal-profile-section" style={{ marginTop: 20 }}>
//                                         <h3><i className="fas fa-file-alt me-2" style={{ color: '#1a3c8b' }}></i>About the Firm</h3>
//                                         <p style={{ color: '#374151', lineHeight: 1.7 }}>{firmData.bio}</p>
//                                     </div>
//                                 )}
//                             </>
//                         ) : (
//                             <form onSubmit={handleProfileSave}>
//                                 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
//                                     <h2 style={{ margin: 0 }}>Edit Firm Profile</h2>
//                                     <div style={{ display: 'flex', gap: 12 }}>
//                                         <button type="button" onClick={() => setEditingProfile(false)} style={{ padding: '8px 20px', borderRadius: 8, border: '1px solid #d1d5db', background: 'white', cursor: 'pointer' }}>Cancel</button>
//                                         <button type="submit" className="lawfirm-portal-btn-primary"><i className="fas fa-save me-2"></i>Save Changes</button>
//                                     </div>
//                                 </div>
//                                 <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
//                                     {[
//                                         { label: 'Firm Name', key: 'firm_name', type: 'text' },
//                                         { label: 'Registration Number', key: 'registration_no', type: 'text' },
//                                         { label: 'Phone', key: 'phone', type: 'tel' },
//                                         { label: 'Website', key: 'website', type: 'url' },
//                                         { label: 'City', key: 'city', type: 'text' },
//                                         { label: 'State', key: 'state', type: 'text' },
//                                         { label: 'Primary Lawyer Name', key: 'primary_lawyer_name', type: 'text' },
//                                         { label: 'Bar Council ID', key: 'primary_lawyer_bar_council_id', type: 'text' },
//                                         { label: 'Primary Lawyer Experience (years)', key: 'primary_lawyer_years_experience', type: 'number' },
//                                         { label: 'Primary Lawyer Specialization', key: 'primary_lawyer_specialization', type: 'text' },
//                                         { label: 'Firm Experience (e.g. 3-5)', key: 'experience', type: 'text' },
//                                         { label: 'Specialization (comma-separated)', key: 'specialization', type: 'text' },
//                                     ].map(field => (
//                                         <div key={field.key}>
//                                             <label style={{ fontSize: '0.875rem', fontWeight: 500, color: '#374151', display: 'block', marginBottom: 4 }}>{field.label}</label>
//                                             <input type={field.type} value={profileForm[field.key] || ''} onChange={e => setProfileForm({ ...profileForm, [field.key]: e.target.value })}
//                                                 style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 8, fontSize: '0.875rem', boxSizing: 'border-box' }} />
//                                         </div>
//                                     ))}
//                                     <div style={{ gridColumn: '1/-1' }}>
//                                         <label style={{ fontSize: '0.875rem', fontWeight: 500, color: '#374151', display: 'block', marginBottom: 4 }}>Street Address</label>
//                                         <input type="text" value={profileForm.address || ''} onChange={e => setProfileForm({ ...profileForm, address: e.target.value })}
//                                             style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 8, fontSize: '0.875rem', boxSizing: 'border-box' }} />
//                                     </div>
//                                     <div style={{ gridColumn: '1/-1' }}>
//                                         <label style={{ fontSize: '0.875rem', fontWeight: 500, color: '#374151', display: 'block', marginBottom: 4 }}>About the Firm</label>
//                                         <textarea rows={4} value={profileForm.bio || ''} onChange={e => setProfileForm({ ...profileForm, bio: e.target.value })}
//                                             style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 8, fontSize: '0.875rem', resize: 'vertical', boxSizing: 'border-box' }} />
//                                     </div>
//                                 </div>
//                             </form>
//                         )}
//                     </div>
//                 )}
//             </div>

//             {/* ADD TEAM MEMBER MODAL */}
//             {showAddTeamMemberForm && (
//                 <div className="lawfirm-portal-modal" onClick={() => setShowAddTeamMemberForm(false)}>
//                     <div className="lawfirm-add-lawyer-modal" onClick={e => e.stopPropagation()}>
//                         <div className="lawfirm-portal-modal-header">
//                             <div>
//                                 <h3 style={{ margin: 0 }}>Add Team Member</h3>
//                                 <p style={{ margin: 0, fontSize: '0.8rem', color: '#6b7280' }}>Add a new member to your law firm team</p>
//                             </div>
//                             <button onClick={() => setShowAddTeamMemberForm(false)} style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#6b7280' }}>&times;</button>
//                         </div>
//                         <form onSubmit={handleAddTeamMember} className="lawfirm-add-lawyer-form">
//                             <div className="modal-section">
//                                 <h4 className="modal-section-title"><i className="fas fa-user me-2"></i>Basic Information</h4>
//                                 <div className="modal-grid-2">
//                                     <div><label>Full Name *</label><input type="text" value={newTeamMember.name} onChange={e => setNewTeamMember({ ...newTeamMember, name: e.target.value })} required placeholder="Full name" /></div>
//                                     <div><label>Email Address *</label><input type="email" value={newTeamMember.email} onChange={e => setNewTeamMember({ ...newTeamMember, email: e.target.value })} required placeholder="email@example.com" /></div>
//                                     <div><label>Role *</label>
//                                         <select value={newTeamMember.role} onChange={e => setNewTeamMember({ ...newTeamMember, role: e.target.value })} required>
//                                             {roleOptions.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
//                                         </select>
//                                     </div>
//                                     <div><label>Experience (years) *</label><input type="number" value={newTeamMember.experience_years} onChange={e => setNewTeamMember({ ...newTeamMember, experience_years: e.target.value })} required min="0" max="50" placeholder="Years of experience" /></div>
//                                 </div>
//                             </div>
//                             <div className="lawfirm-portal-modal-footer">
//                                 <button type="button" onClick={() => setShowAddTeamMemberForm(false)}>Cancel</button>
//                                 <button type="submit" style={{ background: '#1a3c8b', color: 'white' }}><i className="fas fa-user-plus me-1"></i> Add Team Member</button>
//                             </div>
//                         </form>
//                     </div>
//                 </div>
//             )}
//         </div>
//     );
// }

// export default LawfirmPortal;

















// import React, { useState, useEffect, useRef, useCallback } from 'react';
// import { useNavigate } from 'react-router-dom';
// import API from '../services/api';
// import Chart from 'chart.js/auto';

// function LawfirmPortal() {
//     const navigate = useNavigate();
//     const [loading, setLoading] = useState(true);
//     const [activePage, setActivePage] = useState('dashboard');
//     const [firmData, setFirmData] = useState(null);
//     const [stats, setStats] = useState({
//         totalCases: 0,
//         activeCases: 0,
//         pendingRequests: 0,
//         successRate: 0
//     });
//     const [caseRequests, setCaseRequests] = useState([]);
//     const [assignedCases, setAssignedCases] = useState([]);
//     const [lawyers, setLawyers] = useState([]);
//     const [courtUpdates, setCourtUpdates] = useState([]);
    
//     // Chat states
//     const [conversations, setConversations] = useState([]);
//     const [selectedChat, setSelectedChat] = useState(null);
//     const [chatMessages, setChatMessages] = useState([]);
//     const [newMessage, setNewMessage] = useState("");
    
//     const [showAddLawyerForm, setShowAddLawyerForm] = useState(false);
//     const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
//     const [newLawyer, setNewLawyer] = useState({
//         name: '',
//         email: '',
//         phone: '',
//         experience: '',
//         expertise: [],
//         bar_number: ''
//     });
    
//     const chartRef = useRef(null);
//     let chartInstance = null;
//     const chatPollInterval = useRef(null);
//     const chatEndRef = useRef(null);

//     const expertiseOptions = [
//         'Civil Law', 'Criminal Law', 'Corporate Law', 'Family Law',
//         'Property Law', 'Tax Law', 'Intellectual Property', 'Labor Law'
//     ];

//     // Load conversations for chat
//     const loadConversations = useCallback(async () => {
//         try {
//             const res = await API.get('chat/conversations/');
//             setConversations(res.data);
//         } catch (err) {
//             console.error("Failed to load conversations:", err);
//         }
//     }, []);

//     // Load chat messages
//     const loadChatMessages = async (caseId, otherPartyId) => {
//         try {
//             const res = await API.get(`chat/${caseId}/${otherPartyId}/`);
//             setChatMessages(res.data);
//         } catch (err) {
//             console.error("Failed to load messages:", err);
//         }
//     };

//     // Send message
//     const sendMessage = async () => {
//         if (!newMessage.trim() || !selectedChat) return;
//         const msg = newMessage;
//         setNewMessage("");
//         try {
//             await API.post("chat/send/", {
//                 case_id: selectedChat.caseId,
//                 receiver_id: selectedChat.otherPartyId,
//                 content: msg,
//             });
//             await loadChatMessages(selectedChat.caseId, selectedChat.otherPartyId);
//             await loadConversations();
//         } catch (err) {
//             console.error("Failed to send message:", err);
//             alert("Failed to send message");
//             setNewMessage(msg);
//         }
//     };

//     // Accept case request
//     const handleAcceptRequest = async (caseId) => {
//         try {
//             await API.post(`cases/${caseId}/accept/`);
//             alert('Case request accepted successfully!');
//             await loadPendingRequests();
//             await loadAssignedCases();
//             await loadConversations();
//         } catch (error) {
//             console.error('Error accepting request:', error);
//             alert('Failed to accept request');
//         }
//     };

//     // Reject case request
//     const handleRejectRequest = async (caseId) => {
//         if (!window.confirm('Are you sure you want to reject this case?')) return;
//         try {
//             await API.post(`cases/${caseId}/reject/`);
//             alert('Case request rejected');
//             await loadPendingRequests();
//             await loadConversations();
//         } catch (error) {
//             console.error('Error rejecting request:', error);
//             alert('Failed to reject request');
//         }
//     };

//     // Load pending requests
//     const loadPendingRequests = async () => {
//         try {
//             const res = await API.get('cases/pending-requests/');
//             setCaseRequests(res.data || []);
//         } catch (err) {
//             console.error('Pending requests error:', err);
//         }
//     };

//     // Load assigned cases
//     const loadAssignedCases = async () => {
//         try {
//             const res = await API.get('cases/assigned-cases/');
//             setAssignedCases(res.data || []);
//         } catch (err) {
//             console.error('Assigned cases error:', err);
//         }
//     };

//     // Add lawyer
//     const handleAddLawyer = async (e) => {
//         e.preventDefault();
//         try {
//             await API.post('profiles/add-lawyer/', newLawyer);
//             const lawyersRes = await API.get('profiles/lawfirm-lawyers/');
//             setLawyers(lawyersRes.data);
//             setShowAddLawyerForm(false);
//             setNewLawyer({ name: '', email: '', phone: '', experience: '', expertise: [], bar_number: '' });
//             alert('Lawyer added successfully!');
//         } catch (error) {
//             console.error('Error adding lawyer:', error);
//             alert('Failed to add lawyer');
//         }
//     };

//     // Initialize chart
//     const initChart = () => {
//         const ctx = chartRef.current.getContext('2d');
//         chartInstance = new Chart(ctx, {
//             type: 'bar',
//             data: {
//                 labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
//                 datasets: [
//                     {
//                         label: 'New Cases',
//                         data: [12, 19, 8, 15, 12, 17, 10, 14, 16, 12, 10, 15],
//                         backgroundColor: 'rgba(26, 60, 139, 0.7)',
//                         borderColor: 'rgba(26, 60, 139, 1)',
//                         borderWidth: 1
//                     },
//                     {
//                         label: 'Closed Cases',
//                         data: [8, 12, 6, 10, 9, 13, 7, 11, 12, 9, 8, 11],
//                         backgroundColor: 'rgba(212, 175, 55, 0.7)',
//                         borderColor: 'rgba(212, 175, 55, 1)',
//                         borderWidth: 1
//                     }
//                 ]
//             },
//             options: {
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 scales: { y: { beginAtZero: true } }
//             }
//         });
//     };

//     // Handle logout
//     const handleLogout = () => {
//         localStorage.clear();
//         navigate('/');
//     };

//     // Format date
//     const formatDate = (dateString) => {
//         if (!dateString) return 'N/A';
//         try {
//             return new Date(dateString).toLocaleDateString('en-US', {
//                 year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
//             });
//         } catch {
//             return 'Invalid date';
//         }
//     };

//     // Get status badge class
//     const getStatusBadgeClass = (status) => {
//         switch(status) {
//             case 'pending': return 'status-pending';
//             case 'in_progress': return 'status-in-court';
//             case 'assigned': return 'status-assigned';
//             case 'resolved': return 'status-closed';
//             case 'closed': return 'status-closed';
//             default: return 'status-pending';
//         }
//     };

//     const getStatusText = (status) => {
//         switch(status) {
//             case 'pending': return 'Pending';
//             case 'assigned': return 'Assigned';
//             case 'in_progress': return 'In Progress';
//             case 'resolved': return 'Resolved';
//             case 'closed': return 'Closed';
//             default: return status;
//         }
//     };

//     // Load dashboard data
//     useEffect(() => {
//         const loadDashboard = async () => {
//             try {
//                 const token = localStorage.getItem('access_token');
//                 if (!token) {
//                     navigate('/');
//                     return;
//                 }

//                 // Load profile
//                 try {
//                     const profileRes = await API.get('profiles/lawfirm-dashboard/');
//                     if (profileRes.data.status === 'approved') {
//                         setFirmData(profileRes.data);
//                     } else if (profileRes.data.status === 'pending') {
//                         navigate('/lawfirm-pending-onboarding');
//                         return;
//                     } else {
//                         navigate('/lawfirm-onboarding');
//                         return;
//                     }
//                 } catch (err) {
//                     console.error('Profile error:', err);
//                 }

//                 // Load stats
//                 try {
//                     const statsRes = await API.get('cases/lawfirm-stats/');
//                     setStats(statsRes.data);
//                 } catch (e) { console.error('Stats error:', e); }

//                 // Load data
//                 await loadPendingRequests();
//                 await loadAssignedCases();
//                 await loadConversations();

//                 // Load lawyers
//                 try {
//                     const lawyersRes = await API.get('profiles/lawfirm-lawyers/');
//                     setLawyers(lawyersRes.data || []);
//                 } catch (e) { console.error('Lawyers error:', e); }

//                 // Load court updates
//                 try {
//                     const updatesRes = await API.get('cases/court-updates/');
//                     setCourtUpdates(updatesRes.data || []);
//                 } catch (e) { console.error('Court updates error:', e); }

//             } catch (error) {
//                 console.error('Error loading dashboard:', error);
//                 if (error.response?.status === 401) {
//                     localStorage.clear();
//                     navigate('/');
//                 }
//             } finally {
//                 setLoading(false);
//             }
//         };
//         loadDashboard();
//     }, [navigate]);

//     // Chart effect
//     useEffect(() => {
//         if (activePage === 'dashboard' && chartRef.current && !chartInstance) {
//             initChart();
//         }
//         return () => {
//             if (chartInstance) {
//                 chartInstance.destroy();
//                 chartInstance = null;
//             }
//         };
//     }, [activePage]);

//     // Chat polling effect
//     useEffect(() => {
//         if (chatPollInterval.current) clearInterval(chatPollInterval.current);
//         if (selectedChat && activePage === 'messages') {
//             chatPollInterval.current = setInterval(() => {
//                 loadChatMessages(selectedChat.caseId, selectedChat.otherPartyId);
//             }, 3000);
//         }
//         return () => {
//             if (chatPollInterval.current) clearInterval(chatPollInterval.current);
//         };
//     }, [selectedChat, activePage]);

//     // Auto-scroll effect
//     useEffect(() => {
//         if (chatEndRef.current) chatEndRef.current.scrollIntoView({ behavior: "smooth" });
//     }, [chatMessages]);

//     if (loading) {
//         return (
//             <div className="lawfirm-loading-container">
//                 <div className="lawfirm-loading-card">
//                     <div className="lawfirm-spinner"></div>
//                     <h2>Loading Dashboard...</h2>
//                 </div>
//             </div>
//         );
//     }

//     const unreadCount = conversations.reduce((sum, c) => sum + (c.unread_count || 0), 0);

//     return (
//         <div className="lawfirm-portal-wrapper">
//             {/* Sidebar */}
//             <div className={`lawfirm-portal-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
//                 <div className="lawfirm-portal-logo">
//                     <div className="lawfirm-portal-logo-icon">
//                         <i className="fas fa-balance-scale"></i>
//                     </div>
//                     <div className="lawfirm-portal-logo-text">Advocare</div>
//                 </div>
                
//                 <div className="lawfirm-portal-nav">
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'dashboard' ? 'active' : ''}`} onClick={() => setActivePage('dashboard')}>
//                         <i className="fas fa-tachometer-alt"></i>
//                         <span>Dashboard</span>
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'case-requests' ? 'active' : ''}`} onClick={() => { setActivePage('case-requests'); loadPendingRequests(); }}>
//                         <i className="fas fa-file-contract"></i>
//                         <span>Case Requests</span>
//                         {caseRequests.length > 0 && <span className="lawfirm-portal-badge">{caseRequests.length}</span>}
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'assigned-cases' ? 'active' : ''}`} onClick={() => { setActivePage('assigned-cases'); loadAssignedCases(); }}>
//                         <i className="fas fa-briefcase"></i>
//                         <span>Assigned Cases</span>
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'lawyers' ? 'active' : ''}`} onClick={() => setActivePage('lawyers')}>
//                         <i className="fas fa-user-tie"></i>
//                         <span>Lawyers</span>
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'court-updates' ? 'active' : ''}`} onClick={() => setActivePage('court-updates')}>
//                         <i className="fas fa-gavel"></i>
//                         <span>Court Updates</span>
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'messages' ? 'active' : ''}`} onClick={() => setActivePage('messages')}>
//                         <i className="fas fa-comments"></i>
//                         <span>Messages</span>
//                         {unreadCount > 0 && <span className="lawfirm-portal-badge">{unreadCount}</span>}
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'profile' ? 'active' : ''}`} onClick={() => setActivePage('profile')}>
//                         <i className="fas fa-building"></i>
//                         <span>Firm Profile</span>
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'settings' ? 'active' : ''}`} onClick={() => setActivePage('settings')}>
//                         <i className="fas fa-cog"></i>
//                         <span>Settings</span>
//                     </div>
//                 </div>
                
//                 <div className="lawfirm-portal-user">
//                     <div className="lawfirm-portal-avatar">{firmData?.firm_name?.charAt(0) || 'F'}</div>
//                     <div className="lawfirm-portal-user-info">
//                         <h4>{firmData?.firm_name || 'Law Firm'}</h4>
//                         <p>Law Firm Admin</p>
//                     </div>
//                 </div>
//             </div>
            
//             {/* Main Content */}
//             <div className="lawfirm-portal-main">
//                 <div className="lawfirm-portal-header">
//                     <div className="lawfirm-portal-title">
//                         <button className="lawfirm-portal-toggle" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
//                             <i className="fas fa-bars"></i>
//                         </button>
//                         <i className="fas fa-tachometer-alt"></i>
//                         <span>
//                             {activePage === 'dashboard' ? 'Law Firm Dashboard' :
//                              activePage === 'case-requests' ? 'Case Requests' :
//                              activePage === 'assigned-cases' ? 'Assigned Cases' :
//                              activePage === 'lawyers' ? 'Lawyers Management' :
//                              activePage === 'court-updates' ? 'Court & Hearing Updates' :
//                              activePage === 'messages' ? 'Messages' :
//                              activePage === 'profile' ? 'Firm Profile' : 'Settings'}
//                         </span>
//                     </div>
//                     <div className="lawfirm-portal-actions">
//                         <div className="lawfirm-portal-search">
//                             <i className="fas fa-search"></i>
//                             <input type="text" placeholder="Search..." />
//                         </div>
//                         <div className="lawfirm-portal-notification">
//                             <i className="fas fa-bell"></i>
//                             <span className="lawfirm-portal-dot"></span>
//                         </div>
//                         <button className="lawfirm-portal-logout" onClick={handleLogout}>
//                             <i className="fas fa-sign-out-alt"></i> Logout
//                         </button>
//                     </div>
//                 </div>

//                 {/* Dashboard Page */}
//                 {activePage === 'dashboard' && (
//                     <div className="lawfirm-portal-dashboard">
//                         <div className="lawfirm-portal-kpi">
//                             <div className="lawfirm-portal-kpi-card">
//                                 <div className="lawfirm-portal-kpi-icon"><i className="fas fa-folder-open"></i></div>
//                                 <div><h3>{stats.totalCases}</h3><p>Total Cases</p></div>
//                             </div>
//                             <div className="lawfirm-portal-kpi-card">
//                                 <div className="lawfirm-portal-kpi-icon"><i className="fas fa-gavel"></i></div>
//                                 <div><h3>{stats.activeCases}</h3><p>Active Cases</p></div>
//                             </div>
//                             <div className="lawfirm-portal-kpi-card">
//                                 <div className="lawfirm-portal-kpi-icon"><i className="fas fa-clock"></i></div>
//                                 <div><h3>{stats.pendingRequests}</h3><p>Pending Requests</p></div>
//                             </div>
//                             <div className="lawfirm-portal-kpi-card">
//                                 <div className="lawfirm-portal-kpi-icon"><i className="fas fa-chart-line"></i></div>
//                                 <div><h3>{stats.successRate}%</h3><p>Success Rate</p></div>
//                             </div>
//                         </div>

//                         <div className="lawfirm-portal-stats">
//                             <div className="lawfirm-portal-chart">
//                                 <div className="lawfirm-portal-section-title">
//                                     <span>Case Statistics</span>
//                                     <select><option>Last 30 Days</option><option>Last 3 Months</option></select>
//                                 </div>
//                                 <canvas ref={chartRef}></canvas>
//                             </div>
//                             <div className="lawfirm-portal-activity">
//                                 <div className="lawfirm-portal-section-title">
//                                     <span>Recent Activity</span>
//                                     <button onClick={() => setActivePage('assigned-cases')}>View All</button>
//                                 </div>
//                                 {assignedCases.slice(0, 3).map(c => (
//                                     <div key={c.id} className="lawfirm-portal-activity-item">
//                                         <div className="lawfirm-portal-activity-icon"><i className="fas fa-landmark"></i></div>
//                                         <div><h4>{c.title}</h4><p>Status: {getStatusText(c.status)}</p><small>{formatDate(c.updated_at)}</small></div>
//                                     </div>
//                                 ))}
//                             </div>
//                         </div>

//                         <div className="lawfirm-portal-actions-grid">
//                             <button className="lawfirm-portal-action-card" onClick={() => setActivePage('case-requests')}>
//                                 <i className="fas fa-file-contract"></i><span>View Case Requests</span>
//                             </button>
//                             <button className="lawfirm-portal-action-card" onClick={() => setShowAddLawyerForm(true)}>
//                                 <i className="fas fa-user-plus"></i><span>Add Lawyer</span>
//                             </button>
//                             <button className="lawfirm-portal-action-card" onClick={() => setActivePage('court-updates')}>
//                                 <i className="fas fa-upload"></i><span>Upload Update</span>
//                             </button>
//                             <button className="lawfirm-portal-action-card" onClick={() => setActivePage('messages')}>
//                                 <i className="fas fa-comment-medical"></i><span>New Message</span>
//                             </button>
//                         </div>
//                     </div>
//                 )}

//                 {/* Case Requests Page */}
//                 {activePage === 'case-requests' && (
//                     <div>
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Case Requests ({caseRequests.length})</h2>
//                         </div>
//                         <div className="lawfirm-portal-requests-grid">
//                             {caseRequests.map(req => (
//                                 <div key={req.id} className="lawfirm-portal-request-card">
//                                     <div><h3>{req.title}</h3><span className="lawfirm-portal-case-type">{req.case_type}</span></div>
//                                     <p className="lawfirm-portal-case-desc">{req.description?.substring(0, 150)}...</p>
//                                     <div className="lawfirm-portal-client">
//                                         <div className="lawfirm-portal-client-avatar">{req.client_name?.charAt(0)}</div>
//                                         <div><h4>{req.client_name}</h4><p>{req.client_email}</p></div>
//                                     </div>
//                                     <div className="lawfirm-portal-request-actions">
//                                         <button className="lawfirm-portal-btn-accept" onClick={() => handleAcceptRequest(req.id)}>Accept</button>
//                                         <button className="lawfirm-portal-btn-reject" onClick={() => handleRejectRequest(req.id)}>Reject</button>
//                                         <button className="lawfirm-portal-btn-view">View Details</button>
//                                     </div>
//                                 </div>
//                             ))}
//                             {caseRequests.length === 0 && <div className="lawfirm-portal-no-data">No pending case requests</div>}
//                         </div>
//                     </div>
//                 )}

//                 {/* Assigned Cases Page */}
//                 {activePage === 'assigned-cases' && (
//                     <div>
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Assigned Cases ({assignedCases.length})</h2>
//                         </div>
//                         <div className="lawfirm-portal-table">
//                             <table className="table">
//                                 <thead>
//                                     <tr><th>Case</th><th>Client</th><th>Status</th><th>Court</th><th>Action</th></tr>
//                                 </thead>
//                                 <tbody>
//                                     {assignedCases.map(c => (
//                                         <tr key={c.id}>
//                                             <td><strong>{c.title}</strong><br/><small>#{c.id}</small></td>
//                                             <td>{c.client_name}</td>
//                                             <td><span className={`badge ${getStatusBadgeClass(c.status)}`}>{getStatusText(c.status)}</span></td>
//                                             <td>{c.court_location || '—'}</td>
//                                             <td>
//                                                 <button className="btn-sm btn-outline-primary me-1" 
//                                                     onClick={() => {
//                                                         setSelectedChat({
//                                                             caseId: c.id,
//                                                             caseTitle: c.title,
//                                                             otherPartyId: c.client_id,
//                                                             otherPartyName: c.client_name,
//                                                         });
//                                                         loadChatMessages(c.id, c.client_id);
//                                                         setActivePage('messages');
//                                                     }}>
//                                                     <i className="fas fa-comment"></i> Chat
//                                                 </button>
//                                                 <button className="btn-sm btn-outline-secondary">Update</button>
//                                             </td>
//                                         </tr>
//                                     ))}
//                                 </tbody>
//                             </table>
//                         </div>
//                     </div>
//                 )}

//                 {/* Lawyers Page */}
//                 {activePage === 'lawyers' && (
//                     <div>
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Lawyers Management</h2>
//                             <button className="lawfirm-portal-btn-primary" onClick={() => setShowAddLawyerForm(true)}>+ Add Lawyer</button>
//                         </div>
//                         <div className="lawfirm-portal-table">
//                             <table className="table">
//                                 <thead>
//                                     <tr><th>Name</th><th>Practice Area</th><th>Experience</th><th>Contact</th><th>Action</th></tr>
//                                 </thead>
//                                 <tbody>
//                                     {lawyers.map(l => (
//                                         <tr key={l.id}>
//                                             <td><div className="lawfirm-portal-lawyer"><span className="lawfirm-portal-lawyer-avatar">{l.name?.charAt(0)}</span>{l.name}</div></td>
//                                             <td>{l.expertise?.join(', ') || '—'}</td>
//                                             <td>{l.experience} years</td>
//                                             <td>{l.email}<br/>{l.phone}</td>
//                                             <td><button className="lawfirm-portal-btn-view-sm">Assign Case</button></td>
//                                         </tr>
//                                     ))}
//                                 </tbody>
//                             </table>
//                         </div>
//                     </div>
//                 )}

//                 {/* Court Updates Page */}
//                 {activePage === 'court-updates' && (
//                     <div className="lawfirm-portal-court">
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Court & Hearing Updates</h2>
//                             <button className="lawfirm-portal-btn-primary">+ Add Update</button>
//                         </div>
//                         <div className="lawfirm-portal-court-grid">
//                             <div>
//                                 <h3>Upcoming Hearings</h3>
//                                 {courtUpdates.filter(u => u.type === 'hearing').map(u => (
//                                     <div key={u.id} className="lawfirm-portal-update-item">
//                                         <div className="lawfirm-portal-update-icon"><i className="fas fa-landmark"></i></div>
//                                         <div><h4>{u.title}</h4><p>{u.court_name}</p><small>{formatDate(u.date)}</small></div>
//                                     </div>
//                                 ))}
//                             </div>
//                             <div>
//                                 <h3>Recent Orders</h3>
//                                 {courtUpdates.filter(u => u.type === 'order').map(u => (
//                                     <div key={u.id} className="lawfirm-portal-order-item">
//                                         <div><h4>{u.title}</h4><p>{u.description}</p><small>{formatDate(u.date)}</small></div>
//                                         <button className="lawfirm-portal-btn-view-sm"><i className="fas fa-download"></i></button>
//                                     </div>
//                                 ))}
//                             </div>
//                         </div>
//                     </div>
//                 )}

//                 {/* Messages Page - Updated with full chat functionality */}
//                 {activePage === 'messages' && (
//                     <div className="lawfirm-messages-container">
//                         <div className="lawfirm-conversations-list">
//                             <h4><i className="fas fa-comments me-2"></i>Conversations</h4>
//                             {conversations.length === 0 ? (
//                                 <div className="text-center p-4 text-muted">
//                                     <i className="fas fa-comment-slash fa-3x mb-3"></i>
//                                     <p>No active conversations</p>
//                                     <small>When clients message you, conversations will appear here</small>
//                                 </div>
//                             ) : (
//                                 conversations.map(conv => (
//                                     <div 
//                                         key={conv.case_id} 
//                                         className={`lawfirm-conversation-item ${selectedChat?.caseId === conv.case_id ? 'active' : ''}`} 
//                                         onClick={() => {
//                                             setSelectedChat({
//                                                 caseId: conv.case_id,
//                                                 caseTitle: conv.case_title,
//                                                 otherPartyId: conv.other_party_id,
//                                                 otherPartyName: conv.other_party_name,
//                                             });
//                                             loadChatMessages(conv.case_id, conv.other_party_id);
//                                         }}
//                                     >
//                                         <div className="lawfirm-conversation-avatar">{conv.other_party_name?.charAt(0) || 'C'}</div>
//                                         <div className="lawfirm-conversation-info">
//                                             <div className="lawfirm-conversation-name">{conv.other_party_name}</div>
//                                             <div className="lawfirm-conversation-case">{conv.case_title}</div>
//                                             <div className="lawfirm-conversation-last-msg">{conv.last_message?.substring(0, 50) || 'No messages yet'}</div>
//                                         </div>
//                                         {conv.unread_count > 0 && <div className="lawfirm-conversation-unread">{conv.unread_count}</div>}
//                                     </div>
//                                 ))
//                             )}
//                         </div>

//                         <div className="lawfirm-chat-area">
//                             {!selectedChat ? (
//                                 <div className="lawfirm-chat-placeholder">
//                                     <i className="fas fa-comments fa-4x mb-3 text-muted"></i>
//                                     <h5>Select a Conversation</h5>
//                                     <p>Choose a case from the left to start messaging with the client</p>
//                                 </div>
//                             ) : (
//                                 <>
//                                     <div className="lawfirm-chat-header">
//                                         <div className="lawfirm-chat-header-info">
//                                             <div className="lawfirm-chat-avatar">{selectedChat.otherPartyName?.charAt(0)}</div>
//                                             <div>
//                                                 <h5 className="mb-0">{selectedChat.otherPartyName}</h5>
//                                                 <small className="text-muted">Case: {selectedChat.caseTitle}</small>
//                                             </div>
//                                         </div>
//                                     </div>
//                                     <div className="lawfirm-chat-messages">
//                                         {chatMessages.length === 0 ? (
//                                             <div className="text-center text-muted mt-5">
//                                                 <i className="fas fa-comment-dots fa-3x mb-3"></i>
//                                                 <p>No messages yet. Start the conversation!</p>
//                                             </div>
//                                         ) : (
//                                             chatMessages.map(msg => (
//                                                 <div key={msg.id} className={`lawfirm-message ${msg.sender_role === 'lawfirm' ? 'sent' : 'received'}`}>
//                                                     <div className="lawfirm-message-bubble">
//                                                         <p>{msg.content}</p>
//                                                         <small>{formatDate(msg.created_at)}</small>
//                                                     </div>
//                                                 </div>
//                                             ))
//                                         )}
//                                         <div ref={chatEndRef} />
//                                     </div>
//                                     <div className="lawfirm-chat-input">
//                                         <input 
//                                             type="text" 
//                                             className="form-control" 
//                                             placeholder="Type your message..." 
//                                             value={newMessage} 
//                                             onChange={e => setNewMessage(e.target.value)} 
//                                             onKeyPress={e => e.key === 'Enter' && sendMessage()} 
//                                         />
//                                         <button className="btn-advocare" onClick={sendMessage}>
//                                             <i className="fas fa-paper-plane"></i> Send
//                                         </button>
//                                     </div>
//                                 </>
//                             )}
//                         </div>
//                     </div>
//                 )}

//                 {/* Profile Page */}
//                 {activePage === 'profile' && firmData && (
//                     <div className="lawfirm-portal-profile">
//                         <div className="lawfirm-portal-profile-header">
//                             <div className="lawfirm-portal-profile-avatar">{firmData.firm_name?.charAt(0)}</div>
//                             <div><h2>{firmData.firm_name}</h2><p>Registered Law Firm</p></div>
//                         </div>
//                         <div className="lawfirm-portal-profile-section">
//                             <h3>Contact Information</h3>
//                             <p><strong>Email:</strong> {firmData.email}</p>
//                             <p><strong>Phone:</strong> {firmData.phone || 'Not provided'}</p>
//                             <p><strong>Address:</strong> {firmData.address || 'Not provided'}</p>
//                         </div>
//                         <div className="lawfirm-portal-profile-section">
//                             <h3>Practice Areas</h3>
//                             <div className="lawfirm-portal-tags">
//                                 {firmData.specialization?.split(',').map((a, i) => <span key={i}>{a.trim()}</span>) || 'General Practice'}
//                             </div>
//                         </div>
//                         <div className="lawfirm-portal-profile-stats">
//                             <div><h3>Total Cases</h3><div className="lawfirm-portal-stat-value">{stats.totalCases}</div></div>
//                             <div><h3>Success Rate</h3><div className="lawfirm-portal-stat-value">{stats.successRate}%</div></div>
//                             <div><h3>Rating</h3><div className="lawfirm-portal-stat-value">{firmData.rating || '4.5'}</div></div>
//                         </div>
//                     </div>
//                 )}

//                 {/* Settings Page */}
//                 {activePage === 'settings' && (
//                     <div className="lawfirm-portal-settings">
//                         <h3>Change Password</h3>
//                         <form>
//                             <div className="mb-3">
//                                 <label>Current Password</label>
//                                 <input type="password" className="form-control" />
//                             </div>
//                             <div className="mb-3">
//                                 <label>New Password</label>
//                                 <input type="password" className="form-control" />
//                             </div>
//                             <div className="mb-3">
//                                 <label>Confirm Password</label>
//                                 <input type="password" className="form-control" />
//                             </div>
//                             <button className="lawfirm-portal-btn-primary">Update Password</button>
//                         </form>
//                     </div>
//                 )}
//             </div>

//             {/* Add Lawyer Modal */}
//             {showAddLawyerForm && (
//                 <div className="lawfirm-portal-modal" onClick={() => setShowAddLawyerForm(false)}>
//                     <div className="lawfirm-portal-modal-content" onClick={e => e.stopPropagation()}>
//                         <div className="lawfirm-portal-modal-header">
//                             <h3>Add New Lawyer</h3>
//                             <button onClick={() => setShowAddLawyerForm(false)}>&times;</button>
//                         </div>
//                         <form onSubmit={handleAddLawyer}>
//                             <div className="lawfirm-portal-form-row">
//                                 <div><label>Full Name</label><input type="text" value={newLawyer.name} onChange={e => setNewLawyer({...newLawyer, name: e.target.value})} required /></div>
//                                 <div><label>Email</label><input type="email" value={newLawyer.email} onChange={e => setNewLawyer({...newLawyer, email: e.target.value})} required /></div>
//                             </div>
//                             <div className="lawfirm-portal-form-row">
//                                 <div><label>Phone</label><input type="tel" value={newLawyer.phone} onChange={e => setNewLawyer({...newLawyer, phone: e.target.value})} /></div>
//                                 <div><label>Experience (Years)</label><input type="number" value={newLawyer.experience} onChange={e => setNewLawyer({...newLawyer, experience: e.target.value})} /></div>
//                             </div>
//                             <div className="mb-3">
//                                 <label>Practice Area</label>
//                                 <select className="form-control" multiple value={newLawyer.expertise} onChange={e => setNewLawyer({...newLawyer, expertise: Array.from(e.target.selectedOptions, o => o.value)})}>
//                                     {expertiseOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
//                                 </select>
//                                 <small className="text-muted">Hold Ctrl to select multiple</small>
//                             </div>
//                             <div className="mb-3">
//                                 <label>Bar Registration No.</label>
//                                 <input type="text" className="form-control" value={newLawyer.bar_number} onChange={e => setNewLawyer({...newLawyer, bar_number: e.target.value})} />
//                             </div>
//                             <div className="lawfirm-portal-modal-footer">
//                                 <button type="button" onClick={() => setShowAddLawyerForm(false)}>Cancel</button>
//                                 <button type="submit">Add Lawyer</button>
//                             </div>
//                         </form>
//                     </div>
//                 </div>
//             )}

//             {/* Chat Styles */}
//             <style>{`
//                 .lawfirm-messages-container { display: flex; gap: 20px; height: calc(100vh - 150px); }
//                 .lawfirm-conversations-list { width: 320px; background: white; border-radius: 12px; overflow-y: auto; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
//                 .lawfirm-conversations-list h4 { padding: 15px 20px; margin: 0; border-bottom: 1px solid #e9ecef; }
//                 .lawfirm-conversation-item { display: flex; align-items: center; padding: 12px 20px; cursor: pointer; border-bottom: 1px solid #f0f0f0; transition: all 0.2s; }
//                 .lawfirm-conversation-item:hover { background: #f8f9fa; }
//                 .lawfirm-conversation-item.active { background: #e3f2fd; border-left: 3px solid var(--primary); }
//                 .lawfirm-conversation-avatar { width: 48px; height: 48px; border-radius: 50%; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 12px; flex-shrink: 0; }
//                 .lawfirm-conversation-info { flex: 1; min-width: 0; }
//                 .lawfirm-conversation-name { font-weight: 600; color: var(--primary); }
//                 .lawfirm-conversation-case { font-size: 12px; color: #6c757d; }
//                 .lawfirm-conversation-last-msg { font-size: 12px; color: #999; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
//                 .lawfirm-conversation-unread { background: #dc3545; color: white; border-radius: 12px; padding: 2px 8px; font-size: 11px; font-weight: bold; }
//                 .lawfirm-chat-area { flex: 1; background: white; border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
//                 .lawfirm-chat-header { padding: 15px 20px; border-bottom: 1px solid #e9ecef; background: #f8f9fa; }
//                 .lawfirm-chat-header-info { display: flex; align-items: center; gap: 12px; }
//                 .lawfirm-chat-avatar { width: 40px; height: 40px; border-radius: 50%; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; }
//                 .lawfirm-chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
//                 .lawfirm-message { display: flex; }
//                 .lawfirm-message.sent { justify-content: flex-end; }
//                 .lawfirm-message.received { justify-content: flex-start; }
//                 .lawfirm-message-bubble { max-width: 70%; padding: 10px 15px; border-radius: 18px; }
//                 .lawfirm-message.sent .lawfirm-message-bubble { background: var(--primary); color: white; border-radius: 18px 18px 4px 18px; }
//                 .lawfirm-message.received .lawfirm-message-bubble { background: #f1f1f1; color: #333; border-radius: 18px 18px 18px 4px; }
//                 .lawfirm-message-bubble small { font-size: 10px; opacity: 0.7; display: block; margin-top: 4px; }
//                 .lawfirm-chat-input { padding: 15px 20px; border-top: 1px solid #e9ecef; display: flex; gap: 10px; }
//                 .lawfirm-chat-input input { flex: 1; }
//                 .lawfirm-chat-placeholder { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #6c757d; }
//                 .badge.status-pending { background: #ffc107; color: #856404; }
//                 .badge.status-assigned { background: #17a2b8; color: white; }
//                 .badge.status-in-court { background: #2d5bb5; color: white; }
//                 .badge.status-closed { background: #28a745; color: white; }
//                 .btn-advocare { background: var(--primary); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
//                 .btn-advocare:hover { opacity: 0.9; }
//             `}</style>
//         </div>
//     );
// }

// export default LawfirmPortal;


















// import React, { useState, useEffect, useRef } from 'react';
// import { useNavigate } from 'react-router-dom';
// import API from '../services/api';
// import Chart from 'chart.js/auto';

// function LawfirmPortal() {
//     const navigate = useNavigate();
//     const [loading, setLoading] = useState(true);
//     const [activePage, setActivePage] = useState('dashboard');
//     const [firmData, setFirmData] = useState(null);
//     const [stats, setStats] = useState({
//         totalCases: 0,
//         activeCases: 0,
//         pendingRequests: 0,
//         successRate: 0
//     });
//     const [caseRequests, setCaseRequests] = useState([]);
//     const [assignedCases, setAssignedCases] = useState([]);
//     const [lawyers, setLawyers] = useState([]);
//     const [courtUpdates, setCourtUpdates] = useState([]);
//     const [messages, setMessages] = useState([]);
//     const [showAddLawyerForm, setShowAddLawyerForm] = useState(false);
//     const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
//     const [activeTab, setActiveTab] = useState('client-chats');
//     const [newLawyer, setNewLawyer] = useState({
//         name: '',
//         email: '',
//         phone: '',
//         experience: '',
//         expertise: [],
//         bar_number: ''
//     });
//     const chartRef = useRef(null);
//     let chartInstance = null;

//     const expertiseOptions = [
//         'Civil Law', 'Criminal Law', 'Corporate Law', 'Family Law',
//         'Property Law', 'Tax Law', 'Intellectual Property', 'Labor Law'
//     ];

//     const roleOptions = [
//         { value: 'associate', label: 'Associate' },
//         { value: 'partner', label: 'Partner' },
//         { value: 'senior_advocate', label: 'Senior Advocate' }
//     ];

//     useEffect(() => {
//         const loadDashboard = async () => {
//             try {
//                 const token = localStorage.getItem('access_token');
//                 if (!token) {
//                     navigate('/');
//                     return;
//                 }

//                 const profileRes = await API.get('profiles/lawfirm-dashboard/');
//                 if (profileRes.data.status === 'approved') {
//                     setFirmData(profileRes.data);
//                 } else if (profileRes.data.status === 'pending') {
//                     navigate('/lawfirm-pending-onboarding');
//                     return;
//                 } else {
//                     navigate('/lawfirm-onboarding');
//                     return;
//                 }

//                 try {
//                     const statsRes = await API.get('cases/lawfirm-stats/');
//                     setStats(statsRes.data);
//                 } catch (e) { console.error('Stats error:', e); }

//                 try {
//                     const requestsRes = await API.get('cases/case-requests/');
//                     setCaseRequests(requestsRes.data || []);
//                 } catch (e) { console.error('Requests error:', e); }

//                 try {
//                     const casesRes = await API.get('cases/assigned-cases/');
//                     setAssignedCases(casesRes.data || []);
//                 } catch (e) { console.error('Assigned cases error:', e); }

//                 try {
//                     const lawyersRes = await API.get('profiles/lawfirm-lawyers/');
//                     setLawyers(lawyersRes.data || []);
//                 } catch (e) { console.error('Lawyers error:', e); }

//                 try {
//                     const updatesRes = await API.get('cases/court-updates/');
//                     setCourtUpdates(updatesRes.data || []);
//                 } catch (e) { console.error('Court updates error:', e); }

//                 try {
//                     const messagesRes = await API.get('messages/firm-messages/');
//                     setMessages(messagesRes.data || []);
//                 } catch (e) { console.error('Messages error:', e); }

//             } catch (error) {
//                 console.error('Error loading dashboard:', error);
//                 if (error.response?.status === 401) {
//                     localStorage.clear();
//                     navigate('/');
//                 }
//             } finally {
//                 setLoading(false);
//             }
//         };
//         loadDashboard();
//     }, [navigate]);

//     useEffect(() => {
//         if (activePage === 'dashboard' && chartRef.current && !chartInstance) {
//             initChart();
//         }
//         return () => {
//             if (chartInstance) {
//                 chartInstance.destroy();
//                 chartInstance = null;
//             }
//         };
//     }, [activePage]);

//     const initChart = () => {
//         const ctx = chartRef.current.getContext('2d');
//         chartInstance = new Chart(ctx, {
//             type: 'bar',
//             data: {
//                 labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
//                 datasets: [
//                     {
//                         label: 'New Cases',
//                         data: [12, 19, 8, 15, 12, 17, 10, 14, 16, 12, 10, 15],
//                         backgroundColor: 'rgba(26, 60, 139, 0.7)',
//                         borderColor: 'rgba(26, 60, 139, 1)',
//                         borderWidth: 1
//                     },
//                     {
//                         label: 'Closed Cases',
//                         data: [8, 12, 6, 10, 9, 13, 7, 11, 12, 9, 8, 11],
//                         backgroundColor: 'rgba(212, 175, 55, 0.7)',
//                         borderColor: 'rgba(212, 175, 55, 1)',
//                         borderWidth: 1
//                     }
//                 ]
//             },
//             options: {
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 scales: { y: { beginAtZero: true } }
//             }
//         });
//     };

//     const handleAcceptRequest = async (requestId) => {
//         try {
//             await API.post(`cases/accept-request/${requestId}/`);
//             setCaseRequests(prev => prev.filter(req => req.id !== requestId));
//             const statsRes = await API.get('cases/lawfirm-stats/');
//             setStats(statsRes.data);
//             alert('Case request accepted successfully!');
//         } catch (error) {
//             console.error('Error accepting request:', error);
//             alert('Failed to accept request');
//         }
//     };

//     const handleRejectRequest = async (requestId) => {
//         const reason = prompt('Please enter rejection reason:');
//         if (!reason) return;
//         try {
//             await API.post(`cases/reject-request/${requestId}/`, { reason });
//             setCaseRequests(prev => prev.filter(req => req.id !== requestId));
//             alert('Case request rejected');
//         } catch (error) {
//             console.error('Error rejecting request:', error);
//             alert('Failed to reject request');
//         }
//     };

//     const handleAddLawyer = async (e) => {
//         e.preventDefault();
//         try {
//             await API.post('profiles/add-lawyer/', newLawyer);
//             const lawyersRes = await API.get('profiles/lawfirm-lawyers/');
//             setLawyers(lawyersRes.data);
//             setShowAddLawyerForm(false);
//             setNewLawyer({ name: '', email: '', phone: '', experience: '', expertise: [], bar_number: '' });
//             alert('Lawyer added successfully!');
//         } catch (error) {
//             console.error('Error adding lawyer:', error);
//             alert('Failed to add lawyer');
//         }
//     };

//     const handleLogout = () => {
//         localStorage.clear();
//         navigate('/');
//     };

//     const formatDate = (dateString) => {
//         if (!dateString) return 'N/A';
//         try {
//             return new Date(dateString).toLocaleDateString('en-US', {
//                 year: 'numeric', month: 'short', day: 'numeric'
//             });
//         } catch {
//             return 'Invalid date';
//         }
//     };

//     const getStatusBadgeClass = (status) => {
//         switch(status) {
//             case 'pending': return 'status-pending';
//             case 'in_progress': return 'status-in-court';
//             case 'filed': return 'status-filed';
//             case 'new': return 'status-new';
//             case 'assigned': return 'status-assigned';
//             default: return 'status-pending';
//         }
//     };

//     if (loading) {
//         return (
//             <div className="lawfirm-loading-container">
//                 <div className="lawfirm-loading-card">
//                     <div className="lawfirm-spinner"></div>
//                     <h2>Loading Dashboard...</h2>
//                 </div>
//             </div>
//         );
//     }

//     return (
//         <div className="lawfirm-portal-wrapper">
//             {/* Sidebar */}
//             <div className={`lawfirm-portal-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
//                 <div className="lawfirm-portal-logo">
//                     <div className="lawfirm-portal-logo-icon">
//                         <i className="fas fa-balance-scale"></i>
//                     </div>
//                     <div className="lawfirm-portal-logo-text">Advocare</div>
//                 </div>
                
//                 <div className="lawfirm-portal-nav">
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'dashboard' ? 'active' : ''}`} onClick={() => setActivePage('dashboard')}>
//                         <i className="fas fa-tachometer-alt"></i>
//                         <span>Dashboard</span>
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'case-requests' ? 'active' : ''}`} onClick={() => setActivePage('case-requests')}>
//                         <i className="fas fa-file-contract"></i>
//                         <span>Case Requests</span>
//                         {caseRequests.length > 0 && <span className="lawfirm-portal-badge">{caseRequests.length}</span>}
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'assigned-cases' ? 'active' : ''}`} onClick={() => setActivePage('assigned-cases')}>
//                         <i className="fas fa-briefcase"></i>
//                         <span>Assigned Cases</span>
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'lawyers' ? 'active' : ''}`} onClick={() => setActivePage('lawyers')}>
//                         <i className="fas fa-user-tie"></i>
//                         <span>Lawyers</span>
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'court-updates' ? 'active' : ''}`} onClick={() => setActivePage('court-updates')}>
//                         <i className="fas fa-gavel"></i>
//                         <span>Court Updates</span>
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'messages' ? 'active' : ''}`} onClick={() => setActivePage('messages')}>
//                         <i className="fas fa-comments"></i>
//                         <span>Messages</span>
//                         {messages.filter(m => !m.is_read).length > 0 && <span className="lawfirm-portal-badge">{messages.filter(m => !m.is_read).length}</span>}
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'profile' ? 'active' : ''}`} onClick={() => setActivePage('profile')}>
//                         <i className="fas fa-building"></i>
//                         <span>Firm Profile</span>
//                     </div>
//                     <div className={`lawfirm-portal-nav-item ${activePage === 'settings' ? 'active' : ''}`} onClick={() => setActivePage('settings')}>
//                         <i className="fas fa-cog"></i>
//                         <span>Settings</span>
//                     </div>
//                 </div>
                
//                 <div className="lawfirm-portal-user">
//                     <div className="lawfirm-portal-avatar">{firmData?.firm_name?.charAt(0) || 'F'}</div>
//                     <div className="lawfirm-portal-user-info">
//                         <h4>{firmData?.firm_name || 'Law Firm'}</h4>
//                         <p>Law Firm Admin</p>
//                     </div>
//                 </div>
//             </div>
            
//             {/* Main Content */}
//             <div className="lawfirm-portal-main">
//                 <div className="lawfirm-portal-header">
//                     <div className="lawfirm-portal-title">
//                         <button className="lawfirm-portal-toggle" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
//                             <i className="fas fa-bars"></i>
//                         </button>
//                         <i className="fas fa-tachometer-alt"></i>
//                         <span>
//                             {activePage === 'dashboard' ? 'Law Firm Dashboard' :
//                              activePage === 'case-requests' ? 'Case Requests' :
//                              activePage === 'assigned-cases' ? 'Assigned Cases' :
//                              activePage === 'lawyers' ? 'Lawyers Management' :
//                              activePage === 'court-updates' ? 'Court & Hearing Updates' :
//                              activePage === 'messages' ? 'Messages' :
//                              activePage === 'profile' ? 'Firm Profile' : 'Settings'}
//                         </span>
//                     </div>
//                     <div className="lawfirm-portal-actions">
//                         <div className="lawfirm-portal-search">
//                             <i className="fas fa-search"></i>
//                             <input type="text" placeholder="Search..." />
//                         </div>
//                         <div className="lawfirm-portal-notification">
//                             <i className="fas fa-bell"></i>
//                             <span className="lawfirm-portal-dot"></span>
//                         </div>
//                         <button className="lawfirm-portal-logout" onClick={handleLogout}>
//                             <i className="fas fa-sign-out-alt"></i> Logout
//                         </button>
//                     </div>
//                 </div>

//                 {/* Dashboard Page */}
//                 {activePage === 'dashboard' && (
//                     <div className="lawfirm-portal-dashboard">
//                         <div className="lawfirm-portal-kpi">
//                             <div className="lawfirm-portal-kpi-card">
//                                 <div className="lawfirm-portal-kpi-icon"><i className="fas fa-folder-open"></i></div>
//                                 <div><h3>{stats.totalCases}</h3><p>Total Cases</p></div>
//                             </div>
//                             <div className="lawfirm-portal-kpi-card">
//                                 <div className="lawfirm-portal-kpi-icon"><i className="fas fa-gavel"></i></div>
//                                 <div><h3>{stats.activeCases}</h3><p>Active Cases</p></div>
//                             </div>
//                             <div className="lawfirm-portal-kpi-card">
//                                 <div className="lawfirm-portal-kpi-icon"><i className="fas fa-clock"></i></div>
//                                 <div><h3>{stats.pendingRequests}</h3><p>Pending Requests</p></div>
//                             </div>
//                             <div className="lawfirm-portal-kpi-card">
//                                 <div className="lawfirm-portal-kpi-icon"><i className="fas fa-chart-line"></i></div>
//                                 <div><h3>{stats.successRate}%</h3><p>Success Rate</p></div>
//                             </div>
//                         </div>

//                         <div className="lawfirm-portal-stats">
//                             <div className="lawfirm-portal-chart">
//                                 <div className="lawfirm-portal-section-title">
//                                     <span>Case Statistics</span>
//                                     <select><option>Last 30 Days</option><option>Last 3 Months</option></select>
//                                 </div>
//                                 <canvas ref={chartRef}></canvas>
//                             </div>
//                             <div className="lawfirm-portal-activity">
//                                 <div className="lawfirm-portal-section-title">
//                                     <span>Recent Activity</span>
//                                     <button onClick={() => setActivePage('assigned-cases')}>View All</button>
//                                 </div>
//                                 {assignedCases.slice(0, 3).map(c => (
//                                     <div key={c.id} className="lawfirm-portal-activity-item">
//                                         <div className="lawfirm-portal-activity-icon"><i className="fas fa-landmark"></i></div>
//                                         <div><h4>{c.title}</h4><p>Status: {c.status}</p><small>{formatDate(c.updated_at)}</small></div>
//                                     </div>
//                                 ))}
//                             </div>
//                         </div>

//                         <div className="lawfirm-portal-actions-grid">
//                             <button className="lawfirm-portal-action-card" onClick={() => setActivePage('case-requests')}>
//                                 <i className="fas fa-file-contract"></i><span>View Case Requests</span>
//                             </button>
//                             <button className="lawfirm-portal-action-card" onClick={() => setShowAddLawyerForm(true)}>
//                                 <i className="fas fa-user-plus"></i><span>Add Lawyer</span>
//                             </button>
//                             <button className="lawfirm-portal-action-card" onClick={() => setActivePage('court-updates')}>
//                                 <i className="fas fa-upload"></i><span>Upload Update</span>
//                             </button>
//                             <button className="lawfirm-portal-action-card" onClick={() => setActivePage('messages')}>
//                                 <i className="fas fa-comment-medical"></i><span>New Message</span>
//                             </button>
//                         </div>
//                     </div>
//                 )}

//                 {/* Case Requests Page */}
//                 {activePage === 'case-requests' && (
//                     <div>
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Case Requests ({caseRequests.length})</h2>
//                         </div>
//                         <div className="lawfirm-portal-requests-grid">
//                             {caseRequests.map(req => (
//                                 <div key={req.id} className="lawfirm-portal-request-card">
//                                     <div><h3>{req.title}</h3><span className="lawfirm-portal-case-type">{req.case_type}</span></div>
//                                     <p className="lawfirm-portal-case-desc">{req.description}</p>
//                                     <div className="lawfirm-portal-client">
//                                         <div className="lawfirm-portal-client-avatar">{req.client_name?.charAt(0)}</div>
//                                         <div><h4>{req.client_name}</h4><p>{req.client_email}</p></div>
//                                     </div>
//                                     <div className="lawfirm-portal-request-actions">
//                                         <button className="lawfirm-portal-btn-accept" onClick={() => handleAcceptRequest(req.id)}>Accept</button>
//                                         <button className="lawfirm-portal-btn-reject" onClick={() => handleRejectRequest(req.id)}>Reject</button>
//                                         <button className="lawfirm-portal-btn-view">View</button>
//                                     </div>
//                                 </div>
//                             ))}
//                             {caseRequests.length === 0 && <div className="lawfirm-portal-no-data">No pending case requests</div>}
//                         </div>
//                     </div>
//                 )}

//                 {/* Assigned Cases Page */}
//                 {activePage === 'assigned-cases' && (
//                     <div>
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Assigned Cases ({assignedCases.length})</h2>
//                             <button className="lawfirm-portal-btn-primary">+ New Case</button>
//                         </div>
//                         <div className="lawfirm-portal-table">
//                             <table>
//                                 <thead><tr><th>Case</th><th>Client</th><th>Status</th><th>Court</th><th>Next Hearing</th><th>Action</th></tr></thead>
//                                 <tbody>
//                                     {assignedCases.map(c => (
//                                         <tr key={c.id}>
//                                             <td><strong>{c.title}</strong></td>
//                                             <td>{c.client_name}</td>
//                                             <td><span className={`lawfirm-portal-badge-status ${getStatusBadgeClass(c.status)}`}>{c.status}</span></td>
//                                             <td>{c.court_location || '—'}</td>
//                                             <td>{c.next_hearing ? formatDate(c.next_hearing) : '—'}</td>
//                                             <td><button className="lawfirm-portal-btn-view-sm">View</button></td>
//                                         </tr>
//                                     ))}
//                                 </tbody>
//                             </table>
//                         </div>
//                     </div>
//                 )}

//                 {/* Lawyers Page */}
//                 {activePage === 'lawyers' && (
//                     <div>
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Lawyers Management</h2>
//                             <button className="lawfirm-portal-btn-primary" onClick={() => setShowAddLawyerForm(true)}>+ Add Lawyer</button>
//                         </div>
//                         <div className="lawfirm-portal-table">
//                             <table>
//                                 <thead><tr><th>Name</th><th>Practice Area</th><th>Experience</th><th>Active Cases</th><th>Contact</th><th>Action</th></tr></thead>
//                                 <tbody>
//                                     {lawyers.map(l => (
//                                         <tr key={l.id}>
//                                             <td><div className="lawfirm-portal-lawyer"><span className="lawfirm-portal-lawyer-avatar">{l.name?.charAt(0)}</span>{l.name}</div></td>
//                                             <td>{l.expertise?.join(', ') || '—'}</td>
//                                             <td>{l.experience} years</td>
//                                             <td>{l.active_cases}</td>
//                                             <td>{l.email}</td>
//                                             <td><button className="lawfirm-portal-btn-view-sm">Assign</button></td>
//                                         </tr>
//                                     ))}
//                                 </tbody>
//                             </table>
//                         </div>
//                     </div>
//                 )}

//                 {/* Court Updates Page */}
//                 {activePage === 'court-updates' && (
//                     <div className="lawfirm-portal-court">
//                         <div className="lawfirm-portal-page-header">
//                             <h2>Court & Hearing Updates</h2>
//                             <button className="lawfirm-portal-btn-primary">+ Add Update</button>
//                         </div>
//                         <div className="lawfirm-portal-court-grid">
//                             <div>
//                                 <h3>Upcoming Hearings</h3>
//                                 {courtUpdates.filter(u => u.type === 'hearing').map(u => (
//                                     <div key={u.id} className="lawfirm-portal-update-item">
//                                         <div className="lawfirm-portal-update-icon"><i className="fas fa-landmark"></i></div>
//                                         <div><h4>{u.title}</h4><p>{u.court_name}</p><small>{formatDate(u.date)}</small></div>
//                                     </div>
//                                 ))}
//                             </div>
//                             <div>
//                                 <h3>Recent Orders</h3>
//                                 {courtUpdates.filter(u => u.type === 'order').map(u => (
//                                     <div key={u.id} className="lawfirm-portal-order-item">
//                                         <div><h4>{u.title}</h4><p>{u.description}</p><small>{formatDate(u.date)}</small></div>
//                                         <button className="lawfirm-portal-btn-view-sm"><i className="fas fa-download"></i></button>
//                                     </div>
//                                 ))}
//                             </div>
//                         </div>
//                     </div>
//                 )}

//                 {/* Messages Page */}
//                 {activePage === 'messages' && (
//                     <div>
//                         <div className="lawfirm-portal-tabs">
//                             <button className={`lawfirm-portal-tab ${activeTab === 'client-chats' ? 'active' : ''}`} onClick={() => setActiveTab('client-chats')}>Client Chats</button>
//                             <button className={`lawfirm-portal-tab ${activeTab === 'admin-messages' ? 'active' : ''}`} onClick={() => setActiveTab('admin-messages')}>Admin Messages</button>
//                         </div>
//                         {activeTab === 'client-chats' && (
//                             <div className="lawfirm-portal-chat">
//                                 <div className="lawfirm-portal-chat-list">
//                                     <h3>Conversations</h3>
//                                     {messages.filter(m => m.type === 'client').map(m => (
//                                         <div key={m.id} className="lawfirm-portal-chat-item">
//                                             <div className="lawfirm-portal-chat-avatar">{m.sender_name?.charAt(0)}</div>
//                                             <div><h4>{m.sender_name}</h4><p>{m.case_title}</p><small>{formatDate(m.created_at)}</small></div>
//                                         </div>
//                                     ))}
//                                 </div>
//                                 <div className="lawfirm-portal-chat-area">
//                                     <div className="lawfirm-portal-chat-header"><h3>Chat</h3></div>
//                                     <div className="lawfirm-portal-chat-messages">
//                                         <div className="lawfirm-portal-message received"><p>Hello, any updates on my case?</p><span>10:15 AM</span></div>
//                                         <div className="lawfirm-portal-message sent"><p>Hearing scheduled for 18th Jan.</p><span>10:18 AM</span></div>
//                                     </div>
//                                     <div className="lawfirm-portal-chat-input"><input placeholder="Type message..." /><button>Send</button></div>
//                                 </div>
//                             </div>
//                         )}
//                     </div>
//                 )}

//                 {/* Profile Page */}
//                 {activePage === 'profile' && firmData && (
//                     <div className="lawfirm-portal-profile">
//                         <div className="lawfirm-portal-profile-header">
//                             <div className="lawfirm-portal-profile-avatar">{firmData.firm_name?.charAt(0)}</div>
//                             <div><h2>{firmData.firm_name}</h2><p>Established {firmData.established_year || 'N/A'}</p></div>
//                         </div>
//                         <div className="lawfirm-portal-profile-section"><h3>Description</h3><p>{firmData.description || 'No description'}</p></div>
//                         <div className="lawfirm-portal-profile-section"><h3>Practice Areas</h3><div className="lawfirm-portal-tags">{firmData.specialization?.split(',').map((a, i) => <span key={i}>{a.trim()}</span>)}</div></div>
//                         <div className="lawfirm-portal-profile-stats"><div><h3>Success Rate</h3><div className="lawfirm-portal-stat-value">{stats.successRate}%</div></div><div><h3>Rating</h3><div className="lawfirm-portal-stat-value">{firmData.rating || '4.7'}</div></div></div>
//                     </div>
//                 )}

//                 {/* Settings Page */}
//                 {activePage === 'settings' && (
//                     <div className="lawfirm-portal-settings">
//                         <h3>Change Password</h3>
//                         <form>
//                             <div><label>Current Password</label><input type="password" /></div>
//                             <div><label>New Password</label><input type="password" /></div>
//                             <div><label>Confirm Password</label><input type="password" /></div>
//                             <button className="lawfirm-portal-btn-primary">Update Password</button>
//                         </form>
//                     </div>
//                 )}
//             </div>

//             {/* Add Lawyer Modal */}
//             {showAddLawyerForm && (
//                 <div className="lawfirm-portal-modal" onClick={() => setShowAddLawyerForm(false)}>
//                     <div className="lawfirm-portal-modal-content" onClick={e => e.stopPropagation()}>
//                         <div className="lawfirm-portal-modal-header"><h3>Add New Lawyer</h3><button onClick={() => setShowAddLawyerForm(false)}>&times;</button></div>
//                         <form onSubmit={handleAddLawyer}>
//                             <div className="lawfirm-portal-form-row"><div><label>Full Name</label><input type="text" value={newLawyer.name} onChange={e => setNewLawyer({...newLawyer, name: e.target.value})} required /></div>
//                             <div><label>Email</label><input type="email" value={newLawyer.email} onChange={e => setNewLawyer({...newLawyer, email: e.target.value})} required /></div></div>
//                             <div className="lawfirm-portal-form-row"><div><label>Phone</label><input type="tel" value={newLawyer.phone} onChange={e => setNewLawyer({...newLawyer, phone: e.target.value})} /></div>
//                             <div><label>Experience (Years)</label><input type="number" value={newLawyer.experience} onChange={e => setNewLawyer({...newLawyer, experience: e.target.value})} /></div></div>
//                             <div><label>Practice Area</label><select multiple value={newLawyer.expertise} onChange={e => setNewLawyer({...newLawyer, expertise: Array.from(e.target.selectedOptions, o => o.value)})}>{expertiseOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}</select></div>
//                             <div><label>Bar Registration No.</label><input type="text" value={newLawyer.bar_number} onChange={e => setNewLawyer({...newLawyer, bar_number: e.target.value})} /></div>
//                             <div className="lawfirm-portal-modal-footer"><button type="button" onClick={() => setShowAddLawyerForm(false)}>Cancel</button><button type="submit">Add Lawyer</button></div>
//                         </form>
//                     </div>
//                 </div>
//             )}
//         </div>
//     );
// }

// export default LawfirmPortal;