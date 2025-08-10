import api from "./api";

export default {
  getNotifications() {
    return api.get("notifications/notifications/");
  },

  markAsRead(id) {
    return api.post(`notifications/notifications/${id}/mark_as_read/`);
  },

  markAllAsRead() {
    return api.post("notifications/notifications/mark_all_as_read/");
  },

  sendEmail(id) {
    return api.post(`notifications/notifications/${id}/send_email/`);
  },
};
