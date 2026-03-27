import React, { useEffect, useState } from "react";
import API from "../services/api";

function AdminDashboard() {
  const [clients, setClients] = useState([]);

  const fetchClients = async () => {
    const res = await API.get("pending-clients/");
    setClients(res.data);
  };

  const approve = async (id) => {
    await API.post(`approve-client/${id}/`);
    fetchClients();
  };

  const reject = async (id) => {
    await API.post(`reject-client/${id}/`);
    fetchClients();
  };

  useEffect(() => {
    fetchClients();
  }, []);

  return (
    <div>
      <h2>Admin Dashboard</h2>

      {clients.map((c) => (
        <div key={c.id}>
          <p>{c.user.email}</p>

          <button onClick={() => approve(c.id)}>Approve</button>
          <button onClick={() => reject(c.id)}>Reject</button>
        </div>
      ))}
    </div>
  );
}

export default AdminDashboard;