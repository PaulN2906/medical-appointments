import NotificationService from "@/services/notification.service";

export default {
  namespaced: true,

  state: {
    notifications: [],
    loading: false,
    error: null,
  },

  mutations: {
    setNotifications(state, notifications) {
      state.notifications = notifications;
    },
    setLoading(state, loading) {
      state.loading = loading;
    },
    setError(state, error) {
      state.error = error;
    },
    markAsRead(state, notificationId) {
      const notification = state.notifications.find(
        (n) => n.id === notificationId
      );
      if (notification) {
        notification.read = true;
      }
    },
    markAllAsRead(state) {
      state.notifications.forEach((notification) => {
        notification.read = true;
      });
    },
  },

  actions: {
    async fetchNotifications({ commit }) {
      commit("setLoading", true);
      commit("setError", null);

      try {
        const response = await NotificationService.getNotifications();
        commit("setNotifications", response.data);
      } catch (error) {
        commit(
          "setError",
          error.response?.data?.error || "Failed to load notifications"
        );
        console.error("Error fetching notifications:", error);
      } finally {
        commit("setLoading", false);
      }
    },

    async markAsRead({ commit }, notificationId) {
      try {
        await NotificationService.markAsRead(notificationId);
        commit("markAsRead", notificationId);
        return { success: true };
      } catch (error) {
        console.error("Error marking notification as read:", error);
        return {
          success: false,
          error:
            error.response?.data?.error ||
            "Failed to mark notification as read",
        };
      }
    },

    async markAllAsRead({ commit }) {
      try {
        await NotificationService.markAllAsRead();
        commit("markAllAsRead");
        return { success: true };
      } catch (error) {
        console.error("Error marking all notifications as read:", error);
        return {
          success: false,
          error:
            error.response?.data?.error ||
            "Failed to mark all notifications as read",
        };
      }
    },

    async sendEmail(_, notificationId) {
      try {
        await NotificationService.sendEmail(notificationId);
        return { success: true };
      } catch (error) {
        console.error("Error sending email notification:", error);
        return {
          success: false,
          error:
            error.response?.data?.error || "Failed to send email notification",
        };
      }
    },
  },

  getters: {
    allNotifications: (state) => state.notifications,
    unreadNotifications: (state) => state.notifications.filter((n) => !n.read),
    notificationById: (state) => (id) =>
      state.notifications.find((n) => n.id === id),
    notificationCount: (state) => state.notifications.length,
    unreadCount: (state) => state.notifications.filter((n) => !n.read).length,
    isLoading: (state) => state.loading,
    hasError: (state) => !!state.error,
    errorMessage: (state) => state.error,
  },
};
