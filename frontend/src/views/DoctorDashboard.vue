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
import AppointmentService from "@/services/appointment.service";
import NotificationService from "@/services/notification.service";
import DoctorCalendar from "@/components/calendar/DoctorCalendar.vue";

export default {
  name: "DoctorDashboard",
  components: {
    DoctorCalendar,
  },

  setup() {
    const router = useRouter();

    const loading = ref(true);
    const loadingSchedule = ref(true);
    const loadingNotifications = ref(true);
    const allAppointments = ref([]);
    const notifications = ref([]);

    // Obtine programarile
    const loadAppointments = async () => {
      try {
        const response = await AppointmentService.getAppointments();
        allAppointments.value = response.data;
      } catch (error) {
        console.error("Failed to load appointments", error);
      } finally {
        loading.value = false;
      }
    };

    // Filtreaza programarile pentru astazi
    const todayAppointments = computed(() => {
      const today = new Date().toISOString().split("T")[0];
      return allAppointments.value
        .filter(
          (appointment) =>
            appointment.schedule_details &&
            appointment.schedule_details.date === today
        )
        .sort((a, b) => {
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
      try {
        await AppointmentService.confirmAppointment(appointmentId);
        const index = allAppointments.value.findIndex(
          (a) => a.id === appointmentId
        );
        if (index !== -1) {
          allAppointments.value[index].status = "confirmed";
        }
        alert("Appointment confirmed successfully");
      } catch (error) {
        console.error("Failed to confirm appointment", error);
        alert("Failed to confirm appointment. Please try again.");
      }
    };

    // Anuleaza o programare
    const cancelAppointment = async (appointmentId) => {
      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      try {
        await AppointmentService.cancelAppointment(appointmentId);
        const index = allAppointments.value.findIndex(
          (a) => a.id === appointmentId
        );
        if (index !== -1) {
          allAppointments.value[index].status = "cancelled";
        }
        alert("Appointment cancelled successfully");
      } catch (error) {
        console.error("Failed to cancel appointment", error);
        alert("Failed to cancel appointment. Please try again.");
      }
    };

    // Navigheaza la detaliile programarii
    const viewAppointment = (appointmentId) => {
      router.push(`/appointments/${appointmentId}`);
    };

    // Helper pentru afisarea numelui pacientului
    const getPatientName = (appointment) => {
      if (appointment.patient_details && appointment.patient_details.user) {
        const user = appointment.patient_details.user;
        return `${user.first_name} ${user.last_name}`;
      }
      return "Unknown Patient";
    };

    // Helper pentru formatarea orei
    const formatTime = (timeString) => {
      const timeParts = timeString.split(":");
      const date = new Date();
      date.setHours(parseInt(timeParts[0], 10));
      date.setMinutes(parseInt(timeParts[1], 10));

      return date.toLocaleTimeString(undefined, {
        hour: "2-digit",
        minute: "2-digit",
      });
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

    // Helper pentru obtinerea clasei CSS in functie de status
    const getStatusClass = (status) => {
      const statusClasses = {
        pending: "badge bg-warning",
        confirmed: "badge bg-success",
        cancelled: "badge bg-danger",
        completed: "badge bg-info",
      };

      return statusClasses[status] || "badge bg-secondary";
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
