import axios from "axios";

console.log("🔥 API URL:", process.env.REACT_APP_API_URL);

const API = axios.create({
    baseURL: process.env.REACT_APP_API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

API.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("access_token");

        console.log("========== API REQUEST ==========");
        console.log("URL:", config.baseURL + config.url);
        console.log("TOKEN EXISTS:", !!token);

        if (token) {
            config.headers = config.headers || {};
            config.headers.Authorization = `Bearer ${token}`;

            console.log("✅ Authorization header added");
        } else {
            console.error("❌ access_token NOT FOUND in localStorage");
        }

        console.log("=================================");

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

API.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error(
            "❌ API ERROR:",
            error.response?.status,
            error.config?.url
        );

        // Abhi debugging ke time automatic logout mat karo
        return Promise.reject(error);
    }
);

export default API;