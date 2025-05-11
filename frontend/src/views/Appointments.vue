<template>
  <div class="container my-4">
    <h1 class="mb-4">My Appointments</h1>

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div
            class="card-header d-flex justify-content-between align-items-center"
          >
            <div>
              Your Appointments
              <span v-if="filter" class="badge bg-secondary ms-2">
                {{ filter }} only
              </span>
            </div>
            <router-link
              v-if="isPatient"
              to="/book-appointment"
              class="btn btn-primary"
            >
              <i class="bi bi-plus"></i> New Appointment
            </router-link>
          </div>

          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div
              v-else-if="filteredAppointments.length === 0"
              class="text-center p-5"
            >
              <p class="mb-4">
                You don't have any {{ filter || "" }} appointments.
              </p>
              <router-link
                v-if="isPatient"
                to="/book-appointment"
                class="btn btn-primary"
              >
                Book Your First Appointment
              </router-link>
            </div>

            <div v-else>
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>{{ isDoctor ? "Patient" : "Doctor" }}</th>
                      <th>Date</th>
                      <th>Time</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="appointment in filteredAppointments"
                      :key="appointment.id"
                    >
                      <td>
                        {{
                          isDoctor
                            ? getPatientName(appointment)
                            : getDoctorName(appointment)
                        }}
                      </td>
                      <td>
                        {{ formatDate(appointment.schedule_details.date) }}
                      </td>
                      <td>
                        {{
                          formatTime(appointment.schedule_details.start_time)
                        }}
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
                          v-if="isDoctor && appointment.status === 'pending'"
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
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";
import AppointmentService from "@/services/appointment.service";

export default {
  name: "Appointments",

  setup() {
    const route = useRoute();
    const router = useRouter();
    const store = useStore();

    const loading = ref(true);
    const appointments = ref([]);

    // Get filter from query params
    const filter = computed(() => route.query.filter);

    // Get current user and role
    const currentUser = computed(() => store.getters["auth/currentUser"]);
    const isDoctor = computed(() => currentUser.value?.role === "doctor");
    const isPatient = computed(() => currentUser.value?.role === "patient");

    // Filter appointments based on query param
    const filteredAppointments = computed(() => {
      if (!filter.value) return appointments.value;
      return appointments.value.filter((apt) => apt.status === filter.value);
    });

    // Load appointments
    const loadAppointments = async () => {
      try {
        const response = await AppointmentService.getAppointments();
        appointments.value = response.data;
      } catch (error) {
        console.error("Failed to load appointments", error);
      } finally {
        loading.value = false;
      }
    };

    // Navigate to appointment details
    const viewAppointment = (id) => {
      router.push(`/appointments/${id}`);
    };

    // Confirm appointment (for doctors)
    const confirmAppointment = async (id) => {
      try {
        await AppointmentService.confirmAppointment(id);
        // Reload appointments
        await loadAppointments();
      } catch (error) {
        console.error("Failed to confirm appointment", error);
        alert("Failed to confirm appointment");
      }
    };

    // Cancel appointment
    const cancelAppointment = async (id) => {
      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      try {
        await AppointmentService.cancelAppointment(id);
        // Reload appointments
        await loadAppointments();
      } catch (error) {
        console.error("Failed to cancel appointment", error);
        alert("Failed to cancel appointment");
      }
    };

    // Format helpers
    const getDoctorName = (appointment) => {
      if (appointment.doctor_details?.user) {
        const user = appointment.doctor_details.user;
        return `Dr. ${user.first_name} ${user.last_name}`;
      }
      return "Unknown Doctor";
    };

    const getPatientName = (appointment) => {
      if (appointment.patient_details?.user) {
        const user = appointment.patient_details.user;
        return `${user.first_name} ${user.last_name}`;
      }
      return "Unknown Patient";
    };
    const formatDate = (dateString) => {
      const options = { year: "numeric", month: "long", day: "numeric" };
      return new Date(dateString).toLocaleDateString(undefined, options);
    };

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
    });

    return {
      loading,
      appointments,
      filter,
      filteredAppointments,
      currentUser,
      isDoctor,
      isPatient,
      viewAppointment,
      confirmAppointment,
      cancelAppointment,
      getDoctorName,
      getPatientName,
      formatDate,
      formatTime,
      getStatusClass,
    };
  },
};
</script>
