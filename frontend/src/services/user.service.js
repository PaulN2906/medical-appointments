import api from "./api";

export default {
  getUserProfile() {
    return api.get("auth/users/profile/");
  },

  updateProfile(profileData) {
    return api.put("auth/users/profile/", profileData);
  },

  changePassword(passwordData) {
    return api.post("auth/users/change-password/", passwordData);
  },

  updateNotificationPreferences(preferences) {
    return api.put("auth/users/notification-preferences/", preferences);
  },
};
