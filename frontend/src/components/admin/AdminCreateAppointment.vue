<template>
  <div>
    <form @submit.prevent="createAppointment">
      <div class="row">
        <!-- Patient Selection -->
        <div class="col-md-6 mb-3">
          <label class="form-label">Patient *</label>
          <select class="form-select" v-model="form.patient" required>
            <option value="">Select a patient...</option>
            <option
              v-for="patient in patients"
              :key="patient.id"
              :value="patient.id"
            >
              {{ patient.user.first_name }} {{ patient.user.last_name }} ({{
                patient.user.email
              }})
            </option>
          </select>
        </div>

        <!-- Doctor Selection -->
        <div class="col-md-6 mb-3">
          <label class="form-label">Doctor *</label>
          <select
            class="form-select"
            v-model="form.doctor"
            required
            @change="loadDoctorSchedules"
          >
            <option value="">Select a doctor...</option>
            <option
              v-for="doctor in doctors"
              :key="doctor.id"
              :value="doctor.id"
            >
              Dr. {{ doctor.user.last_name }} {{ doctor.user.first_name }} -
              {{ doctor.speciality }}
            </option>
          </select>
        </div>
      </div>

      <div class="row">
        <!-- Date Selection -->
        <div class="col-md-4 mb-3">
          <label class="form-label">Date *</label>
          <input
            type="date"
            class="form-control"
            v-model="form.date"
            :min="minDate"
            required
            @change="loadAvailableSlots"
          />
        </div>

        <!-- Time Slot Selection -->
        <div class="col-md-8 mb-3">
          <label class="form-label">Available Time Slots *</label>
          <div v-if="loadingSlots" class="text-center p-2">
            <div class="spinner-border spinner-border-sm" role="status"></div>
            <span class="ms-2">Loading available slots...</span>
          </div>
          <div
            v-else-if="availableSlots.length === 0"
            class="alert alert-warning"
          >
            No available slots for this doctor on the selected date.
          </div>
          <div v-else class="row">
            <div
              class="col-md-6 col-lg-4 mb-2"
              v-for="slot in availableSlots"
              :key="slot.id"
            >
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="radio"
                  :id="`slot-${slot.id}`"
                  :value="slot.id"
                  v-model="form.schedule"
                  required
                />
                <label class="form-check-label" :for="`slot-${slot.id}`">
                  {{ formatTime(slot.start_time) }} -
                  {{ formatTime(slot.end_time) }}
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div class="mb-3">
        <label class="form-label">Notes (Optional)</label>
        <textarea
          class="form-control"
          v-model="form.notes"
          rows="3"
          placeholder="Any additional notes for this appointment..."
        ></textarea>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
      </div>

      <!-- Success Display -->
      <div v-if="success" class="alert alert-success">
        <i class="bi bi-check-circle me-2"></i>
        {{ success }}
      </div>

      <!-- Form Actions -->
      <div class="text-end">
        <button type="button" class="btn btn-secondary me-2" @click="resetForm">
          Reset
        </button>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="
            creating || !form.patient || !form.doctor || !form.schedule
          "
        >
          <span
            v-if="creating"
            class="spinner-border spinner-border-sm me-2"
            role="status"
          ></span>
          <i v-else class="bi bi-calendar-plus me-2"></i>
          Create Appointment
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";
import AdminService from "@/services/admin.service";
import DoctorService from "@/services/doctor.service";

export default {
  name: "AdminCreateAppointment",
  emits: ["created"],

  setup(props, { emit }) {
    const loading = ref(true);
    const loadingSlots = ref(false);
    const creating = ref(false);
    const error = ref("");
    const success = ref("");

    const doctors = ref([]);
    const patients = ref([]);
    const availableSlots = ref([]);

    const form = reactive({
      patient: "",
      doctor: "",
      date: "",
      schedule: "",
      notes: "",
    });

    // Minimum date (today)
    const minDate = new Date().toISOString().split("T")[0];

    const loadData = async () => {
      try {
        const [doctorsResponse, patientsResponse] = await Promise.all([
          AdminService.getAllDoctors(),
          AdminService.getAllPatients(),
        ]);

        doctors.value = doctorsResponse.data;
        patients.value = patientsResponse.data;
      } catch (err) {
        console.error("Failed to load doctors/patients", err);
        error.value = "Failed to load doctors and patients data";
      } finally {
        loading.value = false;
      }
    };

    const loadAvailableSlots = async () => {
      if (!form.doctor || !form.date) {
        availableSlots.value = [];
        return;
      }

      loadingSlots.value = true;
      try {
        const response = await DoctorService.getSchedules(form.doctor);

        // Filter pentru data selectata si doar slot-urile disponibile
        availableSlots.value = response.data.filter(
          (schedule) => schedule.date === form.date && schedule.is_available
        );
      } catch (err) {
        console.error("Failed to load available slots", err);
        error.value = "Failed to load available time slots";
      } finally {
        loadingSlots.value = false;
      }
    };

    const loadDoctorSchedules = () => {
      form.schedule = ""; // Reset selected slot cand schimbam doctorul
      if (form.date) {
        loadAvailableSlots();
      }
    };

    const createAppointment = async () => {
      creating.value = true;
      error.value = "";
      success.value = "";

      try {
        const appointmentData = {
          patient: form.patient,
          doctor: form.doctor,
          schedule: form.schedule,
          notes: form.notes || "",
        };

        await AdminService.createAppointmentAsAdmin(appointmentData);

        success.value = "Appointment created successfully!";

        // Emit success event
        setTimeout(() => {
          emit("created");
        }, 1500);
      } catch (err) {
        console.error("Failed to create appointment", err);
        const errorMsg =
          err.response?.data?.error ||
          err.response?.data?.detail ||
          "Failed to create appointment";
        error.value = errorMsg;
      } finally {
        creating.value = false;
      }
    };

    const resetForm = () => {
      Object.keys(form).forEach((key) => {
        form[key] = "";
      });
      availableSlots.value = [];
      error.value = "";
      success.value = "";
    };

    const formatTime = (timeString) => {
      if (!timeString) return "";
      const timeParts = timeString.split(":");
      const date = new Date();
      date.setHours(parseInt(timeParts[0], 10));
      date.setMinutes(parseInt(timeParts[1], 10));
      return date.toLocaleTimeString(undefined, {
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    onMounted(() => {
      loadData();
    });

    return {
      loading,
      loadingSlots,
      creating,
      error,
      success,
      doctors,
      patients,
      availableSlots,
      form,
      minDate,
      loadAvailableSlots,
      loadDoctorSchedules,
      createAppointment,
      resetForm,
      formatTime,
    };
  },
};
</script>
