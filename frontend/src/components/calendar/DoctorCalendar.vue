<template>
  <div>
    <h2 class="mb-4">Doctor's Schedule</h2>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <div class="doctor-calendar-wrapper mb-4">
        <FullCalendar ref="calendarRef" :options="calendarOptions" />
      </div>
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
import { ref, onMounted, computed, defineExpose, watch } from "vue";
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
      required: true,
    },
    editable: {
      type: Boolean,
      default: false,
    },
    showUnavailable: {
      type: Boolean,
      default: true,
    },
    allowSelect: {
      type: Boolean,
      default: false,
    },
  },

  emits: ["dateSelect", "eventClick", "selectSlot"],

  setup(props, { emit }) {
    const store = useStore();
    const loading = ref(true);
    // ref pentru acces la instanta FullCalendar
    const calendarRef = ref(null);
    const events = ref([]);
    const filteredEvents = computed(() => {
      return props.showUnavailable
        ? events.value
        : events.value.filter((evt) => evt.extendedProps.isAvailable);
    });
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
      events: filteredEvents.value,
      selectable: props.editable,
      editable: props.editable,
      select: handleDateSelect,
      eventClick: handleEventClick,
      height: "auto",
      contentHeight: "auto",
      expandRows: true,
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
      const isAvailable = info.event.extendedProps.isAvailable;
      // daca allowSelect e true si slotul e disponibil, trimitem datele inapoi
      if (props.allowSelect && isAvailable) {
        emit("selectSlot", {
          id: info.event.id,
          date: info.event.startStr.split("T")[0],
          start_time: info.event.startStr.split("T")[1].substr(0, 5),
          end_time: info.event.endStr.split("T")[1].substr(0, 5),
        });
        return;
      }

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
        const doctorIdToUse = props.doctorId;
        const scheduleData = {
          doctor: doctorIdToUse,
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
      } catch (err) {
        console.error("Failed to save schedule", err);
        // show server message if available
        const msg =
          err.response?.data?.error ||
          err.response?.data?.detail ||
          err.message ||
          "Please try again.";
        alert("Failed to save schedule: " + msg);
        return;
      }

      try {
        await loadSchedule();
      } catch (reloadErr) {
        console.warn(
          "Schedule saved, but failed to reload calendar:",
          reloadErr
        );
      }

      // close the modal
      const modalEl = document.getElementById("scheduleModal");
      bootstrap.Modal.getInstance(modalEl).hide();
    };

    // expunem doua metode catre componenta parinte
    function refreshCalendar() {
      calendarRef.value?.getApi().refetchEvents();
    }

    async function reloadSchedule() {
      await loadSchedule();
      calendarRef.value?.getApi().refetchEvents();
    }

    watch(
      () => props.showUnavailable,
      () => {
        calendarRef.value?.getApi().refetchEvents();
      }
    );

    // permitem parintelui sa apeleze metodele de mai sus
    defineExpose({ refreshCalendar, reloadSchedule });

    onMounted(() => {
      loadSchedule();
    });

    return {
      loading,
      calendarRef,
      calendarOptions,
      isEditing,
      scheduleForm,
      saveSchedule,
    };
  },
};
</script>

<style>
.doctor-calendar-wrapper {
  margin-bottom: 2.5rem;
}
</style>
