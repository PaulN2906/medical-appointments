<template>
  <div class="container my-4">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div
            class="card-header d-flex justify-content-between align-items-center"
          >
            <h3 class="mb-0">Appointment Details</h3>
            <span
              :class="getStatusClass(appointment.status)"
              v-if="appointment"
            >
              {{ appointment.status }}
            </span>
          </div>

          <div v-if="loading" class="card-body text-center p-5">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <template v-else-if="appointment">
            <div class="card-body">
              <div class="row mb-4">
                <div class="col-md-6">
                  <h5>Date & Time</h5>
                  <p class="mb-1">
                    <strong>Date:</strong>
                    {{ formatDate(appointment.schedule_details.date) }}
                  </p>
                  <p>
                    <strong>Time:</strong>
                    {{ formatTime(appointment.schedule_details.start_time) }} -
                    {{ formatTime(appointment.schedule_details.end_time) }}
                  </p>
                </div>
                <div class="col-md-6">
                  <h5>{{ isDoctor ? "Patient" : "Doctor" }}</h5>
                  <p class="mb-1">
                    <strong>Name:</strong>
                    {{ isDoctor ? getPatientName() : getDoctorName() }}
                  </p>
                  <p v-if="!isDoctor">
                    <strong>Speciality:</strong>
                    {{ appointment.doctor_details.speciality }}
                  </p>
                </div>
              </div>

              <div class="mb-4">
                <h5>Notes</h5>
                <p v-if="appointment.notes">{{ appointment.notes }}</p>
                <p v-else class="text-muted">No notes provided</p>
              </div>

              <div class="mb-4">
                <h5>Appointment History</h5>
                <ul class="list-group">
                  <li class="list-group-item">
                    <strong>Created:</strong>
                    {{ formatDateTime(appointment.created_at) }}
                  </li>
                  <li
                    class="list-group-item"
                    v-if="appointment.updated_at !== appointment.created_at"
                  >
                    <strong>Last Updated:</strong>
                    {{ formatDateTime(appointment.updated_at) }}
                  </li>
                </ul>
              </div>
            </div>

            <div class="card-footer">
              <div class="d-flex justify-content-between">
                <button class="btn btn-outline-secondary" @click="goBack">
                  <i class="bi bi-arrow-left"></i> Back
                </button>

                <div>
                  <button
                    v-if="isDoctor && appointment.status === 'pending'"
                    @click="confirmAppointment"
                    class="btn btn-success me-2"
                  >
                    <i class="bi bi-check-circle"></i> Confirm
                  </button>

                  <button
                    v-if="
                      appointment.status === 'pending' ||
                      appointment.status === 'confirmed'
                    "
                    @click="cancelAppointment"
                    class="btn btn-danger"
                  >
                    <i class="bi bi-x-circle"></i> Cancel
                  </button>
                </div>
              </div>
            </div>
          </template>

          <div v-else class="card-body text-center">
            <p>
              Appointment not found or you don't have permission to view it.
            </p>
            <button class="btn btn-primary" @click="goBack">Go Back</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useStore } from "vuex";
import AppointmentService from "@/services/appointment.service";

export default {
  name: "AppointmentDetails",

  setup() {
    const router = useRouter();
    const route = useRoute();
    const store = useStore();

    const loading = ref(true);
    const appointment = ref(null);

    // Obtine utilizatorul curent
    const currentUser = computed(() => store.getters["auth/currentUser"]);

    // Determina daca utilizatorul curent este medic
    const isDoctor = computed(() => {
      return (
        currentUser.value &&
        currentUser.value.role === "doctor" &&
        appointment.value &&
        currentUser.value.doctor_id === appointment.value.doctor_details.id
      );
    });

    // Incarca detaliile programarii
    const loadAppointment = async () => {
      const appointmentId = route.params.id;

      if (!appointmentId) {
        router.push("/dashboard");
        return;
      }

      try {
        const response = await AppointmentService.getAppointmentDetails(
          appointmentId
        );
        appointment.value = response.data;
      } catch (error) {
        console.error("Failed to load appointment details", error);
      } finally {
        loading.value = false;
      }
    };

    // Confirma programarea (doar pentru medici)
    const confirmAppointment = async () => {
      if (!isDoctor.value || appointment.value.status !== "pending") {
        return;
      }

      try {
        await AppointmentService.confirmAppointment(appointment.value.id);
        appointment.value.status = "confirmed";
        alert("Appointment confirmed successfully!");
      } catch (error) {
        console.error("Failed to confirm appointment", error);
        alert("Failed to confirm appointment. Please try again.");
      }
    };

    // Anuleaza programarea
    const cancelAppointment = async () => {
      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      try {
        await AppointmentService.cancelAppointment(appointment.value.id);
        appointment.value.status = "cancelled";
        alert("Appointment cancelled successfully!");
      } catch (error) {
        console.error("Failed to cancel appointment", error);
        alert("Failed to cancel appointment. Please try again.");
      }
    };

    // Navigheaza inapoi la pagina anterioara
    const goBack = () => {
      router.back();
    };

    // Helper pentru afisarea numelui pacientului
    const getPatientName = () => {
      if (
        appointment.value &&
        appointment.value.patient_details &&
        appointment.value.patient_details.user
      ) {
        const user = appointment.value.patient_details.user;
        return `${user.first_name} ${user.last_name}`;
      }
      return "Unknown Patient";
    };

    // Helper pentru afisarea numelui medicului
    const getDoctorName = () => {
      if (
        appointment.value &&
        appointment.value.doctor_details &&
        appointment.value.doctor_details.user
      ) {
        const user = appointment.value.doctor_details.user;
        return `Dr. ${user.last_name} ${user.first_name}`;
      }
      return "Unknown Doctor";
    };

    // Helper pentru formatarea datei
    const formatDate = (dateString) => {
      const options = {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      };
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
        month: "long",
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
      loadAppointment();
    });

    return {
      loading,
      appointment,
      isDoctor,
      confirmAppointment,
      cancelAppointment,
      goBack,
      getPatientName,
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
/* Stilizare specifica pentru pagina de detalii */
</style>
