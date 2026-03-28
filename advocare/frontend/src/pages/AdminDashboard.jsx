import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';

function AdminDashboard() {
  const navigate = useNavigate();
  const [activeModule, setActiveModule] = useState('onboarding');
  const [pendingClients, setPendingClients] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  // Load data based on active module (no redirect checks)
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        if (activeModule === 'onboarding') {
          const res = await API.get('profiles/pending-clients/');
          setPendingClients(res.data);
        } else if (activeModule === 'dashboard') {
          const res = await API.get('admin/dashboard/');
          setStats(res.data);
        }
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [activeModule]);

  const handleApprove = async (clientId) => {
    try {
      await API.post(`profiles/approve-client/${clientId}/`);
      const res = await API.get('profiles/pending-clients/');
      setPendingClients(res.data);
      alert('Client approved');
    } catch (error) {
      console.error('Approval failed:', error);
      alert('Failed to approve client');
    }
  };

  const handleReject = async (clientId) => {
    try {
      await API.post(`profiles/reject-client/${clientId}/`);
      const res = await API.get('profiles/pending-clients/');
      setPendingClients(res.data);
      alert('Client rejected');
    } catch (error) {
      console.error('Rejection failed:', error);
      alert('Failed to reject client');
    }
  };

  const modules = [
    { id: 'dashboard', name: 'Dashboard', icon: 'tachometer-alt' },
    { id: 'onboarding', name: 'Client Onboarding', icon: 'user-clock', badge: pendingClients.length },
    { id: 'clients', name: 'Client Management', icon: 'users' },
    { id: 'cases', name: 'Case Moderation', icon: 'folder-open' },
    { id: 'lawfirms', name: 'Law Firm Verification', icon: 'landmark' },
    { id: 'lawyers', name: 'Lawyer Verification', icon: 'user-tie' },
    { id: 'court', name: 'Court Simulation', icon: 'gavel' },
    { id: 'reports', name: 'Disputes & Reports', icon: 'flag' },
    { id: 'analytics', name: 'Analytics & Logs', icon: 'chart-line' },
    { id: 'settings', name: 'System Settings', icon: 'cog' },
  ];

  const renderContent = () => {
    if (loading) return <div className="loading">Loading...</div>;

    switch (activeModule) {
      case 'onboarding':
        return (
          <div className="onboarding-module">
            <h3>Pending Client Onboarding Requests</h3>
            <div className="onboarding-grid">
              {pendingClients.length === 0 && <p>No pending requests</p>}
              {pendingClients.map(client => (
                <div key={client.id} className="client-card">
                  <div className="client-header">
                    <span className="client-name">{client.name}</span>
                    <span className="client-badge">Pending</span>
                  </div>
                  <div className="client-info">
                    <div><i className="fas fa-envelope"></i> {client.email}</div>
                    <div><i className="fas fa-phone"></i> {client.phone || 'Not provided'}</div>
                    <div><i className="fas fa-id-card"></i> {client.id_proof_type}: {client.id_proof_number}</div>
                  </div>
                  <div className="action-buttons">
                    <button className="btn-view" onClick={() => alert('View details not implemented')}>
                      <i className="fas fa-eye"></i> Review
                    </button>
                    <button className="btn-approve" onClick={() => handleApprove(client.id)}>
                      <i className="fas fa-check"></i> Approve
                    </button>
                    <button className="btn-reject" onClick={() => handleReject(client.id)}>
                      <i className="fas fa-times"></i> Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      case 'dashboard':
        return (
          <div className="dashboard-module">
            <div className="kpi-container">
              <div className="kpi-card">
                <div className="kpi-value">{stats.totalClients || 0}</div>
                <div className="kpi-label">Total Clients</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-value">{stats.activeCases || 0}</div>
                <div className="kpi-label">Active Cases</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-value">{stats.pendingOnboarding || 0}</div>
                <div className="kpi-label">Pending Onboarding</div>
              </div>
            </div>
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
          <div className="logo">
            <i className="fas fa-balance-scale"></i>
            <h1>Advocare</h1>
          </div>
        </div>
        <div className="nav-menu">
          {modules.map(module => (
            <div
              key={module.id}
              className={`nav-item ${activeModule === module.id ? 'active' : ''}`}
              onClick={() => setActiveModule(module.id)}
            >
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
              <div className="admin-avatar">AD</div>
              <div className="admin-info">
                <h4>Admin User</h4>
                <p>System Administrator</p>
              </div>
            </div>
            <button className="btn btn-outline" onClick={() => {
              localStorage.clear();
              navigate('/');
            }}>
              <i className="fas fa-sign-out-alt"></i> Logout
            </button>
          </div>
        </header>

        <div className="content-area">
          {renderContent()}
        </div>

        <footer className="admin-footer">
          <p>Advocare - Smart Legal Case Management System | Admin Portal | © 2025</p>
        </footer>
      </div>
    </div>
  );
}

export default AdminDashboard;