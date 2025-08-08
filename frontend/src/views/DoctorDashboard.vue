<template>
  <div class="container my-4">
    <h1 class="mb-4">Doctor Dashboard</h1>

    <div class="row">
      <div class="col-md-4 mb-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">My Schedule</h5>
            <p class="card-text">Manage your availability and working hours.</p>
            <router-link to="/doctor-schedule" class="btn btn-primary"
              >Manage Schedule</router-link
            >
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Pending Appointments</h5>
            <p class="card-text">Review and confirm pending appointments.</p>
            <router-link
              to="/appointments?filter=pending"
              class="btn btn-warning"
              >Review</router-link
            >
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">My Profile</h5>
            <p class="card-text">Update your professional information.</p>
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
          <div class="card-header">Today's Appointments</div>
          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div
              v-else-if="todayAppointments.length === 0"
              class="text-center p-4"
            >
              <p>You don't have any appointments scheduled for today.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Patient</th>
                    <th>Status</th>
                    <th>Notes</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="appointment in todayAppointments"
                    :key="appointment.id"
                  >
                    <td>
                      {{ formatTime(appointment.schedule_details.start_time) }}
                    </td>
                    <td>{{ getPatientName(appointment) }}</td>
                    <td>
                      <span :class="getStatusClass(appointment.status)">
                        {{ appointment.status }}
                      </span>
                    </td>
                    <td>{{ appointment.notes || "No notes" }}</td>
                    <td>
                      <button
                        @click="viewAppointment(appointment.id)"
                        class="btn btn-sm btn-info me-2"
                      >
                        View
                      </button>
                      <button
                        v-if="appointment.status === 'pending'"
                        @click="confirmAppointment(appointment.id)"
                        class="btn btn-sm btn-success me-2"
                      >
                        Confirm
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
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">Weekly Schedule</div>
          <div class="card-body">
            <div v-if="loadingSchedule" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else>
              <!-- Componenta calendar în mod compact -->
              <DoctorCalendar
                :editable="false"
                :view="'timeGridWeek'"
                :height="500"
              />
              <div class="text-center mt-3">
                <router-link
                  to="/doctor-schedule"
                  class="btn btn-outline-primary"
                >
                  Full Schedule View
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card">
          <div class="card-header">Recent Notifications</div>
          <div class="card-body">
            <div v-if="loadingNotifications" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="notifications.length === 0" class="text-center p-4">
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
import DoctorCalendar from "@/components/calendar/DoctorCalendar.vue";
import {
  getPatientName,
  formatTime,
  formatDateTime,
  getStatusClass,
} from "@/utils/formatters";

export default {
  name: "DoctorDashboard",
  components: {
    DoctorCalendar,
  },

  setup() {
    const router = useRouter();
    const store = useStore();

    const loadingSchedule = ref(true);
    const loadingNotifications = ref(true);
    const notifications = ref([]);

    // Stare din store
    const loading = computed(() => store.getters["appointments/isLoading"]);
    const allAppointments = computed(
      () => store.getters["appointments/allAppointments"]
    );

    // Obtine programarile
    const loadAppointments = async () => {
      await store.dispatch("appointments/fetchAppointments");
    };

    // Filtreaza programarile pentru astazi
    const todayAppointments = computed(() => {
      const today = new Date();
      const todayString = today.toISOString().split("T")[0]; // Format: YYYY-MM-DD
      return allAppointments.value
        .filter((appointment) => {
          // Check if appointment is for today and not cancelled/completed
          const isToday =
            appointment.schedule_details &&
            appointment.schedule_details.date === todayString;
          const isActive = ["pending", "confirmed"].includes(
            appointment.status
          );

          return isToday && isActive;
        })
        .sort((a, b) => {
          // Sort by start time
          return a.schedule_details.start_time.localeCompare(
            b.schedule_details.start_time
          );
        });
    });

    // Obtine notificarile
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

    // Afiseaza doar cele mai recente 5 notificari
    const recentNotifications = computed(() => {
      return notifications.value.slice(0, 5);
    });

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
      }
    };

    // Confirma o programare
    const confirmAppointment = async (appointmentId) => {
      const result = await store.dispatch(
        "appointments/confirmAppointment",
        appointmentId
      );
      if (result.success) {
        alert("Appointment confirmed successfully");
      } else {
        alert(
          result.error || "Failed to confirm appointment. Please try again."
        );
      }
    };

    // Anuleaza o programare
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

    // Navigheaza la detaliile programarii
    const viewAppointment = (appointmentId) => {
      router.push(`/appointments/${appointmentId}`);
    };

    onMounted(() => {
      loadAppointments();
      loadNotifications();
      loadingSchedule.value = false; // Se va seta cand calendarul se incarca complet
    });

    return {
      loading,
      loadingSchedule,
      loadingNotifications,
      todayAppointments,
      notifications,
      recentNotifications,
      markAsRead,
      confirmAppointment,
      cancelAppointment,
      viewAppointment,
      getPatientName,
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
</style>
