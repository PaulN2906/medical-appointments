<template>
  <div class="container my-4">
    <h1 class="mb-4">Patient Dashboard</h1>

    <div class="row">
      <div class="col-md-4 mb-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">My Calendar</h5>
            <p class="card-text">View and manage your appointments.</p>
            <router-link to="/patient-calendar" class="btn btn-primary"
              >View Calendar</router-link
            >
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Book Appointment</h5>
            <p class="card-text">Schedule a new appointment with a doctor.</p>
            <router-link to="/book-appointment" class="btn btn-success"
              >Book Now</router-link
            >
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">My Profile</h5>
            <p class="card-text">
              Update your personal information and preferences.
            </p>
            <router-link to="/profile" class="btn btn-secondary"
              >Edit Profile</router-link
            >
          </div>
        </div>
      </div>
    </div>

    <div class="row mt-4">
      <div class="col-md-12">
        <div class="card">
          <div
            class="card-header d-flex justify-content-between align-items-center"
          >
            <span>Upcoming Appointments</span>
            <small class="text-muted">{{ getCurrentDateInfo() }}</small>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <LoadingSpinner />
            </div>

            <div
              v-else-if="upcomingAppointments.length === 0"
              class="text-center p-4"
            >
              <div class="mb-3">
                <i class="bi bi-calendar-check fs-1 text-muted"></i>
              </div>
              <p class="mb-3">You don't have any upcoming appointments.</p>
              <router-link to="/book-appointment" class="btn btn-primary"
                >Book an Appointment</router-link
              >

              <!-- Show link to view all appointments if there might be past ones -->
              <div class="mt-3">
                <router-link
                  to="/patient-calendar"
                  class="btn btn-outline-secondary btn-sm"
                >
                  View My Calendar
                </router-link>
              </div>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Days Until</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="appointment in upcomingAppointments"
                    :key="appointment.id"
                    :class="{
                      'table-warning': isToday(
                        appointment.schedule_details.date
                      ),
                    }"
                  >
                    <td>{{ getDoctorName(appointment) }}</td>
                    <td>
                      {{ formatDate(appointment.schedule_details.date) }}
                      <span
                        v-if="isToday(appointment.schedule_details.date)"
                        class="badge bg-primary ms-2"
                        >Today</span
                      >
                    </td>
                    <td>
                      {{ formatTime(appointment.schedule_details.start_time) }}
                    </td>
                    <td>
                      <span :class="getStatusClass(appointment.status)">
                        {{ appointment.status }}
                      </span>
                    </td>
                    <td>
                      <small class="text-muted">
                        {{ getDaysUntil(appointment.schedule_details.date) }}
                      </small>
                    </td>
                    <td>
                      <button
                        @click="viewAppointment(appointment.id)"
                        class="btn btn-sm btn-info me-2"
                      >
                        View
                      </button>
                      <button
                        v-if="
                          appointment.status === 'pending' ||
                          appointment.status === 'confirmed'
                        "
                        @click="cancelAppointment(appointment.id)"
                        class="btn btn-sm btn-danger"
                      >
                        Cancel
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row mt-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">Recent Notifications</div>
          <div class="card-body">
            <div v-if="loadingNotifications" class="text-center p-4">
              <LoadingSpinner />
            </div>

            <div
              v-else-if="recentNotifications.length === 0"
              class="text-center p-4"
            >
              <p>You don't have any recent notifications.</p>
            </div>

            <div v-else>
              <div
                v-for="notification in recentNotifications"
                :key="notification.id"
                class="notification-item mb-3 p-3"
                :class="{ unread: !notification.read }"
              >
                <div class="d-flex justify-content-between">
                  <h6>{{ notification.title }}</h6>
                  <small>{{ formatDateTime(notification.created_at) }}</small>
                </div>
                <p>{{ notification.message }}</p>
                <button
                  v-if="!notification.read"
                  @click="markAsRead(notification.id)"
                  class="btn btn-sm btn-outline-secondary"
                >
                  Mark as Read
                </button>
              </div>

              <div class="text-center mt-3" v-if="notifications.length > 5">
                <router-link
                  to="/notifications"
                  class="btn btn-outline-primary"
                >
                  View All Notifications
                </router-link>
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
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import NotificationService from "@/services/notification.service";
import {
  getDoctorName,
  formatDate,
  formatTime,
  formatDateTime,
  getStatusClass,
  isToday,
  getDaysUntil,
  isUpcoming,
} from "@/utils/formatters";

export default {
  name: "PatientDashboard",

  setup() {
    const router = useRouter();
    const store = useStore();

    const loadingNotifications = ref(true);
    const notifications = ref([]);

    // Stare din store
    const loading = computed(() => store.getters["appointments/isLoading"]);
    const upcomingAppointments = computed(() => {
      return store.getters["appointments/allAppointments"]
        .filter((appointment) => {
          const isActiveStatus = ["pending", "confirmed"].includes(
            appointment.status
          );
          const isUpcomingAppt = isUpcoming(appointment.schedule_details?.date);
          return isActiveStatus && isUpcomingAppt;
        })
        .sort((a, b) => {
          const dateComparison = a.schedule_details.date.localeCompare(
            b.schedule_details.date
          );
          if (dateComparison !== 0) {
            return dateComparison;
          }
          return a.schedule_details.start_time.localeCompare(
            b.schedule_details.start_time
          );
        });
    });

    // Show only the 5 most recent notifications
    const recentNotifications = computed(() => {
      return notifications.value.slice(0, 5);
    });

    // Get current date info for display
    const getCurrentDateInfo = () => {
      const today = new Date();
      return today.toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    };

    // Load upcoming appointments
    const loadAppointments = async () => {
      await store.dispatch("appointments/fetchAppointments");
    };

    // Load notifications
    const loadNotifications = async () => {
      try {
        const response = await NotificationService.getNotifications();
        notifications.value = response.data;
      } catch (error) {
        console.error("Failed to load notifications", error);
      } finally {
        loadingNotifications.value = false;
      }
    };

    // Mark notification as read
    const markAsRead = async (notificationId) => {
      try {
        await NotificationService.markAsRead(notificationId);
        // Update notification state in UI
        const notificationIndex = notifications.value.findIndex(
          (n) => n.id === notificationId
        );
        if (notificationIndex !== -1) {
          notifications.value[notificationIndex].read = true;
        }
      } catch (error) {
        console.error("Failed to mark notification as read", error);
      }
    };

    // Cancel an appointment
    const cancelAppointment = async (appointmentId) => {
      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      const result = await store.dispatch(
        "appointments/cancelAppointment",
        appointmentId
      );
      if (result.success) {
        alert("Appointment cancelled successfully");
      } else {
        alert(
          result.error || "Failed to cancel appointment. Please try again."
        );
      }
    };

    // Navigate to appointment details
    const viewAppointment = (appointmentId) => {
      router.push(`/appointments/${appointmentId}`);
    };

    onMounted(() => {
      loadAppointments();
      loadNotifications();
    });

    return {
      loading,
      loadingNotifications,
      upcomingAppointments,
      notifications,
      recentNotifications,
      isToday,
      getDaysUntil,
      getCurrentDateInfo,
      markAsRead,
      cancelAppointment,
      viewAppointment,
      getDoctorName,
      formatDate,
      formatTime,
      formatDateTime,
      getStatusClass,
    };
  },
};
</script>

<style scoped>
.notification-item {
  border-radius: 4px;
  background-color: #f8f9fa;
  border-left: 3px solid #6c757d;
}

.notification-item.unread {
  background-color: #e2f3ff;
  border-left-color: #007bff;
}

.table-warning {
  background-color: rgba(255, 193, 7, 0.1) !important;
}
</style>
