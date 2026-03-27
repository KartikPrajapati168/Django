import { BrowserRouter, Routes, Route } from "react-router-dom";
import Auth from "./pages/Auth";
import ClientOnboarding from "./pages/ClientOnboarding";
import LawfirmOnboarding from "./pages/LawfirmOnboarding";
import ClientDashboard from "./pages/ClientDashboard";
import LawfirmDashboard from "./pages/LawfirmDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Auth />} />
        <Route path="/client-onboarding" element={<ClientOnboarding />} />
        <Route path="/lawfirm-onboarding" element={<LawfirmOnboarding />} />
        <Route
  path="/client-dashboard"
  element={
    <ProtectedRoute>
      <ClientDashboard />
    </ProtectedRoute>
  }
/>
        <Route
  path="/lawfirm-dashboard"
  element={
    <ProtectedRoute>
      <LawfirmDashboard />
    </ProtectedRoute>
  }
/>
        <Route
  path="/admin-dashboard"
  element={
    <ProtectedRoute>
      <AdminDashboard />
    </ProtectedRoute>
  }
/>
      </Routes>
    </BrowserRouter>
  );
}

export default App;














// import logo from './logo.svg';
// import './App.css';

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }

// export default App;
