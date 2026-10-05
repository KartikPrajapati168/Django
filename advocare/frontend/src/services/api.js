import axios from "axios";

console.log("🔥 API URL:", process.env.REACT_APP_API_URL);

const API = axios.create({
    baseURL: process.env.REACT_APP_API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

console.log("🔥 Axios Base URL:", API.defaults.baseURL);

export default API;