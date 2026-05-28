import axios from "axios";

const API = axios.create({
    baseURL: "/api/",
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add token
API.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("access_token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle 401 errors
API.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Use traditional check instead of optional chaining
        if (error.response && error.response.status === 401) {
            localStorage.clear();
            window.location.href = "/";
        }
        return Promise.reject(error);
    }
);

// For file uploads - dynamic content type
API.interceptors.request.use((config) => {
    if (config.data instanceof FormData) {
        config.headers['Content-Type'] = 'multipart/form-data';
    }
    return config;
});

export default API;