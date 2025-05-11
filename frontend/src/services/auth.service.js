import api from "./api";

export default {
  register(userData) {
    return api.post("auth/users/register/", userData);
  },

  login(credentials) {
    return api.post("auth/users/login/", credentials);
  },

  verify2FA(userId, code) {
    return api.post("auth/users/verify_2fa/", { user_id: userId, code });
  },

  enable2FA() {
    return api.post("auth/users/enable_2fa/");
  },

  logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  },

  saveUserData(userData, token) {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(userData));
  },

  getUser() {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
  },

  isLoggedIn() {
    return !!localStorage.getItem("token");
  },
};
