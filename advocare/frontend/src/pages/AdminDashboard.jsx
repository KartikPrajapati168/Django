import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';
import Chart from 'chart.js/auto';

function AdminDashboard() {
    const navigate = useNavigate();
    const [activeModule, setActiveModule] = useState('dashboard');
    const [pendingClients, setPendingClients] = useState([]);
    const [pendingLawFirms, setPendingLawFirms] = useState([]);
    const [allClients, setAllClients] = useState([]);
    const [allLawFirms, setAllLawFirms] = useState([]);
    const [allCases, setAllCases] = useState([]);
    const [assignedCases, setAssignedCases] = useState([]);
    const [disputes, setDisputes] = useState([]);
    const [analytics, setAnalytics] = useState({});
    const [adminProfile, setAdminProfile] = useState({});
    const [editingAdmin, setEditingAdmin] = useState(false);
    const [adminForm, setAdminForm] = useState({});
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState({ text: '', type: '' });
    const [activeLawFirmTab, setActiveLawFirmTab] = useState('pending');
    const [selectedCase, setSelectedCase] = useState(null);
    const [courtUpdateForm, setCourtUpdateForm] = useState({ title: '', description: '', type: 'hearing', court_name: '', date: '', priority: 'normal', case_id: '' });
    const [showCourtForm, setShowCourtForm] = useState(false);
    const [selectedClientDetail, setSelectedClientDetail] = useState(null);
    const [selectedFirmDetail, setSelectedFirmDetail] = useState(null);
    const [caseAiAnalysis, setCaseAiAnalysis] = useState({});
    const [analyzingCase, setAnalyzingCase] = useState(null);

    const barChartRef = useRef(null);
    const lineChartRef = useRef(null);
    const barChartInstance = useRef(null);
    const lineChartInstance = useRef(null);

    const showMsg = (text, type = 'success') => {
        setMessage({ text, type });
        setTimeout(() => setMessage({ text: '', type: '' }), 3500);
    };

    const loadData = useCallback(async () => {
        setLoading(true);
        try {
            const [pendingClientsRes, statsRes, pendingLawFirmsRes] = await Promise.all([
                API.get('profiles/pending-clients/'),
                API.get('profiles/admin-dashboard/'),
                API.get('profiles/pending-lawfirms/')
            ]);
            setPendingClients(pendingClientsRes.data || []);
            setStats(statsRes.data || {});
            setPendingLawFirms(pendingLawFirmsRes.data || []);

            try { const r = await API.get('profiles/all-clients/'); setAllClients(r.data || []); } catch (e) { console.error(e); }
            try { const r = await API.get('profiles/all-lawfirms/'); setAllLawFirms(r.data || []); } catch (e) { console.error(e); }
            try { const r = await API.get('cases/all-cases/'); setAllCases(r.data || []); } catch (e) { console.error(e); }
            try { const r = await API.get('cases/assigned-all/'); setAssignedCases(r.data || []); } catch (e) { console.error(e); }
            try { const r = await API.get('cases/disputes/'); setDisputes(r.data || []); } catch (e) { console.error(e); }
            try { const r = await API.get('profiles/admin-analytics/'); setAnalytics(r.data || {}); } catch (e) { console.error(e); }
            try { const r = await API.get('profiles/admin-profile/'); setAdminProfile(r.data || {}); setAdminForm(r.data || {}); } catch (e) { console.error(e); }
        } catch (error) {
            console.error('Error loading data:', error);
            if (error.response?.status === 401) { localStorage.clear(); navigate('/'); }
        } finally { setLoading(false); }
    }, [navigate]);

    useEffect(() => {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        if (user.role !== 'admin') { navigate('/'); return; }
        loadData();
    }, [navigate, loadData]);

    const initCharts = useCallback(() => {
        if (barChartRef.current) {
            if (barChartInstance.current) barChartInstance.current.destroy();
            barChartInstance.current = new Chart(barChartRef.current.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    datasets: [
                        { label: 'New Clients', data: [8, 14, 10, 18, 13, 21, 11, 16, 19, 14, 12, 17], backgroundColor: 'rgba(26,60,139,0.75)', borderColor: '#1a3c8b', borderWidth: 2, borderRadius: 5 },
                        { label: 'New Cases', data: [5, 11, 7, 14, 9, 16, 8, 12, 15, 10, 9, 13], backgroundColor: 'rgba(212,175,55,0.75)', borderColor: '#d4af37', borderWidth: 2, borderRadius: 5 },
                        { label: 'Resolved Cases', data: [3, 8, 5, 10, 7, 12, 6, 9, 11, 8, 7, 10], backgroundColor: 'rgba(5,150,105,0.75)', borderColor: '#059669', borderWidth: 2, borderRadius: 5 },
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' } }, x: { grid: { display: false } } } }
            });
        }
        if (lineChartRef.current) {
            if (lineChartInstance.current) lineChartInstance.current.destroy();
            lineChartInstance.current = new Chart(lineChartRef.current.getContext('2d'), {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    datasets: [
                        { label: 'Law Firms Onboarded', data: [2, 3, 1, 4, 2, 5, 3, 4, 3, 5, 2, 4], borderColor: '#1a3c8b', backgroundColor: 'rgba(26,60,139,0.1)', tension: 0.4, fill: true, pointRadius: 5 },
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' } }, x: { grid: { display: false } } } }
            });
        }
    }, []);

    useEffect(() => {
        if (activeModule === 'dashboard') {
            const t = setTimeout(initCharts, 100);
            return () => clearTimeout(t);
        }
        return () => {
            if (barChartInstance.current) barChartInstance.current.destroy();
            if (lineChartInstance.current) lineChartInstance.current.destroy();
        };
    }, [activeModule, initCharts]);

    const handleApproveClient = async (clientId) => {
        try { await API.post(`profiles/approve-client/${clientId}/`); showMsg('Client approved!'); await loadData(); } catch { showMsg('Failed to approve', 'error'); }
    };
    const handleRejectClient = async (clientId) => {
        const reason = prompt('Rejection reason:');
        if (!reason) return;
        try { await API.post(`profiles/reject-client/${clientId}/`, { reason }); showMsg('Client rejected', 'error'); await loadData(); } catch { showMsg('Failed to reject', 'error'); }
    };
    const handleApproveLawFirm = async (firmId) => {
        try { await API.post(`profiles/approve-lawfirm/${firmId}/`); showMsg('Law firm approved!'); await loadData(); } catch { showMsg('Failed to approve', 'error'); }
    };
    const handleRejectLawFirm = async (firmId) => {
        const reason = prompt('Rejection reason:');
        if (!reason) return;
        try { await API.post(`profiles/reject-lawfirm/${firmId}/`, { reason }); showMsg('Law firm rejected', 'error'); await loadData(); } catch { showMsg('Failed to reject', 'error'); }
    };

    const handleSendCourtUpdate = async (e) => {
        e.preventDefault();
        try {
            await API.post('cases/admin-court-update/', courtUpdateForm);
            showMsg('Court update sent to law firm!');
            setShowCourtForm(false);
            setCourtUpdateForm({ title: '', description: '', type: 'hearing', court_name: '', date: '', priority: 'normal', case_id: '' });
        } catch { showMsg('Failed to send court update', 'error'); }
    };

    const handleAnalyzeCase = async (caseId) => {
        if (caseAiAnalysis[caseId]) return;
        setAnalyzingCase(caseId);
        try {
            const res = await API.post(`cases/${caseId}/ai-analyze/`);
            setCaseAiAnalysis(prev => ({ ...prev, [caseId]: res.data }));
        } catch {
            setCaseAiAnalysis(prev => ({ ...prev, [caseId]: { summary: 'AI analysis unavailable. Please review manually.', risk: 'N/A', recommendation: 'Manual review required.' } }));
        } finally { setAnalyzingCase(null); }
    };

    const handleSaveAdminProfile = async (e) => {
        e.preventDefault();
        try { await API.put('profiles/admin-profile/', adminForm); setAdminProfile({ ...adminProfile, ...adminForm }); setEditingAdmin(false); showMsg('Profile updated!'); } catch { showMsg('Failed to update', 'error'); }
    };

    const formatDate = (d) => { if (!d) return 'N/A'; try { return new Date(d).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' }); } catch { return 'N/A'; } };
    const getStatusColor = (s) => ({ pending: '#f59e0b', approved: '#10b981', rejected: '#ef4444', active: '#3b82f6', closed: '#6b7280', in_progress: '#8b5cf6' })[s] || '#6b7280';
    const getStatusBg = (s) => ({ pending: '#fef3c7', approved: '#d1fae5', rejected: '#fee2e2', active: '#dbeafe', closed: '#f3f4f6', in_progress: '#ede9fe' })[s] || '#f3f4f6';

    const modules = [
        { id: 'dashboard', name: 'Dashboard', icon: 'tachometer-alt' },
        { id: 'client-onboarding', name: 'Client Onboarding', icon: 'user-clock', badge: pendingClients.length },
        { id: 'lawfirm-onboarding', name: 'Law Firm Onboarding', icon: 'landmark', badge: pendingLawFirms.length },
        { id: 'clients', name: 'Client Management', icon: 'users' },
        { id: 'cases', name: 'Case Moderation', icon: 'folder-open' },
        { id: 'lawfirms', name: 'Law Firm Management', icon: 'building' },
        { id: 'court', name: 'Court Simulation', icon: 'gavel' },
        { id: 'reports', name: 'Disputes & Reports', icon: 'flag' },
        { id: 'analytics', name: 'Analytics & Logs', icon: 'chart-line' },
        { id: 'settings', name: 'System Settings', icon: 'cog' },
    ];

    const renderContent = () => {
        if (loading) return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 200 }}><div className="admin-spinner"></div></div>;

        switch (activeModule) {

            // ── DASHBOARD ──
            case 'dashboard':
                return (
                    <div>
                        <div className="kpi-container">
                            {[
                                { label: 'Total Clients', value: stats.totalClients || 0, icon: 'users', color: '#1a3c8b', bg: '#dbeafe' },
                                { label: 'Total Law Firms', value: stats.totalLawFirms || 0, icon: 'building', color: '#7c3aed', bg: '#ede9fe' },
                                { label: 'Pending Clients', value: stats.pendingClients || 0, icon: 'user-clock', color: '#d97706', bg: '#fef3c7' },
                                { label: 'Pending Law Firms', value: stats.pendingLawFirms || 0, icon: 'landmark', color: '#dc2626', bg: '#fee2e2' },
                                { label: 'Active Cases', value: stats.activeCases || 0, icon: 'folder-open', color: '#059669', bg: '#d1fae5' },
                                { label: 'Approved Clients', value: stats.approvedClients || 0, icon: 'user-check', color: '#0891b2', bg: '#cffafe' },
                            ].map((k, i) => (
                                <div key={i} className="kpi-card" style={{ borderTop: `3px solid ${k.color}` }}>
                                    <div style={{ width: 44, height: 44, borderRadius: 10, background: k.bg, color: k.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.1rem', marginBottom: 10 }}>
                                        <i className={`fas fa-${k.icon}`}></i>
                                    </div>
                                    <div className="kpi-value" style={{ color: k.color }}>{k.value}</div>
                                    <div className="kpi-label">{k.label}</div>
                                </div>
                            ))}
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 20, marginTop: 24 }}>
                            <div className="admin-card">
                                <h3 className="admin-card-title">Monthly Overview</h3>
                                <div style={{ height: 260, position: 'relative' }}><canvas ref={barChartRef}></canvas></div>
                            </div>
                            <div className="admin-card">
                                <h3 className="admin-card-title">Law Firms Growth</h3>
                                <div style={{ height: 260, position: 'relative' }}><canvas ref={lineChartRef}></canvas></div>
                            </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginTop: 20 }}>
                            <div className="admin-card">
                                <h3 className="admin-card-title">Recent Pending Clients</h3>
                                {pendingClients.slice(0, 4).map(c => (
                                    <div key={c.id} className="admin-activity-item">
                                        <div className="admin-activity-avatar">{c.name?.charAt(0)}</div>
                                        <div style={{ flex: 1 }}>
                                            <strong>{c.name}</strong>
                                            <p style={{ margin: 0, fontSize: '0.8rem', color: '#6b7280' }}>{c.case_type} — {c.case_title}</p>
                                        </div>
                                        <span style={{ background: '#fef3c7', color: '#d97706', borderRadius: 20, padding: '2px 10px', fontSize: '0.75rem' }}>Pending</span>
                                    </div>
                                ))}
                                {pendingClients.length === 0 && <p style={{ color: '#9ca3af', textAlign: 'center', padding: 16 }}>No pending clients</p>}
                            </div>
                            <div className="admin-card">
                                <h3 className="admin-card-title">Recent Pending Law Firms</h3>
                                {pendingLawFirms.slice(0, 4).map(f => (
                                    <div key={f.id} className="admin-activity-item">
                                        <div className="admin-activity-avatar" style={{ background: '#7c3aed' }}>{f.firm_name?.charAt(0)}</div>
                                        <div style={{ flex: 1 }}>
                                            <strong>{f.firm_name}</strong>
                                            <p style={{ margin: 0, fontSize: '0.8rem', color: '#6b7280' }}>{f.specialization}</p>
                                        </div>
                                        <span style={{ background: '#ede9fe', color: '#7c3aed', borderRadius: 20, padding: '2px 10px', fontSize: '0.75rem' }}>Review</span>
                                    </div>
                                ))}
                                {pendingLawFirms.length === 0 && <p style={{ color: '#9ca3af', textAlign: 'center', padding: 16 }}>No pending law firms</p>}
                            </div>
                        </div>
                    </div>
                );

            // ── CLIENT ONBOARDING ──
            case 'client-onboarding':
                return (
                    <div className="onboarding-module">
                        <h3>Pending Client Onboarding Requests ({pendingClients.length})</h3>
                        <div className="onboarding-grid">
                            {pendingClients.length === 0 && <div className="no-data"><i className="fas fa-check-circle" style={{ fontSize: 48, color: '#28a745' }}></i><p>No pending client requests</p></div>}
                            {pendingClients.map(client => (
                                <div key={client.id} className="client-card">
                                    <div className="client-header">
                                        <span className="client-name">{client.name}</span>
                                        <span className="client-badge pending">Pending</span>
                                    </div>
                                    <div className="client-info">
                                        <div><i className="fas fa-envelope"></i> {client.email}</div>
                                        <div><i className="fas fa-phone"></i> {client.phone || 'Not provided'}</div>
                                        <div><i className="fas fa-id-card"></i> {client.id_proof_type}: {client.id_proof_number}</div>
                                        <div><i className="fas fa-gavel"></i> {client.case_type} — {client.case_title}</div>
                                        <div><i className="far fa-calendar-alt"></i> Submitted: {client.submitted_at}</div>
                                    </div>
                                    <div className="action-buttons">
                                        <button className="btn-view" onClick={() => setSelectedClientDetail(client)}><i className="fas fa-eye"></i> Review</button>
                                        <button className="btn-approve" onClick={() => handleApproveClient(client.id)}><i className="fas fa-check"></i> Approve</button>
                                        <button className="btn-reject" onClick={() => handleRejectClient(client.id)}><i className="fas fa-times"></i> Reject</button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                );

            // ── LAWFIRM ONBOARDING ──
            case 'lawfirm-onboarding':
                return (
                    <div className="onboarding-module">
                        <div className="lawfirm-tabs">
                            <button className={`lawfirm-tab-btn ${activeLawFirmTab === 'pending' ? 'active' : ''}`} onClick={() => setActiveLawFirmTab('pending')}>Pending ({pendingLawFirms.length})</button>
                            <button className={`lawfirm-tab-btn ${activeLawFirmTab === 'approved' ? 'active' : ''}`} onClick={() => setActiveLawFirmTab('approved')}>Approved Firms</button>
                        </div>
                        {activeLawFirmTab === 'pending' && (
                            <div className="lawfirm-grid">
                                {pendingLawFirms.length === 0 && <div className="no-data"><i className="fas fa-check-circle" style={{ fontSize: 48, color: '#28a745' }}></i><p>No pending law firm requests</p></div>}
                                {pendingLawFirms.map(firm => (
                                    <div key={firm.id} className="lawfirm-card">
                                        <div className="client-header"><span className="client-name">{firm.firm_name}</span><span className="client-badge pending">Pending Verification</span></div>
                                        <div className="client-info">
                                            <div><i className="fas fa-envelope"></i> {firm.email}</div>
                                            <div><i className="fas fa-phone"></i> {firm.phone || 'N/A'}</div>
                                            <div><i className="fas fa-id-card"></i> Reg No: {firm.registration_no}</div>
                                            <div><i className="fas fa-gavel"></i> {firm.specialization}</div>
                                            <div><i className="fas fa-user-tie"></i> Primary: {firm.primary_lawyer_name}</div>
                                            <div><i className="far fa-calendar-alt"></i> Submitted: {firm.submitted_at}</div>
                                        </div>
                                        <div className="action-buttons">
                                            <button className="btn-view" onClick={() => setSelectedFirmDetail(firm)}><i className="fas fa-eye"></i> Review</button>
                                            <button className="btn-approve" onClick={() => handleApproveLawFirm(firm.id)}><i className="fas fa-check"></i> Approve</button>
                                            <button className="btn-reject" onClick={() => handleRejectLawFirm(firm.id)}><i className="fas fa-times"></i> Reject</button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                        {activeLawFirmTab === 'approved' && (
                            <div className="lawfirm-grid">
                                {allLawFirms.filter(f => f.status === 'approved').length === 0 && <div className="no-data"><i className="fas fa-check-circle" style={{ fontSize: 48, color: '#28a745' }}></i><p>No approved firms yet</p></div>}
                                {allLawFirms.filter(f => f.status === 'approved').map(firm => (
                                    <div key={firm.id} className="lawfirm-card">
                                        <div className="client-header"><span className="client-name">{firm.firm_name}</span><span className="client-badge" style={{ background: '#d1fae5', color: '#065f46' }}>Approved</span></div>
                                        <div className="client-info">
                                            <div><i className="fas fa-envelope"></i> {firm.email}</div>
                                            <div><i className="fas fa-gavel"></i> {firm.specialization}</div>
                                            <div><i className="fas fa-user-tie"></i> {firm.primary_lawyer_name}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                );

            // ── CLIENT MANAGEMENT ──
            case 'clients':
                return (
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                            <h3 style={{ margin: 0 }}>All Clients ({allClients.length})</h3>
                            <div style={{ display: 'flex', gap: 10 }}>
                                <input type="text" placeholder="Search clients..." className="admin-search-input" />
                            </div>
                        </div>
                        <div className="admin-table-wrap">
                            <table className="admin-table">
                                <thead><tr><th>Client</th><th>Contact</th><th>ID Proof</th><th>Case</th><th>Status</th><th>Joined</th><th>Action</th></tr></thead>
                                <tbody>
                                    {allClients.map(c => (
                                        <tr key={c.id}>
                                            <td>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                                    <div className="admin-table-avatar">{c.name?.charAt(0)}</div>
                                                    <div><strong>{c.name}</strong><br /><small style={{ color: '#9ca3af' }}>{c.email}</small></div>
                                                </div>
                                            </td>
                                            <td>{c.phone || '—'}</td>
                                            <td><small>{c.id_proof_type}: {c.id_proof_number}</small></td>
                                            <td><strong style={{ fontSize: '0.85rem' }}>{c.case_title}</strong><br /><small style={{ color: '#6b7280' }}>{c.case_type}</small></td>
                                            <td><span style={{ background: getStatusBg(c.status), color: getStatusColor(c.status), borderRadius: 20, padding: '3px 12px', fontSize: '0.75rem', fontWeight: 600 }}>{c.status}</span></td>
                                            <td><small>{formatDate(c.submitted_at)}</small></td>
                                            <td>
                                                <button className="admin-btn-sm" onClick={() => setSelectedClientDetail(c)}>Review</button>
                                                {c.status === 'pending' && <>
                                                    <button className="admin-btn-sm approve" style={{ marginLeft: 4 }} onClick={() => handleApproveClient(c.id)}>✓</button>
                                                    <button className="admin-btn-sm reject" style={{ marginLeft: 4 }} onClick={() => handleRejectClient(c.id)}>✗</button>
                                                </>}
                                            </td>
                                        </tr>
                                    ))}
                                    {allClients.length === 0 && <tr><td colSpan={7} style={{ textAlign: 'center', color: '#9ca3af', padding: 32 }}>No clients found</td></tr>}
                                </tbody>
                            </table>
                        </div>
                    </div>
                );

            // ── CASE MODERATION ──
            case 'cases':
                return (
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                            <h3 style={{ margin: 0 }}>Case Moderation ({allCases.length})</h3>
                            <div style={{ background: '#dbeafe', color: '#1a3c8b', borderRadius: 8, padding: '8px 14px', fontSize: '0.85rem' }}>
                                <i className="fas fa-robot me-2"></i> AI/ML Analysis Available
                            </div>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                            {allCases.map(c => (
                                <div key={c.id} className="admin-card" style={{ padding: 20 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                                                <h4 style={{ margin: 0, fontWeight: 600 }}>{c.title}</h4>
                                                <span style={{ background: getStatusBg(c.status), color: getStatusColor(c.status), borderRadius: 20, padding: '2px 10px', fontSize: '0.75rem', fontWeight: 600 }}>{c.status}</span>
                                                <span style={{ background: '#f3f4f6', color: '#374151', borderRadius: 20, padding: '2px 10px', fontSize: '0.75rem' }}>{c.case_type}</span>
                                            </div>
                                            <p style={{ margin: '6px 0 4px', color: '#6b7280', fontSize: '0.85rem' }}>{c.description?.substring(0, 160)}...</p>
                                            <div style={{ display: 'flex', gap: 20, fontSize: '0.8rem', color: '#9ca3af', flexWrap: 'wrap' }}>
                                                <span><i className="fas fa-user me-1"></i> {c.client_name}</span>
                                                <span><i className="fas fa-building me-1"></i> {c.lawfirm_name || 'Unassigned'}</span>
                                                <span><i className="fas fa-calendar me-1"></i> {formatDate(c.created_at)}</span>
                                                <span><i className="fas fa-map-marker-alt me-1"></i> {c.court_location || 'N/A'}</span>
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', gap: 8, marginLeft: 16 }}>
                                            <button className="admin-btn-sm" onClick={() => setSelectedCase(selectedCase?.id === c.id ? null : c)}>
                                                {selectedCase?.id === c.id ? 'Hide' : 'Details'}
                                            </button>
                                            <button className="admin-btn-sm" style={{ background: '#dbeafe', color: '#1a3c8b' }}
                                                onClick={() => handleAnalyzeCase(c.id)}
                                                disabled={analyzingCase === c.id}>
                                                {analyzingCase === c.id ? <span><i className="fas fa-spinner fa-spin me-1"></i>Analyzing...</span> : <span><i className="fas fa-robot me-1"></i>AI Analyze</span>}
                                            </button>
                                        </div>
                                    </div>

                                    {selectedCase?.id === c.id && (
                                        <div style={{ marginTop: 16, padding: 16, background: '#f9fafb', borderRadius: 10, borderLeft: '3px solid #1a3c8b' }}>
                                            <h5 style={{ fontWeight: 600, marginBottom: 12 }}>Full Case Details</h5>
                                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
                                                {[
                                                    ['Case ID', `#${c.id}`], ['Case Type', c.case_type], ['Status', c.status],
                                                    ['Client', c.client_name], ['Client Email', c.client_email || 'N/A'], ['Law Firm', c.lawfirm_name || 'Unassigned'],
                                                    ['Court', c.court_location || 'N/A'], ['Filed On', formatDate(c.created_at)], ['Last Updated', formatDate(c.updated_at)],
                                                ].map(([label, val], i) => (
                                                    <div key={i}><small style={{ color: '#9ca3af', fontWeight: 500 }}>{label}</small><p style={{ margin: 0, fontWeight: 500, color: '#374151' }}>{val}</p></div>
                                                ))}
                                            </div>
                                            {c.description && <div style={{ marginTop: 12 }}><small style={{ color: '#9ca3af', fontWeight: 500 }}>Full Description</small><p style={{ margin: '4px 0 0', color: '#374151', fontSize: '0.875rem' }}>{c.description}</p></div>}
                                        </div>
                                    )}

                                    {caseAiAnalysis[c.id] && (
                                        <div style={{ marginTop: 12, padding: 16, background: '#fffbeb', borderRadius: 10, borderLeft: '3px solid #f59e0b' }}>
                                            <h5 style={{ fontWeight: 600, color: '#92400e', marginBottom: 10 }}><i className="fas fa-robot me-2"></i>AI/ML Case Analysis</h5>
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                                                <div><small style={{ color: '#9ca3af' }}>Summary</small><p style={{ margin: 0, fontSize: '0.875rem', color: '#374151' }}>{caseAiAnalysis[c.id].summary}</p></div>
                                                <div>
                                                    <small style={{ color: '#9ca3af' }}>Risk Level</small>
                                                    <p style={{ margin: 0, fontWeight: 700, color: caseAiAnalysis[c.id].risk === 'High' ? '#dc2626' : caseAiAnalysis[c.id].risk === 'Medium' ? '#d97706' : '#059669' }}>
                                                        {caseAiAnalysis[c.id].risk}
                                                    </p>
                                                </div>
                                                <div style={{ gridColumn: '1/-1' }}><small style={{ color: '#9ca3af' }}>Recommendation</small><p style={{ margin: 0, fontSize: '0.875rem', color: '#374151' }}>{caseAiAnalysis[c.id].recommendation}</p></div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                            {allCases.length === 0 && <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af' }}><i className="fas fa-folder-open fa-3x mb-3"></i><p>No cases found</p></div>}
                        </div>
                    </div>
                );

            // ── LAW FIRM MANAGEMENT ──
            case 'lawfirms':
                return (
                    <div>
                        <h3 style={{ marginBottom: 20 }}>Law Firm Management ({allLawFirms.length})</h3>
                        <div className="admin-table-wrap">
                            <table className="admin-table">
                                <thead><tr><th>Firm</th><th>Registration</th><th>Specialization</th><th>Primary Lawyer</th><th>Contact</th><th>Status</th><th>Cases</th><th>Action</th></tr></thead>
                                <tbody>
                                    {allLawFirms.map(f => (
                                        <tr key={f.id}>
                                            <td>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                                    <div className="admin-table-avatar" style={{ background: '#7c3aed' }}>{f.firm_name?.charAt(0)}</div>
                                                    <div><strong>{f.firm_name}</strong><br /><small style={{ color: '#9ca3af' }}>{f.email}</small></div>
                                                </div>
                                            </td>
                                            <td><small>{f.registration_no || '—'}</small></td>
                                            <td><small>{f.specialization?.substring(0, 40)}</small></td>
                                            <td>{f.primary_lawyer_name}</td>
                                            <td><small>{f.phone || '—'}</small></td>
                                            <td><span style={{ background: getStatusBg(f.status), color: getStatusColor(f.status), borderRadius: 20, padding: '3px 12px', fontSize: '0.75rem', fontWeight: 600 }}>{f.status}</span></td>
                                            <td>{f.total_cases || 0}</td>
                                            <td>
                                                <button className="admin-btn-sm" onClick={() => setSelectedFirmDetail(f)}>Review</button>
                                                {f.status === 'pending' && <button className="admin-btn-sm approve" style={{ marginLeft: 4 }} onClick={() => handleApproveLawFirm(f.id)}>Approve</button>}
                                            </td>
                                        </tr>
                                    ))}
                                    {allLawFirms.length === 0 && <tr><td colSpan={8} style={{ textAlign: 'center', color: '#9ca3af', padding: 32 }}>No law firms found</td></tr>}
                                </tbody>
                            </table>
                        </div>
                    </div>
                );

            // ── COURT SIMULATION ──
            case 'court':
                return (
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                            <div>
                                <h3 style={{ margin: 0 }}>Court Simulation Panel</h3>
                                <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>Review assigned cases and send court updates to law firms</p>
                            </div>
                            <button className="admin-btn-primary" onClick={() => setShowCourtForm(true)}>
                                <i className="fas fa-plus me-2"></i> Send Court Update
                            </button>
                        </div>

                        {showCourtForm && (
                            <div className="admin-card" style={{ marginBottom: 24, borderLeft: '4px solid #1a3c8b' }}>
                                <h4 style={{ marginTop: 0, color: '#1a3c8b' }}><i className="fas fa-gavel me-2"></i>New Court Update / Order</h4>
                                <form onSubmit={handleSendCourtUpdate}>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                                        <div>
                                            <label className="admin-label">Select Case *</label>
                                            <select required value={courtUpdateForm.case_id} onChange={e => setCourtUpdateForm({ ...courtUpdateForm, case_id: e.target.value })} className="admin-input">
                                                <option value="">Select a case...</option>
                                                {assignedCases.map(c => <option key={c.id} value={c.id}>{c.title} — {c.client_name}</option>)}
                                            </select>
                                        </div>
                                        <div>
                                            <label className="admin-label">Update Type *</label>
                                            <select required value={courtUpdateForm.type} onChange={e => setCourtUpdateForm({ ...courtUpdateForm, type: e.target.value })} className="admin-input">
                                                <option value="hearing">Hearing Date</option>
                                                <option value="order">Court Order</option>
                                                <option value="update">Case Update</option>
                                                <option value="verdict">Verdict</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label className="admin-label">Update Title *</label>
                                            <input required type="text" value={courtUpdateForm.title} onChange={e => setCourtUpdateForm({ ...courtUpdateForm, title: e.target.value })} className="admin-input" placeholder="e.g. Hearing scheduled on..." />
                                        </div>
                                        <div>
                                            <label className="admin-label">Court Name</label>
                                            <input type="text" value={courtUpdateForm.court_name} onChange={e => setCourtUpdateForm({ ...courtUpdateForm, court_name: e.target.value })} className="admin-input" placeholder="e.g. Ahmedabad High Court" />
                                        </div>
                                        <div>
                                            <label className="admin-label">Date & Time</label>
                                            <input type="datetime-local" value={courtUpdateForm.date} onChange={e => setCourtUpdateForm({ ...courtUpdateForm, date: e.target.value })} className="admin-input" />
                                        </div>
                                        <div>
                                            <label className="admin-label">Priority</label>
                                            <select value={courtUpdateForm.priority} onChange={e => setCourtUpdateForm({ ...courtUpdateForm, priority: e.target.value })} className="admin-input">
                                                <option value="normal">Normal</option>
                                                <option value="high">High</option>
                                                <option value="urgent">Urgent</option>
                                            </select>
                                        </div>
                                        <div style={{ gridColumn: '1/-1' }}>
                                            <label className="admin-label">Description / Details *</label>
                                            <textarea required rows={4} value={courtUpdateForm.description} onChange={e => setCourtUpdateForm({ ...courtUpdateForm, description: e.target.value })} className="admin-input" placeholder="Detailed update for the law firm and client..." style={{ resize: 'vertical' }} />
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
                                        <button type="submit" className="admin-btn-primary"><i className="fas fa-paper-plane me-2"></i>Send to Law Firm</button>
                                        <button type="button" onClick={() => setShowCourtForm(false)} style={{ padding: '8px 20px', borderRadius: 8, border: '1px solid #d1d5db', background: 'white', cursor: 'pointer' }}>Cancel</button>
                                    </div>
                                </form>
                            </div>
                        )}

                        <div className="admin-table-wrap">
                            <table className="admin-table">
                                <thead><tr><th>Case</th><th>Client</th><th>Law Firm</th><th>Case Type</th><th>Status</th><th>Court</th><th>Assigned On</th><th>Actions</th></tr></thead>
                                <tbody>
                                    {assignedCases.map(c => (
                                        <tr key={c.id}>
                                            <td><strong>{c.title}</strong><br /><small style={{ color: '#9ca3af' }}>#{c.id}</small></td>
                                            <td>{c.client_name}</td>
                                            <td>{c.lawfirm_name || '—'}</td>
                                            <td><small>{c.case_type}</small></td>
                                            <td><span style={{ background: getStatusBg(c.status), color: getStatusColor(c.status), borderRadius: 20, padding: '2px 10px', fontSize: '0.75rem', fontWeight: 600 }}>{c.status}</span></td>
                                            <td><small>{c.court_location || '—'}</small></td>
                                            <td><small>{formatDate(c.assigned_at || c.created_at)}</small></td>
                                            <td>
                                                <button className="admin-btn-sm" onClick={() => { setCourtUpdateForm({ ...courtUpdateForm, case_id: c.id }); setShowCourtForm(true); }}>
                                                    <i className="fas fa-gavel"></i> Send Update
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                    {assignedCases.length === 0 && <tr><td colSpan={8} style={{ textAlign: 'center', color: '#9ca3af', padding: 32 }}>No assigned cases</td></tr>}
                                </tbody>
                            </table>
                        </div>
                    </div>
                );

            // ── DISPUTES & REPORTS ──
            case 'reports':
                return (
                    <div>
                        <h3 style={{ marginBottom: 20 }}>Disputes & Reports</h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 24 }}>
                            {[
                                { label: 'Total Disputes', value: disputes.length, color: '#dc2626', bg: '#fee2e2', icon: 'flag' },
                                { label: 'Open Disputes', value: disputes.filter(d => d.status === 'open').length, color: '#d97706', bg: '#fef3c7', icon: 'exclamation-triangle' },
                                { label: 'Resolved', value: disputes.filter(d => d.status === 'resolved').length, color: '#059669', bg: '#d1fae5', icon: 'check-circle' },
                            ].map((s, i) => (
                                <div key={i} className="admin-card" style={{ display: 'flex', alignItems: 'center', gap: 14, borderTop: `3px solid ${s.color}` }}>
                                    <div style={{ width: 44, height: 44, borderRadius: 10, background: s.bg, color: s.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.1rem' }}>
                                        <i className={`fas fa-${s.icon}`}></i>
                                    </div>
                                    <div><div style={{ fontSize: '1.75rem', fontWeight: 700, color: s.color }}>{s.value}</div><div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{s.label}</div></div>
                                </div>
                            ))}
                        </div>

                        <div className="admin-table-wrap">
                            <table className="admin-table">
                                <thead><tr><th>Report ID</th><th>Filed By</th><th>Against</th><th>Subject</th><th>Category</th><th>Status</th><th>Date</th><th>Action</th></tr></thead>
                                <tbody>
                                    {disputes.map(d => (
                                        <tr key={d.id}>
                                            <td><strong>#D{d.id}</strong></td>
                                            <td>{d.filed_by_name || '—'}</td>
                                            <td>{d.against_name || '—'}</td>
                                            <td>{d.subject?.substring(0, 50) || '—'}</td>
                                            <td><small>{d.category || 'General'}</small></td>
                                            <td><span style={{ background: getStatusBg(d.status), color: getStatusColor(d.status), borderRadius: 20, padding: '2px 10px', fontSize: '0.75rem', fontWeight: 600 }}>{d.status}</span></td>
                                            <td><small>{formatDate(d.created_at)}</small></td>
                                            <td><button className="admin-btn-sm">Resolve</button></td>
                                        </tr>
                                    ))}
                                    {disputes.length === 0 && <tr><td colSpan={8} style={{ textAlign: 'center', color: '#9ca3af', padding: 32 }}>No disputes filed</td></tr>}
                                </tbody>
                            </table>
                        </div>
                    </div>
                );

            // ── ANALYTICS ──
            case 'analytics':
                return (
                    <div>
                        <h3 style={{ marginBottom: 20 }}>Analytics & System Logs</h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
                            {[
                                { label: 'Total Logins (30d)', value: analytics.totalLogins || '248', icon: 'sign-in-alt', color: '#1a3c8b' },
                                { label: 'API Requests', value: analytics.apiRequests || '5,120', icon: 'server', color: '#7c3aed' },
                                { label: 'Avg. Case Duration', value: analytics.avgCaseDuration || '42 days', icon: 'clock', color: '#d97706' },
                                { label: 'Avg. Resolution Time', value: analytics.avgResolution || '28 days', icon: 'hourglass-half', color: '#059669' },
                            ].map((s, i) => (
                                <div key={i} className="admin-card" style={{ textAlign: 'center', borderTop: `3px solid ${s.color}` }}>
                                    <div style={{ fontSize: '1.5rem', marginBottom: 8, color: s.color }}><i className={`fas fa-${s.icon}`}></i></div>
                                    <div style={{ fontSize: '1.4rem', fontWeight: 700, color: s.color }}>{s.value}</div>
                                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{s.label}</div>
                                </div>
                            ))}
                        </div>

                        <div className="admin-card">
                            <h4 style={{ marginTop: 0, borderBottom: '1px solid #f0f0f0', paddingBottom: 12 }}>System Activity Log</h4>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                                {(analytics.logs || [
                                    { action: 'Client Approved', user: 'Admin', target: 'Rajesh Kumar', time: '2 min ago', type: 'success' },
                                    { action: 'Law Firm Approved', user: 'Admin', target: 'Mehta & Associates', time: '15 min ago', type: 'success' },
                                    { action: 'Case Assigned', user: 'System', target: 'Case #142 → Mehta & Assoc.', time: '1 hr ago', type: 'info' },
                                    { action: 'Court Update Sent', user: 'Admin', target: 'Case #138 - Hearing on 25 Apr', time: '2 hrs ago', type: 'info' },
                                    { action: 'Client Rejected', user: 'Admin', target: 'Priya Patel - Incomplete docs', time: '3 hrs ago', type: 'error' },
                                    { action: 'New Case Filed', user: 'Client: Amit Shah', target: 'Property Dispute #143', time: '4 hrs ago', type: 'info' },
                                    { action: 'Law Firm Rejected', user: 'Admin', target: 'XYZ Legal - Invalid Reg', time: '5 hrs ago', type: 'error' },
                                    { action: 'Password Reset', user: 'System', target: 'User ID #251', time: '6 hrs ago', type: 'warning' },
                                ]).map((log, i) => (
                                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '10px 0', borderBottom: '1px solid #f9fafb' }}>
                                        <div style={{ width: 8, height: 8, borderRadius: '50%', background: log.type === 'success' ? '#10b981' : log.type === 'error' ? '#ef4444' : log.type === 'warning' ? '#f59e0b' : '#3b82f6', flexShrink: 0 }}></div>
                                        <div style={{ flex: 1 }}>
                                            <strong style={{ fontSize: '0.875rem' }}>{log.action}</strong>
                                            <span style={{ fontSize: '0.8rem', color: '#6b7280', marginLeft: 8 }}>by {log.user}</span>
                                            <p style={{ margin: 0, fontSize: '0.8rem', color: '#9ca3af' }}>{log.target}</p>
                                        </div>
                                        <small style={{ color: '#9ca3af', flexShrink: 0 }}>{log.time}</small>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                );

            // ── SETTINGS ──
            case 'settings':
                return (
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                            <div>
                                <h3 style={{ margin: 0 }}>System Settings</h3>
                                <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>Manage your admin profile and system configuration</p>
                            </div>
                            {!editingAdmin && <button className="admin-btn-primary" onClick={() => setEditingAdmin(true)}><i className="fas fa-edit me-2"></i>Edit Profile</button>}
                        </div>

                        {!editingAdmin ? (
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 24 }}>
                                <div className="admin-card" style={{ textAlign: 'center' }}>
                                    <div style={{ width: 80, height: 80, borderRadius: '50%', background: '#1a3c8b', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', fontWeight: 700, margin: '0 auto 16px' }}>
                                        {adminProfile.name?.charAt(0) || 'A'}
                                    </div>
                                    <h3 style={{ margin: 0 }}>{adminProfile.name || 'Admin User'}</h3>
                                    <p style={{ color: '#6b7280', marginBottom: 4 }}>{adminProfile.role || 'System Administrator'}</p>
                                    <span style={{ background: '#dbeafe', color: '#1a3c8b', borderRadius: 20, padding: '3px 14px', fontSize: '0.8rem' }}>Super Admin</span>
                                    <div style={{ marginTop: 16, textAlign: 'left' }}>
                                        <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}><small style={{ color: '#9ca3af' }}>Last Login</small><p style={{ margin: 0, fontSize: '0.875rem' }}>{adminProfile.last_login || 'Just now'}</p></div>
                                        <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}><small style={{ color: '#9ca3af' }}>Account Created</small><p style={{ margin: 0, fontSize: '0.875rem' }}>{adminProfile.created_at ? formatDate(adminProfile.created_at) : 'N/A'}</p></div>
                                        <div style={{ padding: '8px 0' }}><small style={{ color: '#9ca3af' }}>2FA Status</small><p style={{ margin: 0, color: '#059669', fontWeight: 600 }}>{adminProfile.twofa ? 'Enabled' : 'Disabled'}</p></div>
                                    </div>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                                    <div className="admin-card">
                                        <h4 style={{ marginTop: 0, color: '#1a3c8b' }}>Personal Information</h4>
                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                                            {[['Full Name', adminProfile.name], ['Email', adminProfile.email], ['Phone', adminProfile.phone || 'Not set'], ['Department', adminProfile.department || 'Administration'], ['Employee ID', adminProfile.employee_id || 'ADM-001'], ['Designation', adminProfile.designation || 'System Administrator']].map(([label, val], i) => (
                                                <div key={i}><small style={{ color: '#9ca3af', fontWeight: 500 }}>{label}</small><p style={{ margin: 0, fontWeight: 500, color: '#374151' }}>{val || 'N/A'}</p></div>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="admin-card">
                                        <h4 style={{ marginTop: 0, color: '#1a3c8b' }}>System Permissions</h4>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                                            {['Client Management', 'Law Firm Management', 'Case Moderation', 'Court Simulation', 'Analytics Access', 'System Configuration', 'User Management', 'Reports & Disputes'].map((p, i) => (
                                                <span key={i} style={{ background: '#d1fae5', color: '#065f46', borderRadius: 20, padding: '4px 12px', fontSize: '0.75rem', fontWeight: 500 }}>
                                                    <i className="fas fa-check-circle me-1"></i>{p}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="admin-card">
                                        <h4 style={{ marginTop: 0, color: '#1a3c8b' }}>Security Settings</h4>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                            {[['Two-Factor Authentication', adminProfile.twofa ? '✓ Enabled' : '✗ Disabled', adminProfile.twofa ? '#059669' : '#dc2626'], ['Session Timeout', '30 minutes', '#374151'], ['IP Whitelist', 'Not configured', '#374151']].map(([label, val, color], i) => (
                                                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                                                    <span style={{ fontSize: '0.875rem', color: '#374151' }}>{label}</span>
                                                    <span style={{ fontSize: '0.875rem', fontWeight: 600, color }}>{val}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <form onSubmit={handleSaveAdminProfile}>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }} className="admin-card">
                                    <h4 style={{ gridColumn: '1/-1', marginTop: 0, color: '#1a3c8b' }}>Edit Admin Profile</h4>
                                    {[['Full Name', 'name', 'text'], ['Email', 'email', 'email'], ['Phone', 'phone', 'tel'], ['Department', 'department', 'text'], ['Designation', 'designation', 'text'], ['Employee ID', 'employee_id', 'text']].map(([label, key, type]) => (
                                        <div key={key}>
                                            <label className="admin-label">{label}</label>
                                            <input type={type} value={adminForm[key] || ''} onChange={e => setAdminForm({ ...adminForm, [key]: e.target.value })} className="admin-input" />
                                        </div>
                                    ))}
                                    <h4 style={{ gridColumn: '1/-1', margin: '8px 0 0', color: '#1a3c8b' }}>Change Password</h4>
                                    <div><label className="admin-label">Current Password</label><input type="password" className="admin-input" /></div>
                                    <div><label className="admin-label">New Password</label><input type="password" className="admin-input" /></div>
                                    <div style={{ gridColumn: '1/-1', display: 'flex', gap: 12, marginTop: 8 }}>
                                        <button type="submit" className="admin-btn-primary"><i className="fas fa-save me-2"></i>Save Changes</button>
                                        <button type="button" onClick={() => setEditingAdmin(false)} style={{ padding: '8px 20px', borderRadius: 8, border: '1px solid #d1d5db', background: 'white', cursor: 'pointer' }}>Cancel</button>
                                    </div>
                                </div>
                            </form>
                        )}
                    </div>
                );

            default:
                return (
                    <div className="coming-soon">
                        <h3>{modules.find(m => m.id === activeModule)?.name}</h3>
                        <p>This module is under development.</p>
                    </div>
                );
        }
    };

    return (
        <div className="admin-dashboard">
            <div className="admin-sidebar">
                <div className="logo-container">
                    <div className="logo"><i className="fas fa-balance-scale"></i><h1>Advocare</h1></div>
                </div>
                <div className="nav-menu">
                    {modules.map(module => (
                        <div key={module.id} className={`nav-item ${activeModule === module.id ? 'active' : ''}`} onClick={() => setActiveModule(module.id)}>
                            <i className={`fas fa-${module.icon}`}></i>
                            <span>{module.name}</span>
                            {module.badge > 0 && <span className="badge">{module.badge}</span>}
                        </div>
                    ))}
                </div>
            </div>

            <div className="admin-main">
                <header className="admin-header">
                    <div className="header-left">
                        <h2>{modules.find(m => m.id === activeModule)?.name}</h2>
                    </div>
                    <div className="header-right">
                        <div className="admin-profile">
                            <div className="admin-avatar">{adminProfile.name?.charAt(0)?.toUpperCase() || 'AD'}</div>
                            <div className="admin-info">
                                <h4>{adminProfile.name || 'Admin User'}</h4>
                                <p>System Administrator</p>
                            </div>
                        </div>
                        <button className="btn-outline" onClick={() => { localStorage.clear(); navigate('/'); }}>
                            <i className="fas fa-sign-out-alt"></i> Logout
                        </button>
                    </div>
                </header>

                {message.text && (
                    <div className={`alert alert-${message.type === 'success' ? 'success' : 'danger'}`} style={{ margin: '0 24px', borderRadius: 8 }}>
                        <i className={`fas fa-${message.type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2`}></i>
                        {message.text}
                    </div>
                )}

                <div className="content-area">{renderContent()}</div>

                <footer className="admin-footer">
                    <p>Advocare — Smart Legal Case Management System | Admin Portal | © 2025</p>
                </footer>
            </div>

            {/* Client Detail Modal */}
            {selectedClientDetail && (
                <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={() => setSelectedClientDetail(null)}>
                    <div style={{ background: 'white', borderRadius: 16, width: 600, maxHeight: '85vh', overflow: 'auto', boxShadow: '0 25px 50px rgba(0,0,0,0.25)' }} onClick={e => e.stopPropagation()}>
                        <div style={{ padding: '20px 24px', borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3 style={{ margin: 0, color: '#1a3c8b' }}><i className="fas fa-user me-2"></i>Client Full Details</h3>
                            <button onClick={() => setSelectedClientDetail(null)} style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#6b7280' }}>&times;</button>
                        </div>
                        <div style={{ padding: 24 }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                                {[['Full Name', selectedClientDetail.name], ['Email', selectedClientDetail.email], ['Phone', selectedClientDetail.phone || 'N/A'], ['ID Type', selectedClientDetail.id_proof_type], ['ID Number', selectedClientDetail.id_proof_number], ['Status', selectedClientDetail.status], ['Case Title', selectedClientDetail.case_title], ['Case Type', selectedClientDetail.case_type], ['Submitted', formatDate(selectedClientDetail.submitted_at)], ['Address', selectedClientDetail.address || 'N/A']].map(([label, val], i) => (
                                    <div key={i} style={{ padding: '8px 0', borderBottom: '1px solid #f9fafb' }}>
                                        <small style={{ color: '#9ca3af', fontWeight: 500, display: 'block' }}>{label}</small>
                                        <span style={{ fontWeight: 500, color: '#374151' }}>{val}</span>
                                    </div>
                                ))}
                            </div>
                            {selectedClientDetail.case_description && (
                                <div style={{ marginTop: 16, padding: 12, background: '#f9fafb', borderRadius: 8 }}>
                                    <small style={{ color: '#9ca3af', fontWeight: 500 }}>Case Description</small>
                                    <p style={{ margin: '4px 0 0', color: '#374151', fontSize: '0.875rem' }}>{selectedClientDetail.case_description}</p>
                                </div>
                            )}
                            {selectedClientDetail.status === 'pending' && (
                                <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
                                    <button className="btn-approve" onClick={() => { handleApproveClient(selectedClientDetail.id); setSelectedClientDetail(null); }}>
                                        <i className="fas fa-check me-2"></i>Approve Client
                                    </button>
                                    <button className="btn-reject" onClick={() => { handleRejectClient(selectedClientDetail.id); setSelectedClientDetail(null); }}>
                                        <i className="fas fa-times me-2"></i>Reject Client
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Firm Detail Modal */}
            {selectedFirmDetail && (
                <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={() => setSelectedFirmDetail(null)}>
                    <div style={{ background: 'white', borderRadius: 16, width: 640, maxHeight: '85vh', overflow: 'auto', boxShadow: '0 25px 50px rgba(0,0,0,0.25)' }} onClick={e => e.stopPropagation()}>
                        <div style={{ padding: '20px 24px', borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3 style={{ margin: 0, color: '#1a3c8b' }}><i className="fas fa-building me-2"></i>Law Firm Full Details</h3>
                            <button onClick={() => setSelectedFirmDetail(null)} style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#6b7280' }}>&times;</button>
                        </div>
                        <div style={{ padding: 24 }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                                {[['Firm Name', selectedFirmDetail.firm_name], ['Email', selectedFirmDetail.email], ['Phone', selectedFirmDetail.phone || 'N/A'], ['Registration No.', selectedFirmDetail.registration_no], ['Specialization', selectedFirmDetail.specialization], ['Primary Lawyer', selectedFirmDetail.primary_lawyer_name], ['Status', selectedFirmDetail.status], ['Submitted', formatDate(selectedFirmDetail.submitted_at)], ['Address', selectedFirmDetail.address || 'N/A'], ['City', selectedFirmDetail.city || 'N/A'], ['State', selectedFirmDetail.state || 'N/A'], ['GST No.', selectedFirmDetail.gst_no || 'N/A']].map(([label, val], i) => (
                                    <div key={i} style={{ padding: '8px 0', borderBottom: '1px solid #f9fafb' }}>
                                        <small style={{ color: '#9ca3af', fontWeight: 500, display: 'block' }}>{label}</small>
                                        <span style={{ fontWeight: 500, color: '#374151' }}>{val}</span>
                                    </div>
                                ))}
                            </div>
                            {selectedFirmDetail.status === 'pending' && (
                                <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
                                    <button className="btn-approve" onClick={() => { handleApproveLawFirm(selectedFirmDetail.id); setSelectedFirmDetail(null); }}>
                                        <i className="fas fa-check me-2"></i>Approve Law Firm
                                    </button>
                                    <button className="btn-reject" onClick={() => { handleRejectLawFirm(selectedFirmDetail.id); setSelectedFirmDetail(null); }}>
                                        <i className="fas fa-times me-2"></i>Reject Law Firm
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            <style>{`
                .admin-spinner { width: 36px; height: 36px; border: 4px solid #dbeafe; border-top-color: #1a3c8b; border-radius: 50%; animation: spin 0.8s linear infinite; }
                @keyframes spin { to { transform: rotate(360deg); } }
                .admin-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
                .admin-card-title { margin-top: 0; font-size: 1rem; font-weight: 600; color: #1a3c8b; margin-bottom: 16px; }
                .admin-activity-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f9fafb; }
                .admin-activity-avatar { width: 38px; height: 38px; border-radius: 50%; background: #1a3c8b; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; }
                .admin-table-wrap { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
                .admin-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
                .admin-table thead tr { background: #f8fafc; }
                .admin-table th { padding: 12px 16px; text-align: left; font-size: 0.8rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 2px solid #f0f0f0; }
                .admin-table td { padding: 12px 16px; border-bottom: 1px solid #f9fafb; vertical-align: middle; }
                .admin-table tr:hover td { background: #fafafa; }
                .admin-table-avatar { width: 34px; height: 34px; border-radius: 50%; background: #1a3c8b; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; flex-shrink: 0; }
                .admin-btn-sm { padding: 5px 10px; border-radius: 6px; border: 1px solid #e5e7eb; background: #f9fafb; color: #374151; font-size: 0.75rem; cursor: pointer; white-space: nowrap; }
                .admin-btn-sm:hover { background: #f3f4f6; }
                .admin-btn-sm.approve { background: #d1fae5; color: #065f46; border-color: #a7f3d0; }
                .admin-btn-sm.reject { background: #fee2e2; color: #991b1b; border-color: #fecaca; }
                .admin-btn-primary { background: #1a3c8b; color: white; border: none; padding: 9px 18px; border-radius: 8px; cursor: pointer; font-weight: 500; font-size: 0.875rem; display: inline-flex; align-items: center; }
                .admin-btn-primary:hover { background: #15347a; }
                .admin-label { display: block; font-size: 0.8rem; font-weight: 500; color: #374151; margin-bottom: 4px; }
                .admin-input { width: 100%; padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 0.875rem; color: #374151; box-sizing: border-box; }
                .admin-input:focus { outline: none; border-color: #1a3c8b; box-shadow: 0 0 0 2px rgba(26,60,139,0.1); }
                .admin-search-input { padding: 8px 14px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 0.875rem; width: 240px; }
            `}</style>
        </div>
    );
}

export default AdminDashboard;

















// import React, { useState, useEffect } from 'react';
// import { useNavigate } from 'react-router-dom';
// import API from '../services/api';

// function AdminDashboard() {
//     const navigate = useNavigate();
//     const [activeModule, setActiveModule] = useState('dashboard');
//     const [pendingClients, setPendingClients] = useState([]);
//     const [pendingLawFirms, setPendingLawFirms] = useState([]);
//     const [stats, setStats] = useState({});
//     const [loading, setLoading] = useState(true);
//     const [message, setMessage] = useState({ text: '', type: '' });
//     const [activeLawFirmTab, setActiveLawFirmTab] = useState('pending');

//     useEffect(() => {
//         // Check if user is admin
//         const user = JSON.parse(localStorage.getItem("user") || "{}");
//         if (user.role !== 'admin') {
//             navigate('/');
//             return;
//         }
//         loadData();
//     }, [navigate]);

//     const loadData = async () => {
//         setLoading(true);
//         try {
//             const [pendingClientsRes, statsRes, pendingLawFirmsRes] = await Promise.all([
//                 API.get('profiles/pending-clients/'),
//                 API.get('profiles/admin-dashboard/'),
//                 API.get('profiles/pending-lawfirms/')
//             ]);
//             setPendingClients(pendingClientsRes.data);
//             setStats(statsRes.data);
//             setPendingLawFirms(pendingLawFirmsRes.data);
//         } catch (error) {
//             console.error('Error loading data:', error);
//             if (error.response?.status === 401) {
//                 localStorage.clear();
//                 navigate('/');
//             }
//         } finally {
//             setLoading(false);
//         }
//     };

//     // Client Approve/Reject
//     const handleApproveClient = async (clientId) => {
//         try {
//             await API.post(`profiles/approve-client/${clientId}/`);
//             setMessage({ text: 'Client approved successfully!', type: 'success' });
//             await loadData();
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         } catch (error) {
//             console.error('Approval failed:', error);
//             setMessage({ text: 'Failed to approve client', type: 'error' });
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         }
//     };

//     const handleRejectClient = async (clientId) => {
//         const reason = prompt('Please enter rejection reason (will be shown to client):');
//         if (!reason) return;
        
//         try {
//             await API.post(`profiles/reject-client/${clientId}/`, { reason });
//             setMessage({ text: 'Client rejected successfully!', type: 'error' });
//             await loadData();
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         } catch (error) {
//             console.error('Rejection failed:', error);
//             setMessage({ text: 'Failed to reject client', type: 'error' });
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         }
//     };

//     // Law Firm Approve/Reject
//     const handleApproveLawFirm = async (firmId) => {
//         try {
//             await API.post(`profiles/approve-lawfirm/${firmId}/`);
//             setMessage({ text: 'Law firm approved successfully!', type: 'success' });
//             await loadData();
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         } catch (error) {
//             console.error('Approval failed:', error);
//             setMessage({ text: 'Failed to approve law firm', type: 'error' });
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         }
//     };

//     const handleRejectLawFirm = async (firmId) => {
//         const reason = prompt('Please enter rejection reason (will be shown to law firm):');
//         if (!reason) return;
        
//         try {
//             await API.post(`profiles/reject-lawfirm/${firmId}/`, { reason });
//             setMessage({ text: 'Law firm rejected successfully!', type: 'error' });
//             await loadData();
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         } catch (error) {
//             console.error('Rejection failed:', error);
//             setMessage({ text: 'Failed to reject law firm', type: 'error' });
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         }
//     };

//     const modules = [
//         { id: 'dashboard', name: 'Dashboard', icon: 'tachometer-alt' },
//         { id: 'client-onboarding', name: 'Client Onboarding', icon: 'user-clock', badge: pendingClients.length },
//         { id: 'lawfirm-onboarding', name: 'Law Firm Onboarding', icon: 'landmark', badge: pendingLawFirms.length },
//         { id: 'clients', name: 'Client Management', icon: 'users' },
//         { id: 'cases', name: 'Case Moderation', icon: 'folder-open' },
//         { id: 'lawfirms', name: 'Law Firm Management', icon: 'building' },
//         { id: 'court', name: 'Court Simulation', icon: 'gavel' },
//         { id: 'reports', name: 'Disputes & Reports', icon: 'flag' },
//         { id: 'analytics', name: 'Analytics & Logs', icon: 'chart-line' },
//         { id: 'settings', name: 'System Settings', icon: 'cog' },
//     ];

//     const renderContent = () => {
//         if (loading) return <div className="loading">Loading...</div>;

//         switch (activeModule) {
//             case 'client-onboarding':
//                 return (
//                     <div className="onboarding-module">
//                         <h3>Pending Client Onboarding Requests</h3>
//                         <div className="onboarding-grid">
//                             {pendingClients.length === 0 && (
//                                 <div className="no-data">
//                                     <i className="fas fa-check-circle" style={{ fontSize: '48px', color: '#28a745' }}></i>
//                                     <p>No pending client requests</p>
//                                 </div>
//                             )}
//                             {pendingClients.map(client => (
//                                 <div key={client.id} className="client-card">
//                                     <div className="client-header">
//                                         <span className="client-name">{client.name}</span>
//                                         <span className="client-badge pending">Pending</span>
//                                     </div>
//                                     <div className="client-info">
//                                         <div><i className="fas fa-envelope"></i> {client.email}</div>
//                                         <div><i className="fas fa-phone"></i> {client.phone || 'Not provided'}</div>
//                                         <div><i className="fas fa-id-card"></i> {client.id_proof_type}: {client.id_proof_number}</div>
//                                         <div><i className="fas fa-gavel"></i> {client.case_type} - {client.case_title}</div>
//                                         <div><i className="far fa-calendar-alt"></i> Submitted: {client.submitted_at}</div>
//                                     </div>
//                                     <div className="action-buttons">
//                                         <button className="btn-view" onClick={() => alert(`Case Details:\nTitle: ${client.case_title}\nType: ${client.case_type}`)}>
//                                             <i className="fas fa-eye"></i> Review
//                                         </button>
//                                         <button className="btn-approve" onClick={() => handleApproveClient(client.id)}>
//                                             <i className="fas fa-check"></i> Approve
//                                         </button>
//                                         <button className="btn-reject" onClick={() => handleRejectClient(client.id)}>
//                                             <i className="fas fa-times"></i> Reject
//                                         </button>
//                                     </div>
//                                 </div>
//                             ))}
//                         </div>
//                     </div>
//                 );
            
//             case 'lawfirm-onboarding':
//                 return (
//                     <div className="onboarding-module">
//                         <div className="lawfirm-tabs">
//                             <button 
//                                 className={`lawfirm-tab-btn ${activeLawFirmTab === 'pending' ? 'active' : ''}`}
//                                 onClick={() => setActiveLawFirmTab('pending')}
//                             >
//                                 Pending Requests ({pendingLawFirms.length})
//                             </button>
//                             <button 
//                                 className={`lawfirm-tab-btn ${activeLawFirmTab === 'approved' ? 'active' : ''}`}
//                                 onClick={() => setActiveLawFirmTab('approved')}
//                             >
//                                 Approved Firms
//                             </button>
//                         </div>
                        
//                         {activeLawFirmTab === 'pending' && (
//                             <>
//                                 <h3>Pending Law Firm Onboarding Requests</h3>
//                                 <div className="lawfirm-grid">
//                                     {pendingLawFirms.length === 0 && (
//                                         <div className="no-data">
//                                             <i className="fas fa-check-circle" style={{ fontSize: '48px', color: '#28a745' }}></i>
//                                             <p>No pending law firm requests</p>
//                                         </div>
//                                     )}
//                                     {pendingLawFirms.map(firm => (
//                                         <div key={firm.id} className="lawfirm-card">
//                                             <div className="client-header">
//                                                 <span className="client-name">{firm.firm_name}</span>
//                                                 <span className="client-badge pending">Pending Verification</span>
//                                             </div>
//                                             <div className="client-info">
//                                                 <div><i className="fas fa-envelope"></i> {firm.email}</div>
//                                                 <div><i className="fas fa-phone"></i> {firm.phone || 'Not provided'}</div>
//                                                 <div><i className="fas fa-id-card"></i> Reg No: {firm.registration_no}</div>
//                                                 <div><i className="fas fa-gavel"></i> Specialization: {firm.specialization}</div>
//                                                 <div><i className="fas fa-user-tie"></i> Primary Lawyer: {firm.primary_lawyer_name}</div>
//                                                 <div><i className="far fa-calendar-alt"></i> Submitted: {firm.submitted_at}</div>
//                                             </div>
//                                             <div className="action-buttons">
//                                                 <button className="btn-view" onClick={() => alert(`Firm Details:\nName: ${firm.firm_name}\nReg No: ${firm.registration_no}\nPrimary Lawyer: ${firm.primary_lawyer_name}\nSpecialization: ${firm.specialization}`)}>
//                                                     <i className="fas fa-eye"></i> Review
//                                                 </button>
//                                                 <button className="btn-approve" onClick={() => handleApproveLawFirm(firm.id)}>
//                                                     <i className="fas fa-check"></i> Approve
//                                                 </button>
//                                                 <button className="btn-reject" onClick={() => handleRejectLawFirm(firm.id)}>
//                                                     <i className="fas fa-times"></i> Reject
//                                                 </button>
//                                             </div>
//                                         </div>
//                                     ))}
//                                 </div>
//                             </>
//                         )}
                        
//                         {activeLawFirmTab === 'approved' && (
//                             <div className="approved-firms">
//                                 <h3>Approved Law Firms</h3>
//                                 <div className="lawfirm-grid">
//                                     <div className="no-data">
//                                         <i className="fas fa-check-circle" style={{ fontSize: '48px', color: '#28a745' }}></i>
//                                         <p>Approved law firms will appear here</p>
//                                     </div>
//                                 </div>
//                             </div>
//                         )}
//                     </div>
//                 );
            
//             case 'dashboard':
//                 return (
//                     <div className="dashboard-module">
//                         <div className="kpi-container">
//                             <div className="kpi-card">
//                                 <div className="kpi-value">{stats.totalClients || 0}</div>
//                                 <div className="kpi-label">Total Clients</div>
//                             </div>
//                             <div className="kpi-card">
//                                 <div className="kpi-value">{stats.totalLawFirms || 0}</div>
//                                 <div className="kpi-label">Total Law Firms</div>
//                             </div>
//                             <div className="kpi-card">
//                                 <div className="kpi-value">{stats.pendingClients || 0}</div>
//                                 <div className="kpi-label">Pending Clients</div>
//                             </div>
//                             <div className="kpi-card">
//                                 <div className="kpi-value">{stats.pendingLawFirms || 0}</div>
//                                 <div className="kpi-label">Pending Law Firms</div>
//                             </div>
//                             <div className="kpi-card">
//                                 <div className="kpi-value">{stats.activeCases || 0}</div>
//                                 <div className="kpi-label">Active Cases</div>
//                             </div>
//                             <div className="kpi-card">
//                                 <div className="kpi-value">{stats.approvedClients || 0}</div>
//                                 <div className="kpi-label">Approved Clients</div>
//                             </div>
//                         </div>
//                     </div>
//                 );
            
//             default:
//                 return (
//                     <div className="coming-soon">
//                         <h3>{modules.find(m => m.id === activeModule)?.name}</h3>
//                         <p>This module is under development.</p>
//                     </div>
//                 );
//         }
//     };

//     return (
//         <div className="admin-dashboard">
//             <div className="admin-sidebar">
//                 <div className="logo-container">
//                     <div className="logo">
//                         <i className="fas fa-balance-scale"></i>
//                         <h1>Advocare</h1>
//                     </div>
//                 </div>
//                 <div className="nav-menu">
//                     {modules.map(module => (
//                         <div
//                             key={module.id}
//                             className={`nav-item ${activeModule === module.id ? 'active' : ''}`}
//                             onClick={() => setActiveModule(module.id)}
//                         >
//                             <i className={`fas fa-${module.icon}`}></i>
//                             <span>{module.name}</span>
//                             {module.badge > 0 && <span className="badge">{module.badge}</span>}
//                         </div>
//                     ))}
//                 </div>
//             </div>

//             <div className="admin-main">
//                 <header className="admin-header">
//                     <div className="header-left">
//                         <h2>{modules.find(m => m.id === activeModule)?.name}</h2>
//                     </div>
//                     <div className="header-right">
//                         <div className="admin-profile">
//                             <div className="admin-avatar">AD</div>
//                             <div className="admin-info">
//                                 <h4>Admin User</h4>
//                                 <p>System Administrator</p>
//                             </div>
//                         </div>
//                         <button className="btn-outline" onClick={() => {
//                             localStorage.clear();
//                             navigate('/');
//                         }}>
//                             <i className="fas fa-sign-out-alt"></i> Logout
//                         </button>
//                     </div>
//                 </header>

//                 {message.text && (
//                     <div className={`alert alert-${message.type === 'success' ? 'success' : 'danger'}`}>
//                         {message.text}
//                     </div>
//                 )}

//                 <div className="content-area">
//                     {renderContent()}
//                 </div>

//                 <footer className="admin-footer">
//                     <p>Advocare - Smart Legal Case Management System | Admin Portal | © 2025</p>
//                 </footer>
//             </div>
//         </div>
//     );
// }

// export default AdminDashboard;









































// import React, { useState, useEffect } from 'react';
// import { useNavigate } from 'react-router-dom';
// import API from '../services/api';

// function AdminDashboard() {
//     const navigate = useNavigate();
//     const [activeModule, setActiveModule] = useState('onboarding');
//     const [pendingClients, setPendingClients] = useState([]);
//     const [stats, setStats] = useState({});
//     const [loading, setLoading] = useState(true);
//     const [message, setMessage] = useState({ text: '', type: '' });

//     useEffect(() => {
//         const loadData = async () => {
//             setLoading(true);
//             try {
//                 if (activeModule === 'onboarding') {
//                     const res = await API.get('profiles/pending-clients/');
//                     setPendingClients(res.data);
//                 } else if (activeModule === 'dashboard') {
//                     const res = await API.get('profiles/admin-dashboard/');
//                     setStats(res.data);
//                 }
//             } catch (error) {
//                 console.error('Error loading data:', error);
//                 if (error.response?.status === 401) {
//                     navigate('/');
//                 }
//             } finally {
//                 setLoading(false);
//             }
//         };
//         loadData();
//     }, [activeModule, navigate]);

//     const handleApprove = async (clientId) => {
//         try {
//             await API.post(`profiles/approve-client/${clientId}/`);
//             setMessage({ text: 'Client approved successfully!', type: 'success' });
            
//             const res = await API.get('profiles/pending-clients/');
//             setPendingClients(res.data);
            
//             const statsRes = await API.get('profiles/admin-dashboard/');
//             setStats(statsRes.data);
            
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         } catch (error) {
//             console.error('Approval failed:', error);
//             setMessage({ text: 'Failed to approve client', type: 'error' });
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         }
//     };

//     const handleReject = async (clientId) => {
//         const reason = prompt('Please enter rejection reason (will be shown to client):');
//         if (!reason) return;
        
//         try {
//             await API.post(`profiles/reject-client/${clientId}/`, { reason });
//             setMessage({ text: 'Client rejected successfully!', type: 'error' });
            
//             const res = await API.get('profiles/pending-clients/');
//             setPendingClients(res.data);
            
//             const statsRes = await API.get('profiles/admin-dashboard/');
//             setStats(statsRes.data);
            
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         } catch (error) {
//             console.error('Rejection failed:', error);
//             setMessage({ text: 'Failed to reject client', type: 'error' });
//             setTimeout(() => setMessage({ text: '', type: '' }), 3000);
//         }
//     };

//     const modules = [
//         { id: 'dashboard', name: 'Dashboard', icon: 'tachometer-alt' },
//         { id: 'onboarding', name: 'Client Onboarding', icon: 'user-clock', badge: pendingClients.length },
//         { id: 'clients', name: 'Client Management', icon: 'users' },
//         { id: 'cases', name: 'Case Moderation', icon: 'folder-open' },
//         { id: 'lawfirms', name: 'Law Firm Verification', icon: 'landmark' },
//         { id: 'lawyers', name: 'Lawyer Verification', icon: 'user-tie' },
//         { id: 'court', name: 'Court Simulation', icon: 'gavel' },
//         { id: 'reports', name: 'Disputes & Reports', icon: 'flag' },
//         { id: 'analytics', name: 'Analytics & Logs', icon: 'chart-line' },
//         { id: 'settings', name: 'System Settings', icon: 'cog' },
//     ];

//     const renderContent = () => {
//         if (loading) return <div className="loading">Loading...</div>;

//         switch (activeModule) {
//             case 'onboarding':
//                 return (
//                     <div className="onboarding-module">
//                         <h3>Pending Client Onboarding Requests</h3>
//                         <div className="onboarding-grid">
//                             {pendingClients.length === 0 && (
//                                 <div className="no-data">
//                                     <i className="fas fa-check-circle" style={{ fontSize: '48px', color: '#28a745' }}></i>
//                                     <p>No pending requests</p>
//                                 </div>
//                             )}
//                             {pendingClients.map(client => (
//                                 <div key={client.id} className="client-card">
//                                     <div className="client-header">
//                                         <span className="client-name">{client.name}</span>
//                                         <span className="client-badge pending">Pending</span>
//                                     </div>
//                                     <div className="client-info">
//                                         <div><i className="fas fa-envelope"></i> {client.email}</div>
//                                         <div><i className="fas fa-phone"></i> {client.phone || 'Not provided'}</div>
//                                         <div><i className="fas fa-id-card"></i> {client.id_proof_type}: {client.id_proof_number}</div>
//                                         <div><i className="fas fa-gavel"></i> {client.case_type} - {client.case_title}</div>
//                                         <div><i className="far fa-calendar-alt"></i> Submitted: {client.submitted_at}</div>
//                                     </div>
//                                     <div className="action-buttons">
//                                         <button className="btn-view" onClick={() => alert(`Case Details:\nTitle: ${client.case_title}\nType: ${client.case_type}`)}>
//                                             <i className="fas fa-eye"></i> Review
//                                         </button>
//                                         <button className="btn-approve" onClick={() => handleApprove(client.id)}>
//                                             <i className="fas fa-check"></i> Approve
//                                         </button>
//                                         <button className="btn-reject" onClick={() => handleReject(client.id)}>
//                                             <i className="fas fa-times"></i> Reject
//                                         </button>
//                                     </div>
//                                 </div>
//                             ))}
//                         </div>
//                     </div>
//                 );
//             case 'dashboard':
//                 return (
//                     <div className="dashboard-module">
//                         <div className="kpi-container">
//                             <div className="kpi-card">
//                                 <div className="kpi-value">{stats.totalClients || 0}</div>
//                                 <div className="kpi-label">Total Clients</div>
//                             </div>
//                             <div className="kpi-card">
//                                 <div className="kpi-value">{stats.activeCases || 0}</div>
//                                 <div className="kpi-label">Active Cases</div>
//                             </div>
//                             <div className="kpi-card">
//                                 <div className="kpi-value">{stats.pendingOnboarding || 0}</div>
//                                 <div className="kpi-label">Pending Onboarding</div>
//                             </div>
//                             <div className="kpi-card">
//                                 <div className="kpi-value">{stats.approvedClients || 0}</div>
//                                 <div className="kpi-label">Approved Clients</div>
//                             </div>
//                         </div>
//                     </div>
//                 );
//             default:
//                 return (
//                     <div className="coming-soon">
//                         <h3>{modules.find(m => m.id === activeModule)?.name}</h3>
//                         <p>This module is under development.</p>
//                     </div>
//                 );
//         }
//     };

//     return (
//         <div className="admin-dashboard">
//             <div className="admin-sidebar">
//                 <div className="logo-container">
//                     <div className="logo">
//                         <i className="fas fa-balance-scale"></i>
//                         <h1>Advocare</h1>
//                     </div>
//                 </div>
//                 <div className="nav-menu">
//                     {modules.map(module => (
//                         <div
//                             key={module.id}
//                             className={`nav-item ${activeModule === module.id ? 'active' : ''}`}
//                             onClick={() => setActiveModule(module.id)}
//                         >
//                             <i className={`fas fa-${module.icon}`}></i>
//                             <span>{module.name}</span>
//                             {module.badge > 0 && <span className="badge">{module.badge}</span>}
//                         </div>
//                     ))}
//                 </div>
//             </div>

//             <div className="admin-main">
//                 <header className="admin-header">
//                     <div className="header-left">
//                         <h2>{modules.find(m => m.id === activeModule)?.name}</h2>
//                     </div>
//                     <div className="header-right">
//                         <div className="admin-profile">
//                             <div className="admin-avatar">AD</div>
//                             <div className="admin-info">
//                                 <h4>Admin User</h4>
//                                 <p>System Administrator</p>
//                             </div>
//                         </div>
//                         <button className="btn-outline" onClick={() => {
//                             localStorage.clear();
//                             navigate('/');
//                         }}>
//                             <i className="fas fa-sign-out-alt"></i> Logout
//                         </button>
//                     </div>
//                 </header>

//                 {message.text && (
//                     <div className={`alert alert-${message.type === 'success' ? 'success' : 'danger'}`}>
//                         {message.text}
//                     </div>
//                 )}

//                 <div className="content-area">
//                     {renderContent()}
//                 </div>

//                 <footer className="admin-footer">
//                     <p>Advocare - Smart Legal Case Management System | Admin Portal | © 2025</p>
//                 </footer>
//             </div>
//         </div>
//     );
// }

// export default AdminDashboard;






































// import React, { useState, useEffect } from 'react';
// import { useNavigate } from 'react-router-dom';
// import API from '../services/api';

// function AdminDashboard() {
//   const navigate = useNavigate();
//   const [activeModule, setActiveModule] = useState('onboarding');
//   const [pendingClients, setPendingClients] = useState([]);
//   const [stats, setStats] = useState({});
//   const [loading, setLoading] = useState(true);

//   // Load data based on active module
//   useEffect(() => {
//     const loadData = async () => {
//       setLoading(true);
//       try {
//         if (activeModule === 'onboarding') {
//           const res = await API.get('profiles/pending-clients/');
//           setPendingClients(res.data);
//         } else if (activeModule === 'dashboard') {
//           const res = await API.get('profiles/admin-dashboard/');
//           setStats(res.data);
//         }
//       } catch (error) {
//         console.error('Error loading data:', error);
//       } finally {
//         setLoading(false);
//       }
//     };
//     loadData();
//   }, [activeModule]);

//   const handleApprove = async (clientId) => {
//     try {
//       await API.post(`profiles/approve-client/${clientId}/`);
//       const res = await API.get('profiles/pending-clients/');
//       setPendingClients(res.data);
//       alert('Client approved successfully');
//     } catch (error) {
//       console.error('Approval failed:', error);
//       alert('Failed to approve client');
//     }
//   };

//   const handleReject = async (clientId) => {
//     try {
//       await API.post(`profiles/reject-client/${clientId}/`);
//       const res = await API.get('profiles/pending-clients/');
//       setPendingClients(res.data);
//       alert('Client rejected successfully');
//     } catch (error) {
//       console.error('Rejection failed:', error);
//       alert('Failed to reject client');
//     }
//   };

//   const modules = [
//     { id: 'dashboard', name: 'Dashboard', icon: 'tachometer-alt' },
//     { id: 'onboarding', name: 'Client Onboarding', icon: 'user-clock', badge: pendingClients.length },
//     { id: 'clients', name: 'Client Management', icon: 'users' },
//     { id: 'cases', name: 'Case Moderation', icon: 'folder-open' },
//     { id: 'lawfirms', name: 'Law Firm Verification', icon: 'landmark' },
//     { id: 'lawyers', name: 'Lawyer Verification', icon: 'user-tie' },
//     { id: 'court', name: 'Court Simulation', icon: 'gavel' },
//     { id: 'reports', name: 'Disputes & Reports', icon: 'flag' },
//     { id: 'analytics', name: 'Analytics & Logs', icon: 'chart-line' },
//     { id: 'settings', name: 'System Settings', icon: 'cog' },
//   ];

//   const renderContent = () => {
//     if (loading) return <div className="loading">Loading...</div>;

//     switch (activeModule) {
//       case 'onboarding':
//         return (
//           <div className="onboarding-module">
//             <h3>Pending Client Onboarding Requests</h3>
//             <div className="onboarding-grid">
//               {pendingClients.length === 0 && <p>No pending requests</p>}
//               {pendingClients.map(client => (
//                 <div key={client.id} className="client-card">
//                   <div className="client-header">
//                     <span className="client-name">{client.name}</span>
//                     <span className="client-badge">Pending</span>
//                   </div>
//                   <div className="client-info">
//                     <div><i className="fas fa-envelope"></i> {client.email}</div>
//                     <div><i className="fas fa-phone"></i> {client.phone || 'Not provided'}</div>
//                     <div><i className="fas fa-id-card"></i> {client.id_proof_type}: {client.id_proof_number}</div>
//                   </div>
//                   <div className="action-buttons">
//                     <button className="btn-view" onClick={() => alert('View details not implemented')}>
//                       <i className="fas fa-eye"></i> Review
//                     </button>
//                     <button className="btn-approve" onClick={() => handleApprove(client.id)}>
//                       <i className="fas fa-check"></i> Approve
//                     </button>
//                     <button className="btn-reject" onClick={() => handleReject(client.id)}>
//                       <i className="fas fa-times"></i> Reject
//                     </button>
//                   </div>
//                 </div>
//               ))}
//             </div>
//           </div>
//         );
//       case 'dashboard':
//         return (
//           <div className="dashboard-module">
//             <div className="kpi-container">
//               <div className="kpi-card">
//                 <div className="kpi-value">{stats.totalClients || 0}</div>
//                 <div className="kpi-label">Total Clients</div>
//               </div>
//               <div className="kpi-card">
//                 <div className="kpi-value">{stats.activeCases || 0}</div>
//                 <div className="kpi-label">Active Cases</div>
//               </div>
//               <div className="kpi-card">
//                 <div className="kpi-value">{stats.pendingOnboarding || 0}</div>
//                 <div className="kpi-label">Pending Onboarding</div>
//               </div>
//             </div>
//           </div>
//         );
//       default:
//         return (
//           <div className="coming-soon">
//             <h3>{modules.find(m => m.id === activeModule)?.name}</h3>
//             <p>This module is under development.</p>
//           </div>
//         );
//     }
//   };

//   return (
//     <div className="admin-dashboard">
//       <div className="admin-sidebar">
//         <div className="logo-container">
//           <div className="logo">
//             <i className="fas fa-balance-scale"></i>
//             <h1>Advocare</h1>
//           </div>
//         </div>
//         <div className="nav-menu">
//           {modules.map(module => (
//             <div
//               key={module.id}
//               className={`nav-item ${activeModule === module.id ? 'active' : ''}`}
//               onClick={() => setActiveModule(module.id)}
//             >
//               <i className={`fas fa-${module.icon}`}></i>
//               <span>{module.name}</span>
//               {module.badge > 0 && <span className="badge">{module.badge}</span>}
//             </div>
//           ))}
//         </div>
//       </div>

//       <div className="admin-main">
//         <header className="admin-header">
//           <div className="header-left">
//             <h2>{modules.find(m => m.id === activeModule)?.name}</h2>
//           </div>
//           <div className="header-right">
//             <div className="admin-profile">
//               <div className="admin-avatar">AD</div>
//               <div className="admin-info">
//                 <h4>Admin User</h4>
//                 <p>System Administrator</p>
//               </div>
//             </div>
//             <button className="btn btn-outline" onClick={() => {
//               localStorage.clear();
//               navigate('/');
//             }}>
//               <i className="fas fa-sign-out-alt"></i> Logout
//             </button>
//           </div>
//         </header>

//         <div className="content-area">
//           {renderContent()}
//         </div>

//         <footer className="admin-footer">
//           <p>Advocare - Smart Legal Case Management System | Admin Portal | © 2025</p>
//         </footer>
//       </div>
//     </div>
//   );
// }

// export default AdminDashboard;


































// import React, { useState, useEffect } from 'react';
// import { useNavigate } from 'react-router-dom';
// import API from '../services/api';

// function AdminDashboard() {
//   const navigate = useNavigate();
//   const [activeModule, setActiveModule] = useState('onboarding');
//   const [pendingClients, setPendingClients] = useState([]);
//   const [stats, setStats] = useState({});
//   const [loading, setLoading] = useState(true);

//   // Load data based on active module (no redirect checks)
//   useEffect(() => {
//     const loadData = async () => {
//       setLoading(true);
//       try {
//         if (activeModule === 'onboarding') {
//           const res = await API.get('profiles/pending-clients/');
//           setPendingClients(res.data);
//         } else if (activeModule === 'dashboard') {
//           const res = await API.get('admin/dashboard/');
//           setStats(res.data);
//         }
//       } catch (error) {
//         console.error('Error loading data:', error);
//       } finally {
//         setLoading(false);
//       }
//     };
//     loadData();
//   }, [activeModule]);

//   const handleApprove = async (clientId) => {
//     try {
//       await API.post(`profiles/approve-client/${clientId}/`);
//       const res = await API.get('profiles/pending-clients/');
//       setPendingClients(res.data);
//       alert('Client approved');
//     } catch (error) {
//       console.error('Approval failed:', error);
//       alert('Failed to approve client');
//     }
//   };

//   const handleReject = async (clientId) => {
//     try {
//       await API.post(`profiles/reject-client/${clientId}/`);
//       const res = await API.get('profiles/pending-clients/');
//       // For dashboard stats:
//       const res = await API.get('profiles/admin-dashboard/');  // Add this
//       setPendingClients(res.data);
//       alert('Client rejected');
//     } catch (error) {
//       console.error('Rejection failed:', error);
//       alert('Failed to reject client');
//     }
//   };

//   const modules = [
//     { id: 'dashboard', name: 'Dashboard', icon: 'tachometer-alt' },
//     { id: 'onboarding', name: 'Client Onboarding', icon: 'user-clock', badge: pendingClients.length },
//     { id: 'clients', name: 'Client Management', icon: 'users' },
//     { id: 'cases', name: 'Case Moderation', icon: 'folder-open' },
//     { id: 'lawfirms', name: 'Law Firm Verification', icon: 'landmark' },
//     { id: 'lawyers', name: 'Lawyer Verification', icon: 'user-tie' },
//     { id: 'court', name: 'Court Simulation', icon: 'gavel' },
//     { id: 'reports', name: 'Disputes & Reports', icon: 'flag' },
//     { id: 'analytics', name: 'Analytics & Logs', icon: 'chart-line' },
//     { id: 'settings', name: 'System Settings', icon: 'cog' },
//   ];

//   const renderContent = () => {
//     if (loading) return <div className="loading">Loading...</div>;

//     switch (activeModule) {
//       case 'onboarding':
//         return (
//           <div className="onboarding-module">
//             <h3>Pending Client Onboarding Requests</h3>
//             <div className="onboarding-grid">
//               {pendingClients.length === 0 && <p>No pending requests</p>}
//               {pendingClients.map(client => (
//                 <div key={client.id} className="client-card">
//                   <div className="client-header">
//                     <span className="client-name">{client.name}</span>
//                     <span className="client-badge">Pending</span>
//                   </div>
//                   <div className="client-info">
//                     <div><i className="fas fa-envelope"></i> {client.email}</div>
//                     <div><i className="fas fa-phone"></i> {client.phone || 'Not provided'}</div>
//                     <div><i className="fas fa-id-card"></i> {client.id_proof_type}: {client.id_proof_number}</div>
//                   </div>
//                   <div className="action-buttons">
//                     <button className="btn-view" onClick={() => alert('View details not implemented')}>
//                       <i className="fas fa-eye"></i> Review
//                     </button>
//                     <button className="btn-approve" onClick={() => handleApprove(client.id)}>
//                       <i className="fas fa-check"></i> Approve
//                     </button>
//                     <button className="btn-reject" onClick={() => handleReject(client.id)}>
//                       <i className="fas fa-times"></i> Reject
//                     </button>
//                   </div>
//                 </div>
//               ))}
//             </div>
//           </div>
//         );
//       case 'dashboard':
//         return (
//           <div className="dashboard-module">
//             <div className="kpi-container">
//               <div className="kpi-card">
//                 <div className="kpi-value">{stats.totalClients || 0}</div>
//                 <div className="kpi-label">Total Clients</div>
//               </div>
//               <div className="kpi-card">
//                 <div className="kpi-value">{stats.activeCases || 0}</div>
//                 <div className="kpi-label">Active Cases</div>
//               </div>
//               <div className="kpi-card">
//                 <div className="kpi-value">{stats.pendingOnboarding || 0}</div>
//                 <div className="kpi-label">Pending Onboarding</div>
//               </div>
//             </div>
//           </div>
//         );
//       default:
//         return (
//           <div className="coming-soon">
//             <h3>{modules.find(m => m.id === activeModule)?.name}</h3>
//             <p>This module is under development.</p>
//           </div>
//         );
//     }
//   };

//   return (
//     <div className="admin-dashboard">
//       <div className="admin-sidebar">
//         <div className="logo-container">
//           <div className="logo">
//             <i className="fas fa-balance-scale"></i>
//             <h1>Advocare</h1>
//           </div>
//         </div>
//         <div className="nav-menu">
//           {modules.map(module => (
//             <div
//               key={module.id}
//               className={`nav-item ${activeModule === module.id ? 'active' : ''}`}
//               onClick={() => setActiveModule(module.id)}
//             >
//               <i className={`fas fa-${module.icon}`}></i>
//               <span>{module.name}</span>
//               {module.badge > 0 && <span className="badge">{module.badge}</span>}
//             </div>
//           ))}
//         </div>
//       </div>

//       <div className="admin-main">
//         <header className="admin-header">
//           <div className="header-left">
//             <h2>{modules.find(m => m.id === activeModule)?.name}</h2>
//           </div>
//           <div className="header-right">
//             <div className="admin-profile">
//               <div className="admin-avatar">AD</div>
//               <div className="admin-info">
//                 <h4>Admin User</h4>
//                 <p>System Administrator</p>
//               </div>
//             </div>
//             <button className="btn btn-outline" onClick={() => {
//               localStorage.clear();
//               navigate('/');
//             }}>
//               <i className="fas fa-sign-out-alt"></i> Logout
//             </button>
//           </div>
//         </header>

//         <div className="content-area">
//           {renderContent()}
//         </div>

//         <footer className="admin-footer">
//           <p>Advocare - Smart Legal Case Management System | Admin Portal | © 2025</p>
//         </footer>
//       </div>
//     </div>
//   );
// }

// export default AdminDashboard;