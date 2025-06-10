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

  // Initializeaza procesul de activare 2FA
  enable2FA() {
    return api.post("auth/users/enable_2fa/");
  },

  // Confirma activarea 2FA cu codul de verificare
  confirm2FA(code) {
    return api.post("auth/users/confirm_2fa/", { code });
  },

  // Dezactiveaza 2FA
  disable2FA() {
    return api.post("auth/users/disable_2fa/");
  },

  // Obtine statusul 2FA
  get2FAStatus() {
    return api.get("auth/users/get_2fa_status/");
  },

  regenerateBackupCodes() {
    return api.post("auth/users/regenerate_backup_codes/");
  },

  logout() {
    return api.post("auth/users/logout/").finally(() => {
      localStorage.removeItem("user");
    });
  },

  saveUserData(userData) {
    localStorage.setItem("user", JSON.stringify(userData));
  },

  getUser() {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
  },

  isLoggedIn() {
    return !!this.getUser();
  },
};
