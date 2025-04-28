import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { useUserAuthStore } from "../stores/userAuthStore";

const baseURL = import.meta.env.MODE === 'production'? import.meta.env.VITE_BACKEND_URL_PROD : import.meta.env.VITE_BACKEND_URL_DEV

export const defaultAxiosInstance = axios.create({
  baseURL,
  withCredentials: true,
});

export const axiosInstance = axios.create({
  baseURL,
  withCredentials: true,
});


// request interceptor
axiosInstance.interceptors.request.use(
  async (config) => {
    const userAuthStore = useUserAuthStore();
    const accessToken = userAuthStore.accessToken;

    if (accessToken) {
      const bufferTime = 120
      const serverDateTime = await userAuthStore.getCurrentServerTime()
      userAuthStore.currentDate = serverDateTime['current_date']
      const currentTimestamp = serverDateTime['timestamp']
      
      let tokenExpTimestamp = jwtDecode(accessToken).exp || 0
      tokenExpTimestamp = tokenExpTimestamp;
      if ((currentTimestamp + bufferTime) >= tokenExpTimestamp) {
        try {
          await userAuthStore.UpdateToken()
          config.headers.Authorization = `Bearer ${userAuthStore.accessToken}`;
        }
        catch (e) {
          return Promise.reject(e);
        }
      } 
      else {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);


export default axiosInstance;
