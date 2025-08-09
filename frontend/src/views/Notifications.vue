<template>
  <div class="container my-4">
    <h1 class="mb-4">Notifications</h1>

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div
            class="card-header d-flex justify-content-between align-items-center"
          >
            <div>Your Notifications</div>
            <div>
              <button
                @click="markAllAsRead"
                class="btn btn-sm btn-outline-primary"
                :disabled="loading || noUnreadNotifications"
              >
                Mark All as Read
              </button>
            </div>
          </div>

          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <LoadingSpinner />
            </div>

            <div v-else-if="notifications.length === 0" class="text-center p-4">
              <p>You don't have any notifications.</p>
            </div>

            <div v-else>
              <div class="mb-3">
                <div class="form-check form-switch">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="showRead"
                    v-model="showRead"
                  />
                  <label class="form-check-label" for="showRead"
                    >Show Read Notifications</label
                  >
                </div>
              </div>

              <div class="list-group">
                <div
                  v-for="notification in filteredNotifications"
                  :key="notification.id"
                  class="list-group-item list-group-item-action"
                  :class="{ active: !notification.read }"
                >
                  <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">{{ notification.title }}</h5>
                    <small>{{ formatDateTime(notification.created_at) }}</small>
                  </div>
                  <p class="mb-1">{{ notification.message }}</p>
                  <div class="d-flex justify-content-between">
                    <small>{{ getNotificationType(notification.type) }}</small>
                    <div>
                      <button
                        v-if="!notification.read"
                        @click="markAsRead(notification.id)"
                        class="btn btn-sm btn-outline-secondary me-2"
                      >
                        <i class="bi bi-check"></i> Mark as Read
                      </button>
                      <button
                        v-if="notification.type === 'email'"
                        @click="sendEmail(notification.id)"
                        class="btn btn-sm btn-outline-primary"
                      >
                        <i class="bi bi-envelope"></i> Send Email
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div
                v-if="filteredNotifications.length === 0"
                class="text-center mt-4"
              >
                <p v-if="showRead">You don't have any notifications.</p>
                <p v-else>
                  You don't have any unread notifications.
                  <a href="#" @click.prevent="showRead = true"
                    >Show read notifications?</a
                  >
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import NotificationService from "@/services/notification.service";

export default {
  name: "Notifications",

  setup() {
    const loading = ref(true);
    const notifications = ref([]);
    const showRead = ref(false);

    // Filtreaza notificarile in functie de setarea showRead
    const filteredNotifications = computed(() => {
      if (showRead.value) {
        return notifications.value;
      } else {
        return notifications.value.filter((n) => !n.read);
      }
    });

    // Verifica daca nu exista notificari necitite
    const noUnreadNotifications = computed(() => {
      return !notifications.value.some((n) => !n.read);
    });

    // Incarca notificarile
    const loadNotifications = async () => {
      try {
        const response = await NotificationService.getNotifications();
        notifications.value = response.data;
      } catch (error) {
        console.error("Failed to load notifications", error);
      } finally {
        loading.value = false;
      }
    };

    // Marcheaza o notificare ca citita
    const markAsRead = async (notificationId) => {
      try {
        await NotificationService.markAsRead(notificationId);
        const index = notifications.value.findIndex(
          (n) => n.id === notificationId
        );
        if (index !== -1) {
          notifications.value[index].read = true;
        }
      } catch (error) {
        console.error("Failed to mark notification as read", error);
        alert("Failed to mark notification as read. Please try again.");
      }
    };

    // Marcheaza toate notificarile ca citite
    const markAllAsRead = async () => {
      if (noUnreadNotifications.value) {
        return;
      }

      try {
        const unreadNotifications = notifications.value.filter((n) => !n.read);
        for (const notification of unreadNotifications) {
          await NotificationService.markAsRead(notification.id);
          notification.read = true;
        }
      } catch (error) {
        console.error("Failed to mark all notifications as read", error);
        alert("Failed to mark all notifications as read. Please try again.");
      }
    };

    // Trimite email pentru o notificare
    const sendEmail = async (notificationId) => {
      try {
        await NotificationService.sendEmail(notificationId);
        alert("Email sent successfully!");
      } catch (error) {
        console.error("Failed to send email", error);
        alert("Failed to send email. Please try again.");
      }
    };

    // Helper pentru afisarea tipului de notificare
    const getNotificationType = (type) => {
      const types = {
        email: "Email Notification",
        system: "System Notification",
      };

      return types[type] || "Notification";
    };

    // Helper pentru formatarea datei si orei
    const formatDateTime = (dateTimeString) => {
      const options = {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      };
      return new Date(dateTimeString).toLocaleString(undefined, options);
    };

    onMounted(() => {
      loadNotifications();
    });

    return {
      loading,
      notifications,
      showRead,
      filteredNotifications,
      noUnreadNotifications,
      markAsRead,
      markAllAsRead,
      sendEmail,
      getNotificationType,
      formatDateTime,
    };
  },
};
</script>

<style scoped>
.list-group-item.active {
  background-color: #e2f3ff;
  color: #212529;
  border-color: #b8daff;
}
</style>
