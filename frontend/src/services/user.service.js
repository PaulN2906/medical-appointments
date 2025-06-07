import api from "./api";

export default {
  // Get current user's complete profile
  getUserProfile() {
    return api.get("auth/users/get_profile/");
  },

  // Update user profile
  updateProfile(profileData) {
    return api.put("auth/users/update_profile/", profileData);
  },

  // Change password
  changePassword(passwordData) {
    return api.post("auth/users/change_password/", passwordData);
  },

  // Get notification preferences
  getNotificationPreferences() {
    return api.get("auth/users/get_notification_preferences/");
  },

  // Update notification preferences
  updateNotificationPreferences(preferences) {
    return api.put("auth/users/update_notification_preferences/", preferences);
  },

  // Reset notification preferences to defaults
  resetNotificationPreferences() {
    return api.post("auth/users/reset_notification_preferences/");
  },

  // Get user activity/security info (placeholder for future implementation)
  getUserActivity() {
    return api.get("auth/users/activity/");
  },
};
