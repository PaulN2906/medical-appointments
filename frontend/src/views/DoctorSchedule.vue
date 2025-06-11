<template>
  <div class="container my-4">
    <h1 class="mb-4">Manage Schedule</h1>

    <div class="row mb-4">
      <div class="col-md-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <button @click="openBulkCreateModal" class="btn btn-primary me-2">
              <i class="bi bi-calendar-plus"></i> Add Multiple Slots
            </button>
            <button @click="openAddSlotModal" class="btn btn-outline-primary">
              <i class="bi bi-plus-circle"></i> Add Single Slot
            </button>
          </div>
          <div>
            <div class="form-check form-switch">
              <input
                class="form-check-input"
                type="checkbox"
                id="showUnavailable"
                v-model="showUnavailable"
              />
              <label class="form-check-label" for="showUnavailable"
                >Show Booked Slots</label
              >
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">My Schedule</div>
          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else>
              <DoctorCalendar
                v-if="doctorId"
                :doctorId="currentUser.doctor_id"
                :editable="true"
                :showUnavailable="showUnavailable"
                @dateSelect="handleDateSelect"
                @eventClick="handleEventClick"
                ref="calendar"
              />
              <div v-else class="alert alert-info">
                Please log in as a doctor to manage your schedule
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal pentru adaugarea unui slot -->
    <div class="modal fade" id="addSlotModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ isEditing ? "Edit Slot" : "Add New Slot" }}
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveSlot">
              <div class="mb-3">
                <label for="slotDate" class="form-label">Date</label>
                <input
                  type="date"
                  class="form-control"
                  id="slotDate"
                  v-model="slotForm.date"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="startTime" class="form-label">Start Time</label>
                <input
                  type="time"
                  class="form-control"
                  id="startTime"
                  v-model="slotForm.startTime"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="endTime" class="form-label">End Time</label>
                <input
                  type="time"
                  class="form-control"
                  id="endTime"
                  v-model="slotForm.endTime"
                  required
                />
              </div>

              <div
                class="mb-3 form-check"
                v-if="isEditing && !slotForm.isAvailable"
              >
                <input
                  type="checkbox"
                  class="form-check-input"
                  id="cancelAppointment"
                  v-model="slotForm.cancelAppointment"
                />
                <label class="form-check-label" for="cancelAppointment">
                  Cancel existing appointment (this will notify the patient)
                </label>
              </div>

              <div class="alert alert-danger" v-if="error">{{ error }}</div>

              <div class="d-flex justify-content-end">
                <button
                  type="button"
                  class="btn btn-secondary me-2"
                  data-bs-dismiss="modal"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="saving"
                >
                  <span
                    v-if="saving"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                  ></span>
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal pentru adaugarea de sloturi multiple -->
    <div
      class="modal fade"
      id="bulkCreateModal"
      tabindex="-1"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add Multiple Slots</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveBulkSlots">
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Date Range</label>
                  <div class="input-group">
                    <input
                      type="date"
                      class="form-control"
                      v-model="bulkForm.startDate"
                      required
                    />
                    <span class="input-group-text">to</span>
                    <input
                      type="date"
                      class="form-control"
                      v-model="bulkForm.endDate"
                      required
                    />
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Days of Week</label>
                  <div>
                    <div
                      class="form-check form-check-inline"
                      v-for="(day, index) in daysOfWeek"
                      :key="index"
                    >
                      <input
                        class="form-check-input"
                        type="checkbox"
                        :id="`day-${index}`"
                        :value="index"
                        v-model="bulkForm.selectedDays"
                      />
                      <label class="form-check-label" :for="`day-${index}`">{{
                        day
                      }}</label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Time Slots</label>
                  <div
                    v-for="(slot, index) in bulkForm.timeSlots"
                    :key="index"
                    class="d-flex mb-2"
                  >
                    <input
                      type="time"
                      class="form-control me-2"
                      v-model="slot.start"
                      required
                    />
                    <span class="input-group-text">to</span>
                    <input
                      type="time"
                      class="form-control ms-2"
                      v-model="slot.end"
                      required
                    />
                    <button
                      type="button"
                      @click="removeTimeSlot(index)"
                      class="btn btn-outline-danger ms-2"
                      v-if="bulkForm.timeSlots.length > 1"
                    >
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                  <button
                    type="button"
                    @click="addTimeSlot"
                    class="btn btn-outline-secondary mt-2"
                  >
                    <i class="bi bi-plus"></i> Add Time Slot
                  </button>
                </div>
                <div class="col-md-6">
                  <div class="card">
                    <div class="card-header">Summary</div>
                    <div class="card-body">
                      <p>
                        This will create {{ calculateTotalSlots() }} time slots
                        over {{ calculateDays() }} days.
                      </p>
                      <ul>
                        <li
                          v-for="(day, index) in getSelectedDays()"
                          :key="index"
                        >
                          {{ day }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <div class="alert alert-danger" v-if="bulkError">
                {{ bulkError }}
              </div>

              <div class="d-flex justify-content-end">
                <button
                  type="button"
                  class="btn btn-secondary me-2"
                  data-bs-dismiss="modal"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="bulkSaving"
                >
                  <span
                    v-if="bulkSaving"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                  ></span>
                  Create Slots
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
import * as bootstrap from "bootstrap";
import { ref, reactive, onMounted, computed } from "vue";
import DoctorService from "@/services/doctor.service";
import DoctorCalendar from "@/components/calendar/DoctorCalendar.vue";
import { useStore } from "vuex";

export default {
  name: "DoctorSchedule",
  components: {
    DoctorCalendar,
  },

  setup() {
    const store = useStore();
    const calendar = ref(null);

    const loading = ref(true);
    const saving = ref(false);
    const bulkSaving = ref(false);
    const error = ref("");
    const bulkError = ref("");
    const isEditing = ref(false);
    const currentSlotId = ref(null);
    const showUnavailable = ref(true);

    // Formular pentru adaugarea/editarea unui slot
    const slotForm = reactive({
      date: "",
      startTime: "",
      endTime: "",
      isAvailable: true,
      cancelAppointment: false,
    });

    // Formular pentru adaugarea de sloturi multiple
    const bulkForm = reactive({
      startDate: "",
      endDate: "",
      selectedDays: [1, 2, 3, 4, 5], // Default: luni până vineri
      timeSlots: [{ start: "09:00", end: "10:00" }],
    });

    // Utilizatorul curent
    const currentUser = computed(() => store.getters["auth/currentUser"]);
    const doctorId = computed(() => {
      return currentUser.value?.doctor_id ?? null;
    });

    // Zile ale saptamanii
    const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

    // Deschide modalul pentru adaugarea unui slot individual
    const openAddSlotModal = () => {
      isEditing.value = false;
      currentSlotId.value = null;
      resetSlotForm();

      const modal = new bootstrap.Modal(
        document.getElementById("addSlotModal")
      );
      modal.show();
    };

    // Deschide modalul pentru adaugarea de sloturi multiple
    const openBulkCreateModal = () => {
      resetBulkForm();

      const modal = new bootstrap.Modal(
        document.getElementById("bulkCreateModal")
      );
      modal.show();
    };

    // Reseteaza formularul pentru slot individual
    const resetSlotForm = () => {
      const today = new Date().toISOString().split("T")[0];
      slotForm.date = today;
      slotForm.startTime = "09:00";
      slotForm.endTime = "10:00";
      slotForm.isAvailable = true;
      slotForm.cancelAppointment = false;
      error.value = "";
    };

    // Reseteaza formularul pentru sloturi multiple
    const resetBulkForm = () => {
      const today = new Date();
      const nextWeek = new Date(today);
      nextWeek.setDate(today.getDate() + 7);

      bulkForm.startDate = today.toISOString().split("T")[0];
      bulkForm.endDate = nextWeek.toISOString().split("T")[0];
      bulkForm.selectedDays = [1, 2, 3, 4, 5]; // Luni-Vineri
      bulkForm.timeSlots = [{ start: "09:00", end: "10:00" }];
      bulkError.value = "";
    };

    // Gestioneaza selectia din calendar
    const handleDateSelect = (info) => {
      isEditing.value = false;
      currentSlotId.value = null;

      const selectedDate = info.start;

      slotForm.date = selectedDate.toISOString().split("T")[0];
      slotForm.startTime = selectedDate.toTimeString().substring(0, 5);

      const endDate = info.end;
      slotForm.endTime = endDate.toTimeString().substring(0, 5);

      const modal = new bootstrap.Modal(
        document.getElementById("addSlotModal")
      );
      modal.show();
    };

    // Gestioneaza click pe un eveniment din calendar
    const handleEventClick = (info) => {
      isEditing.value = true;
      currentSlotId.value = info.event.id;

      const startDate = info.event.start;
      const endDate = info.event.end;

      slotForm.date = startDate.toISOString().split("T")[0];
      slotForm.startTime = startDate.toTimeString().substring(0, 5);
      slotForm.endTime = endDate.toTimeString().substring(0, 5);
      slotForm.isAvailable = info.event.extendedProps.isAvailable;
      slotForm.cancelAppointment = false;

      const modal = new bootstrap.Modal(
        document.getElementById("addSlotModal")
      );
      modal.show();
    };

    // Salveaza un slot
    const saveSlot = async () => {
      error.value = "";
      saving.value = true;

      try {
        // Get doctor_id from user data
        const doctorId = currentUser.value.doctor_id;
        if (!doctorId) {
          error.value = "Doctor ID not found. Please login again.";
          saving.value = false;
          return;
        }

        const scheduleData = {
          doctor: doctorId,
          date: slotForm.date,
          start_time: slotForm.startTime + ":00",
          end_time: slotForm.endTime + ":00",
          is_available: slotForm.isAvailable,
        };

        if (isEditing.value && currentSlotId.value) {
          await DoctorService.updateSchedule(currentSlotId.value, scheduleData);
        } else {
          await DoctorService.createSchedule(scheduleData);
        }
      } catch (err) {
        console.error("Failed to save slot", err);
        error.value =
          err.response?.data?.error ||
          (Array.isArray(err.response?.data?.doctor)
            ? err.response.data.doctor[0]
            : err.response?.data?.detail) ||
          "Failed to save slot. Please try again.";
        saving.value = false;
        return;
      }
      // Reload calendar
      if (calendar.value?.reloadSchedule) {
        try {
          await calendar.value.reloadSchedule();
        } catch (reloadErr) {
          console.warn("Slot saved, but calendar failed to reload:", reloadErr);
        }
      }

      const modalElement = document.getElementById("addSlotModal");
      bootstrap.Modal.getInstance(modalElement).hide();
      resetSlotForm();
      saving.value = false;
    };

    // Adauga un nou rand de time slot in formularul pentru sloturi multiple
    const addTimeSlot = () => {
      bulkForm.timeSlots.push({ start: "09:00", end: "10:00" });
    };

    // Elimina un rand de time slot din formularul pentru sloturi multiple
    const removeTimeSlot = (index) => {
      if (bulkForm.timeSlots.length > 1) {
        bulkForm.timeSlots.splice(index, 1);
      }
    };

    // Calculeaza nr total de sloturi care vor fi create
    const calculateTotalSlots = () => {
      const start = new Date(bulkForm.startDate);
      const end = new Date(bulkForm.endDate);
      let totalDays = 0;

      // Calculam nr de zile care corespund zilelor selectate
      for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        if (bulkForm.selectedDays.includes(d.getDay())) {
          totalDays++;
        }
      }

      return totalDays * bulkForm.timeSlots.length;
    };

    // Calculeaza numarul de zile pentru care se vor crea sloturi
    const calculateDays = () => {
      const start = new Date(bulkForm.startDate);
      const end = new Date(bulkForm.endDate);
      let totalDays = 0;

      for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        if (bulkForm.selectedDays.includes(d.getDay())) {
          totalDays++;
        }
      }

      return totalDays;
    };

    // Obtine lista zilelor selectate pentru afisare in rezumat
    const getSelectedDays = () => {
      return bulkForm.selectedDays.map((day) => daysOfWeek[day]);
    };

    // Salveaza sloturile multiple
    const saveBulkSlots = async () => {
      bulkError.value = "";
      bulkSaving.value = true;

      try {
        // Validam datele
        const startDate = new Date(bulkForm.startDate);
        const endDate = new Date(bulkForm.endDate);

        if (startDate > endDate) {
          bulkError.value = "End date must be after start date";
          bulkSaving.value = false;
          return;
        }

        if (bulkForm.selectedDays.length === 0) {
          bulkError.value = "Select at least one day of the week";
          bulkSaving.value = false;
          return;
        }

        // Generam toate sloturile
        const slots = [];

        // Pentru fiecare zi in intervalul selectat
        for (
          let d = new Date(startDate);
          d <= endDate;
          d.setDate(d.getDate() + 1)
        ) {
          // Verificam daca ziua curenta este in zilele selectate
          if (bulkForm.selectedDays.includes(d.getDay())) {
            const currentDate = d.toISOString().split("T")[0];

            // Pentru fiecare interval orar
            for (const timeSlot of bulkForm.timeSlots) {
              slots.push({
                doctor: currentUser.value.doctor_id,
                date: currentDate,
                start_time: timeSlot.start + ":00",
                end_time: timeSlot.end + ":00",
                is_available: true,
              });
            }
          }
        }

        // Salvam toate sloturile intr-un singur request
        if (slots.length > 0) {
          await DoctorService.createBulkSchedules(slots);
        }

        // Check if calendar exists and has the method before calling
        if (
          calendar.value &&
          typeof calendar.value.reloadSchedule === "function"
        ) {
          try {
            await calendar.value.reloadSchedule();
          } catch (reloadError) {
            console.warn(
              "Calendar reload failed, but slots were created:",
              reloadError
            );
            // Manual page refresh as fallback
            window.location.reload();
          }
        } else {
          console.warn(
            "Calendar component not available for refresh, reloading page"
          );
          // Fallback: reload the page
          window.location.reload();
        }

        // Inchidem modalul
        const modalElement = document.getElementById("bulkCreateModal");
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
          modal.hide();
        }

        alert(`Successfully created ${slots.length} time slots.`);
      } catch (error) {
        console.error("Failed to create bulk slots", error);
        bulkError.value =
          error.response?.data?.error ||
          "Failed to create slots. Please try again.";
      } finally {
        bulkSaving.value = false;
      }
    };

    onMounted(() => {
      loading.value = false;
    });

    return {
      loading,
      saving,
      bulkSaving,
      error,
      bulkError,
      isEditing,
      showUnavailable,
      slotForm,
      bulkForm,
      calendar,
      daysOfWeek,
      openAddSlotModal,
      openBulkCreateModal,
      handleDateSelect,
      handleEventClick,
      saveSlot,
      addTimeSlot,
      removeTimeSlot,
      calculateTotalSlots,
      calculateDays,
      getSelectedDays,
      saveBulkSlots,
      currentUser,
      doctorId,
    };
  },
};
</script>

<style scoped>
/* Stilizare specifica paginii */
</style>
