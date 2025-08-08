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
                    {{
                      formatDate(appointment.schedule_details.date, {
                        weekday: "long",
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })
                    }}
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
                    {{
                      isDoctor
                        ? getPatientName(appointment)
                        : getDoctorName(appointment)
                    }}
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
import {
  getDoctorName,
  getPatientName,
  formatDate,
  formatTime,
  formatDateTime,
  getStatusClass,
} from "@/utils/formatters";

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

      const result = await store.dispatch(
        "appointments/confirmAppointment",
        appointment.value.id
      );
      if (result.success) {
        await loadAppointment();
        alert("Appointment confirmed successfully!");
      } else {
        alert(
          result.error || "Failed to confirm appointment. Please try again."
        );
      }
    };

    // Anuleaza programarea
    const cancelAppointment = async () => {
      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      const result = await store.dispatch(
        "appointments/cancelAppointment",
        appointment.value.id
      );
      if (result.success) {
        await loadAppointment();
        alert("Appointment cancelled successfully!");
      } else {
        alert(
          result.error || "Failed to cancel appointment. Please try again."
        );
      }
    };

    // Navigheaza inapoi la pagina anterioara
    const goBack = () => {
      router.back();
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
