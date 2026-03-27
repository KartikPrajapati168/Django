import { useEffect } from "react";
import API from "../services/api";

function ClientDashboard() {

  useEffect(() => {
    const check = async () => {
      try {
        await API.get("client-dashboard/");
      } catch {
        alert("Unauthorized");
        window.location.href = "/";
      }
    };

    check();
  }, []);

  return <h2>Client Dashboard</h2>;
}

export default ClientDashboard;