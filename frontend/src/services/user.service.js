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

  // Update notification preferences (placeholder for future implementation)
  updateNotificationPreferences(preferences) {
    return api.put("auth/users/notification_preferences/", preferences);
  },

  // Get user activity/security info (placeholder for future implementation)
  getUserActivity() {
    return api.get("auth/users/activity/");
  },
};
