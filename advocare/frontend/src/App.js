import { BrowserRouter, Routes, Route } from "react-router-dom";
import Auth from "./pages/Auth";
import Homepage from "./pages/Homepage";
import ClientOnboarding from "./pages/ClientOnboarding";
import PendingOnboarding from "./pages/PendingOnboarding";
import ClientPortal from "./pages/ClientPortal";
import LawfirmOnboarding from "./pages/LawfirmOnboarding";
import LawfirmPendingOnboarding from "./pages/LawfirmPendingOnboarding";
import LawfirmPortal from "./pages/LawfirmPortal";
import AdminDashboard from "./pages/AdminDashboard";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
    return ( <
        BrowserRouter >
        <
        Routes > { /* Public Routes */ } <
        Route path = "/"
        element = { < Auth / > }
        /> <
        Route path = "/home"
        element = { < Homepage / > }
        />

        { /* Client Routes */ } <
        Route path = "/client-onboarding"
        element = { < ClientOnboarding / > }
        /> <
        Route path = "/pending-onboarding"
        element = { < PendingOnboarding / > }
        /> <
        Route path = "/client-portal"
        element = { <
            ProtectedRoute requiredRole = "client" >
            <
            ClientPortal / >
            <
            /ProtectedRoute>
        }
        />

        { /* Law Firm Routes */ } <
        Route path = "/lawfirm-onboarding"
        element = { < LawfirmOnboarding / > }
        /> <
        Route path = "/lawfirm-pending-onboarding"
        element = { < LawfirmPendingOnboarding / > }
        /> <
        Route path = "/lawfirm-portal"
        element = { <
            ProtectedRoute requiredRole = "lawfirm" >
            <
            LawfirmPortal / >
            <
            /ProtectedRoute>
        }
        />

        { /* Admin Routes */ } <
        Route path = "/admin-dashboard"
        element = { <
            ProtectedRoute requiredRole = "admin" >
            <
            AdminDashboard / >
            <
            /ProtectedRoute>
        }
        /> <
        /Routes> <
        /BrowserRouter>
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