<template>
  <div class="container my-4">
    <h1 class="mb-4">Book an Appointment</h1>

    <!-- Doctor Selection -->
    <div class="row">
      <div class="col-md-12 mb-4">
        <div class="card">
          <div class="card-header">Select a Doctor</div>
          <div class="card-body">
            <div v-if="loadingDoctors" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else>
              <div class="row">
                <div
                  class="col-md-4 mb-3"
                  v-for="doctor in doctors"
                  :key="doctor.id"
                >
                  <div class="card h-100">
                    <div class="card-body">
                      <h5 class="card-title">
                        Dr. {{ doctor.user.last_name }}
                        {{ doctor.user.first_name }}
                      </h5>
                      <h6 class="card-subtitle mb-2 text-muted">
                        {{ doctor.speciality }}
                      </h6>
                      <p class="card-text">
                        {{ doctor.description || "No description available" }}
                      </p>
                    </div>
                    <div class="card-footer bg-transparent">
                      <button
                        @click="selectDoctor(doctor)"
                        class="btn btn-primary w-100"
                        :class="{
                          active:
                            selectedDoctor && selectedDoctor.id === doctor.id,
                        }"
                        :aria-pressed="
                          selectedDoctor && selectedDoctor.id === doctor.id
                        "
                      >
                        Select
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar & Booking Form -->
    <div v-if="selectedDoctor" class="row mt-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">Select Date and Time</div>
          <div class="card-body">
            <div class="row mb-4">
              <div class="col-md-6">
                <h5>
                  Doctor: Dr. {{ selectedDoctor.user.last_name }}
                  {{ selectedDoctor.user.first_name }}
                </h5>
                <p>Speciality: {{ selectedDoctor.speciality }}</p>
              </div>
              <div class="col-md-6 text-end">
                <button
                  @click="clearSelection"
                  class="btn btn-outline-secondary"
                >
                  Change Doctor
                </button>
              </div>
            </div>

            <div class="doctor-calendar-wrapper mb-4">
              <DoctorCalendar
                :doctorId="selectedDoctor.id"
                :editable="false"
                :showUnavailable="false"
                :allowSelect="true"
                @selectSlot="selectSlot"
              />
            </div>

            <!-- Booking form displayed immediately after calendar click -->
            <div v-if="selectedSlot">
              <div class="card">
                <div class="card-header">Appointment Details</div>
                <div class="card-body">
                  <form @submit.prevent="bookAppointment">
                    <div class="mb-3">
                      <label class="form-label">Doctor</label>
                      <input
                        type="text"
                        class="form-control"
                        :value="`Dr. ${selectedDoctor.user.last_name} ${selectedDoctor.user.first_name}`"
                        disabled
                      />
                    </div>

                    <div class="mb-3">
                      <label class="form-label">Date</label>
                      <input
                        type="text"
                        class="form-control"
                        :value="formatDate(selectedSlot.date)"
                        disabled
                      />
                    </div>

                    <div class="mb-3">
                      <label class="form-label">Time</label>
                      <input
                        type="text"
                        class="form-control"
                        :value="`${formatTime(
                          selectedSlot.start_time
                        )} - ${formatTime(selectedSlot.end_time)}`"
                        disabled
                      />
                    </div>

                    <div class="mb-3">
                      <label for="notes" class="form-label"
                        >Reason for Visit (optional)</label
                      >
                      <textarea
                        id="notes"
                        class="form-control"
                        v-model="appointmentNotes"
                        rows="3"
                        placeholder="Describe your symptoms or reason for the appointment"
                      ></textarea>
                    </div>

                    <div class="mb-3 form-check">
                      <input
                        type="checkbox"
                        class="form-check-input"
                        id="confirmCheck"
                        v-model="confirmed"
                        required
                      />
                      <label class="form-check-label" for="confirmCheck">
                        I confirm that the information provided is correct and I
                        will attend this appointment
                      </label>
                    </div>

                    <div v-if="bookingError" class="alert alert-danger">
                      {{ bookingError }}
                    </div>

                    <div class="text-end">
                      <button
                        type="button"
                        class="btn btn-outline-secondary me-2"
                        @click="clearSlotSelection"
                      >
                        Change Time Slot
                      </button>
                      <button
                        type="submit"
                        class="btn btn-success"
                        :disabled="!confirmed || booking"
                      >
                        <span
                          v-if="booking"
                          class="spinner-border spinner-border-sm me-2"
                          role="status"
                        ></span>
                        Book Appointment
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from "vue";
import { useRouter } from "vue-router";
import DoctorService from "@/services/doctor.service";
import DoctorCalendar from "@/components/calendar/DoctorCalendar.vue";
import { useStore } from "vuex";
import { formatDate, formatTime } from "@/utils/formatters";

export default {
  name: "BookAppointment",
  components: { DoctorCalendar },

  setup() {
    const router = useRouter();
    const store = useStore();

    const loadingDoctors = ref(true);
    const doctors = ref([]);
    const selectedDoctor = ref(null);
    const selectedSlot = ref(null);
    const appointmentNotes = ref("");
    const confirmed = ref(false);
    const booking = ref(false);
    const bookingError = ref("");

    const currentUser = computed(() => store.getters["auth/currentUser"]);

    const loadDoctors = async () => {
      try {
        const response = await DoctorService.getDoctors();
        doctors.value = response.data;
      } catch (error) {
        console.error("Failed to load doctors", error);
      } finally {
        loadingDoctors.value = false;
      }
    };

    const selectDoctor = async (doctor) => {
      selectedDoctor.value = doctor;
      selectedSlot.value = null;
      appointmentNotes.value = "";
      confirmed.value = false;
    };

    const selectSlot = (slot) => {
      selectedSlot.value = slot;
    };

    const clearSelection = () => {
      selectedDoctor.value = null;
      selectedSlot.value = null;
    };

    const clearSlotSelection = () => {
      selectedSlot.value = null;
      appointmentNotes.value = "";
      confirmed.value = false;
    };

    const bookAppointment = async () => {
      if (!selectedSlot.value) {
        bookingError.value = "Please select a slot.";
        return;
      }
      booking.value = true;
      bookingError.value = "";

      try {
        const patientId = currentUser.value.patient_id;
        if (!patientId) {
          bookingError.value = "Patient ID not found. Please login again.";
          booking.value = false;
          return;
        }

        const appointmentData = {
          doctor: selectedDoctor.value.id,
          patient: patientId,
          schedule: selectedSlot.value.id,
          notes: appointmentNotes.value || "",
        };

        const result = await store.dispatch(
          "appointments/createAppointment",
          appointmentData
        );

        if (result.success) {
          router.push("/appointment-confirmation");
        } else {
          bookingError.value =
            result.error || "Failed to book appointment. Please try again.";
        }
      } catch (error) {
        console.error("Failed to book appointment", error);
        bookingError.value = "Failed to book appointment. Please try again.";
      } finally {
        booking.value = false;
      }
    };

    onMounted(loadDoctors);

    watch(selectedSlot, () => {
      appointmentNotes.value = "";
      confirmed.value = false;
    });

    return {
      loadingDoctors,
      doctors,
      selectedDoctor,
      selectedSlot,
      appointmentNotes,
      confirmed,
      booking,
      bookingError,
      selectDoctor,
      selectSlot,
      clearSelection,
      clearSlotSelection,
      bookAppointment,
      formatDate,
      formatTime,
    };
  },
};
</script>

<style scoped>
.slot-card {
  cursor: pointer;
  transition: all 0.2s ease;
}
.slot-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.slot-card.selected {
  border-color: #28a745;
  background-color: #f8fff8;
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.2);
}
.doctor-calendar-wrapper {
  margin-bottom: 2.5rem;
}
</style>
