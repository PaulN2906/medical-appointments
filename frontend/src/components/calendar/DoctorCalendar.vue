<template>
  <div>
    <h2 class="mb-4">Doctor's Schedule</h2>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <FullCalendar :options="calendarOptions" class="doctor-calendar" />
    </div>

    <!-- Modal pentru adaugare/editare program -->
    <div class="modal fade" id="scheduleModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ isEditing ? "Edit Schedule" : "Add Schedule" }}
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveSchedule">
              <div class="mb-3">
                <label class="form-label">Date</label>
                <input
                  type="date"
                  class="form-control"
                  v-model="scheduleForm.date"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Start Time</label>
                <input
                  type="time"
                  class="form-control"
                  v-model="scheduleForm.startTime"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">End Time</label>
                <input
                  type="time"
                  class="form-control"
                  v-model="scheduleForm.endTime"
                  required
                />
              </div>

              <div class="mb-3 form-check">
                <input
                  type="checkbox"
                  class="form-check-input"
                  id="isAvailable"
                  v-model="scheduleForm.isAvailable"
                />
                <label class="form-check-label" for="isAvailable"
                  >Available</label
                >
              </div>

              <div class="text-end">
                <button
                  type="button"
                  class="btn btn-secondary me-2"
                  data-bs-dismiss="modal"
                >
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary">Save</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import { useStore } from "vuex";
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import DoctorService from "@/services/doctor.service";
import * as bootstrap from "bootstrap";

export default {
  name: "DoctorCalendar",
  components: {
    FullCalendar,
  },

  props: {
    doctorId: {
      type: Number,
      default: null,
    },
    editable: {
      type: Boolean,
      default: false,
    },
  },

  setup(props) {
    const store = useStore();
    const loading = ref(true);
    const events = ref([]);
    const isEditing = ref(false);
    const currentScheduleId = ref(null);
    const scheduleForm = ref({
      date: "",
      startTime: "",
      endTime: "",
      isAvailable: true,
    });

    // Obtinem datele utilizatorului din store
    const currentUser = computed(() => store.getters["auth/currentUser"]);

    // Configurare FullCalendar
    const calendarOptions = computed(() => ({
      plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
      initialView: "timeGridWeek",
      headerToolbar: {
        left: "prev,next today",
        center: "title",
        right: "dayGridMonth,timeGridWeek,timeGridDay",
      },
      events: events.value,
      selectable: props.editable,
      editable: props.editable,
      select: handleDateSelect,
      eventClick: handleEventClick,
      height: "auto",
    }));

    // Incarcam programul medicului
    const loadSchedule = async () => {
      loading.value = true;
      try {
        // Use doctor_id from current user or from props
        const doctorIdToUse =
          props.doctorId ||
          (currentUser.value ? currentUser.value.doctor_id : null);

        if (!doctorIdToUse) {
          console.error("No doctor ID available");
          return;
        }

        const response = await DoctorService.getSchedules(doctorIdToUse);

        // Convert data for FullCalendar
        events.value = response.data.map((schedule) => ({
          id: schedule.id,
          title: schedule.is_available ? "Available" : "Booked",
          start: `${schedule.date}T${schedule.start_time}`,
          end: `${schedule.date}T${schedule.end_time}`,
          backgroundColor: schedule.is_available ? "#28a745" : "#dc3545",
          extendedProps: {
            doctorId: schedule.doctor,
            isAvailable: schedule.is_available,
          },
        }));
      } catch (error) {
        console.error("Failed to load schedule", error);
      } finally {
        loading.value = false;
      }
    };

    // Gestionam selectia unei date (pentru adaugare)
    const handleDateSelect = (selectInfo) => {
      if (!props.editable) return;

      isEditing.value = false;
      currentScheduleId.value = null;

      const startDate = new Date(selectInfo.start);
      const endDate = new Date(selectInfo.end);

      scheduleForm.value = {
        date: startDate.toISOString().split("T")[0],
        startTime: startDate.toTimeString().substring(0, 5),
        endTime: endDate.toTimeString().substring(0, 5),
        isAvailable: true,
      };

      // Deschide modal pentru adaugare
      const modal = new bootstrap.Modal(
        document.getElementById("scheduleModal")
      );
      modal.show();
    };

    // Gestionam click pe un eveniment (pentru editare)
    const handleEventClick = (info) => {
      if (!props.editable) return;

      isEditing.value = true;
      currentScheduleId.value = info.event.id;

      const startDate = new Date(info.event.start);
      const endDate = new Date(info.event.end);

      scheduleForm.value = {
        date: startDate.toISOString().split("T")[0],
        startTime: startDate.toTimeString().substring(0, 5),
        endTime: endDate.toTimeString().substring(0, 5),
        isAvailable: info.event.extendedProps.isAvailable,
      };

      // Deschide modal pentru editare
      const modal = new bootstrap.Modal(
        document.getElementById("scheduleModal")
      );
      modal.show();
    };

    // Salvam programul (adaugare sau editare)
    const saveSchedule = async () => {
      try {
        const scheduleData = {
          doctor: props.doctorId || currentUser.value.id,
          date: scheduleForm.value.date,
          start_time: scheduleForm.value.startTime + ":00",
          end_time: scheduleForm.value.endTime + ":00",
          is_available: scheduleForm.value.isAvailable,
        };

        if (isEditing.value && currentScheduleId.value) {
          await DoctorService.updateSchedule(
            currentScheduleId.value,
            scheduleData
          );
        } else {
          await DoctorService.createSchedule(scheduleData);
        }

        // Reincarca programul
        await loadSchedule();

        // Inchide modalul
        const modalElement = document.getElementById("scheduleModal");
        const modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();
      } catch (error) {
        console.error("Failed to save schedule", error);
        alert("Failed to save schedule. Please try again.");
      }
    };

    onMounted(() => {
      loadSchedule();
    });

    return {
      loading,
      calendarOptions,
      isEditing,
      scheduleForm,
      saveSchedule,
    };
  },
};
</script>

<style>
.doctor-calendar {
  height: 600px;
  margin-bottom: 30px;
}
</style>
