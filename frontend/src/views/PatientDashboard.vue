<template>
  <div class="container my-4">
    <h1 class="mb-4">Patient Dashboard</h1>

    <div class="row">
      <div class="col-md-4 mb-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">My Appointments</h5>
            <p class="card-text">View and manage your upcoming appointments.</p>
            <router-link to="/appointments" class="btn btn-primary"
              >View Appointments</router-link
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
          <div class="card-header">Upcoming Appointments</div>
          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div
              v-else-if="upcomingAppointments.length === 0"
              class="text-center p-4"
            >
              <p>You don't have any upcoming appointments.</p>
              <router-link to="/book-appointment" class="btn btn-primary"
                >Book an Appointment</router-link
              >
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="appointment in upcomingAppointments"
                    :key="appointment.id"
                  >
                    <td>{{ getDoctorName(appointment) }}</td>
                    <td>{{ formatDate(appointment.schedule_details.date) }}</td>
                    <td>
                      {{ formatTime(appointment.schedule_details.start_time) }}
                    </td>
                    <td>
                      <span :class="getStatusClass(appointment.status)">
                        {{ appointment.status }}
                      </span>
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
          <div class="card-header">Notifications</div>
          <div class="card-body">
            <div v-if="loadingNotifications" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="notifications.length === 0" class="text-center p-4">
              <p>You don't have any new notifications.</p>
            </div>

            <div v-else>
              <div
                v-for="notification in notifications"
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
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import AppointmentService from "@/services/appointment.service";
import NotificationService from "@/services/notification.service";

export default {
  name: "PatientDashboard",

  setup() {
    const router = useRouter();

    const loading = ref(true);
    const loadingNotifications = ref(true);
    const upcomingAppointments = ref([]);
    const notifications = ref([]);

    // Obtine programarile viitoare
    const loadAppointments = async () => {
      try {
        const response = await AppointmentService.getAppointments();
        // Filtreaza doar programarile care nu sunt finalizate sau anulate
        upcomingAppointments.value = response.data.filter((appointment) =>
          ["pending", "confirmed"].includes(appointment.status)
        );
      } catch (error) {
        console.error("Failed to load appointments", error);
      } finally {
        loading.value = false;
      }
    };

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

    // Marcheaza o notificare ca citita
    const markAsRead = async (notificationId) => {
      try {
        await NotificationService.markAsRead(notificationId);
        // Actualizeaza starea notificarii in UI
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

    // Anuleaza o programare
    const cancelAppointment = async (appointmentId) => {
      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      try {
        await AppointmentService.cancelAppointment(appointmentId);
        // Actualizeaza starea programarii in UI
        const appointmentIndex = upcomingAppointments.value.findIndex(
          (a) => a.id === appointmentId
        );
        if (appointmentIndex !== -1) {
          upcomingAppointments.value[appointmentIndex].status = "cancelled";
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

    // Helper pentru afisarea numelui medicului
    const getDoctorName = (appointment) => {
      if (appointment.doctor_details && appointment.doctor_details.user) {
        const user = appointment.doctor_details.user;
        return `Dr. ${user.last_name} ${user.first_name}`;
      }
      return "Unknown Doctor";
    };

    // Helper pentru formatarea datei
    const formatDate = (dateString) => {
      const options = { year: "numeric", month: "long", day: "numeric" };
      return new Date(dateString).toLocaleDateString(undefined, options);
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
    });

    return {
      loading,
      loadingNotifications,
      upcomingAppointments,
      notifications,
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
</style>
