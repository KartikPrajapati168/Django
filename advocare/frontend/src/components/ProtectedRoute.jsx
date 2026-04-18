// import { Navigate } from "react-router-dom";

// const ProtectedRoute = ({ children }) => {
//   const token = localStorage.getItem("access_token");

//   if (!token) {
//     return <Navigate to="/" />;
//   }

//   return children;
// };

// export default ProtectedRoute;



import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children, requiredRole }) => {
    const token = localStorage.getItem("access_token");
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    if (!token) {
        return <Navigate to="/" replace />;
    }

    if (requiredRole && user.role !== requiredRole) {
        return <Navigate to="/" replace />;
    }

    return children;
};

export default ProtectedRoute;