<template>
  <div class="container my-4">
    <h1 class="mb-4">Book an Appointment</h1>

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

    <div v-if="selectedDoctor" class="row mt-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">Select Date and Time</div>
          <div class="card-body">
            <div v-if="loadingSchedule" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else>
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

              <DoctorCalendar
                :doctorId="selectedDoctor.id"
                :editable="false"
                @selectSlot="selectTimeSlot"
              />

              <div class="mt-4">
                <h4>Available Time Slots</h4>
                <div
                  v-if="availableSlots.length === 0"
                  class="alert alert-info"
                >
                  No available slots for the selected date. Please select
                  another date.
                </div>

                <div v-else class="row">
                  <div
                    class="col-md-3 mb-3"
                    v-for="slot in availableSlots"
                    :key="slot.id"
                  >
                    <div
                      class="card h-100 slot-card"
                      :class="{
                        selected: selectedSlot && selectedSlot.id === slot.id,
                      }"
                      @click="selectSlot(slot)"
                    >
                      <div class="card-body text-center">
                        <h5 class="card-title">{{ formatDate(slot.date) }}</h5>
                        <p class="card-text">
                          {{ formatTime(slot.start_time) }} -
                          {{ formatTime(slot.end_time) }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedSlot" class="row mt-4">
      <div class="col-md-12">
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
                >
                </textarea>
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
                  I confirm that the information provided is correct and I will
                  attend this appointment
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
</template>

<script>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import DoctorService from "@/services/doctor.service";
import AppointmentService from "@/services/appointment.service";
import DoctorCalendar from "@/components/calendar/DoctorCalendar.vue";
import { useStore } from "vuex";

export default {
  name: "BookAppointment",
  components: {
    DoctorCalendar,
  },

  setup() {
    const router = useRouter();
    const store = useStore();

    const loadingDoctors = ref(true);
    const loadingSchedule = ref(false);
    const doctors = ref([]);
    const selectedDoctor = ref(null);
    const availableSlots = ref([]);
    const selectedSlot = ref(null);
    const appointmentNotes = ref("");
    const confirmed = ref(false);
    const booking = ref(false);
    const bookingError = ref("");

    // Obtine utilizatorul curent din store
    const currentUser = store.getters["auth/currentUser"];

    // Incarca lista medicilor
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

    // Selecteaza un medic si incarca programul disponibil
    const selectDoctor = async (doctor) => {
      selectedDoctor.value = doctor;
      loadingSchedule.value = true;

      try {
        const response = await DoctorService.getSchedules(doctor.id);
        // Filtram doar sloturile disponibile
        availableSlots.value = response.data.filter(
          (slot) => slot.is_available
        );
      } catch (error) {
        console.error("Failed to load doctor schedule", error);
      } finally {
        loadingSchedule.value = false;
      }
    };

    // Selecteaza un slot de timp pentru programare
    const selectSlot = (slot) => {
      selectedSlot.value = slot;
    };

    // Handler pentru selectia din calendar
    const selectTimeSlot = (slotInfo) => {
      // Implementare pentru selecția din calendar interactiv
      console.log("Time slot selected:", slotInfo);
    };

    // Curata selectia medicului
    const clearSelection = () => {
      selectedDoctor.value = null;
      selectedSlot.value = null;
      availableSlots.value = [];
    };

    // Curata selectia slotului de timp
    const clearSlotSelection = () => {
      selectedSlot.value = null;
    };

    // Creaza programarea
    const bookAppointment = async () => {
      if (!selectedDoctor.value || !selectedSlot.value || !confirmed.value) {
        return;
      }

      booking.value = true;
      bookingError.value = "";

      try {
        const appointmentData = {
          doctor: selectedDoctor.value.id,
          patient: currentUser.id, // ID-ul pacientului trebuie sa fie disponibil
          schedule: selectedSlot.value.id,
          notes: appointmentNotes.value,
        };

        await AppointmentService.createAppointment(appointmentData);

        // Redirectioneaza catre dashboard sau pagina de confirmare
        router.push("/appointment-confirmation");
      } catch (error) {
        console.error("Failed to book appointment", error);
        bookingError.value =
          error.response?.data?.error ||
          "Failed to book appointment. Please try again.";
      } finally {
        booking.value = false;
      }
    };

    // Helper pentru formatarea datelor si orelor
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

    onMounted(() => {
      loadDoctors();
    });

    return {
      loadingDoctors,
      loadingSchedule,
      doctors,
      selectedDoctor,
      availableSlots,
      selectedSlot,
      appointmentNotes,
      confirmed,
      booking,
      bookingError,
      selectDoctor,
      selectSlot,
      selectTimeSlot,
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
</style>
