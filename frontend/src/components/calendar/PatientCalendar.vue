<template>
  <div>
    <div v-if="loading" class="text-center p-4">
      <LoadingSpinner />
    </div>

    <div v-else>
      <div class="patient-calendar-wrapper mb-4">
        <FullCalendar ref="calendarRef" :options="calendarOptions" />
      </div>
    </div>

    <!-- Legend -->
    <div class="row mt-3">
      <div class="col-md-12">
        <div class="card">
          <div class="card-body">
            <h6 class="card-title">
              <i class="bi bi-info-circle me-2"></i>Legend
            </h6>
            <div class="row">
              <div class="col-md-3">
                <span class="badge bg-warning me-2">●</span>
                <small>Pending</small>
              </div>
              <div class="col-md-3">
                <span class="badge bg-success me-2">●</span>
                <small>Confirmed</small>
              </div>
              <div class="col-md-3">
                <span class="badge bg-danger me-2">●</span>
                <small>Cancelled</small>
              </div>
              <div class="col-md-3">
                <span class="badge bg-info me-2">●</span>
                <small>Completed</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointment Details Modal -->
    <div
      class="modal fade"
      id="appointmentModal"
      tabindex="-1"
      aria-hidden="true"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Appointment Details</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body" v-if="selectedAppointment">
            <div class="mb-3">
              <strong>Doctor:</strong> {{ getDoctorName(selectedAppointment) }}
            </div>
            <div class="mb-3">
              <strong>Speciality:</strong>
              {{ selectedAppointment.doctor_details?.speciality }}
            </div>
            <div class="mb-3">
              <strong>Date:</strong>
              {{ formatDate(selectedAppointment.schedule_details?.date) }}
            </div>
            <div class="mb-3">
              <strong>Time:</strong>
              {{ formatTime(selectedAppointment.schedule_details?.start_time) }}
              -
              {{ formatTime(selectedAppointment.schedule_details?.end_time) }}
            </div>
            <div class="mb-3">
              <strong>Status:</strong>
              <span :class="getStatusClass(selectedAppointment.status)">
                {{ selectedAppointment.status }}
              </span>
            </div>
            <div class="mb-3" v-if="selectedAppointment.notes">
              <strong>Notes:</strong>
              <p class="mb-0">{{ selectedAppointment.notes }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
            >
              Close
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="viewFullDetails"
              data-bs-dismiss="modal"
            >
              View Full Details
            </button>
            <button
              v-if="canCancelAppointment"
              type="button"
              class="btn btn-danger"
              @click="cancelAppointment"
              data-bs-dismiss="modal"
            >
              Cancel Appointment
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import * as bootstrap from "bootstrap";
import {
  getDoctorName,
  formatDate,
  formatTime,
  getStatusClass,
  isPast,
} from "@/utils/formatters";

export default {
  name: "PatientCalendar",
  components: {
    FullCalendar,
  },

  props: {
    statusFilter: {
      type: String,
      default: "all",
    },
    height: {
      type: [String, Number],
      default: "auto",
    },
  },

  setup(props) {
    const store = useStore();
    const router = useRouter();
    const loading = ref(true);
    const calendarRef = ref(null);
    const selectedAppointment = ref(null);

    // Get appointments from store
    const allAppointments = computed(
      () => store.getters["appointments/allAppointments"]
    );

    // Filter appointments based on status filter
    const filteredAppointments = computed(() => {
      let filtered = allAppointments.value;

      switch (props.statusFilter) {
        case "upcoming":
          filtered = filtered.filter(
            (apt) =>
              ["pending", "confirmed"].includes(apt.status) &&
              !isPast(apt.schedule_details?.date)
          );
          break;
        case "past":
          filtered = filtered.filter(
            (apt) =>
              isPast(apt.schedule_details?.date) || apt.status === "completed"
          );
          break;
        case "pending":
          filtered = filtered.filter((apt) => apt.status === "pending");
          break;
        case "confirmed":
          filtered = filtered.filter((apt) => apt.status === "confirmed");
          break;
        case "cancelled":
          filtered = filtered.filter((apt) => apt.status === "cancelled");
          break;
        // "all" or default - no filtering
      }

      return filtered;
    });

    // Convert appointments to calendar events
    const events = computed(() => {
      return filteredAppointments.value.map((appointment) => ({
        id: appointment.id,
        title: `${formatTime(appointment.schedule_details.start_time)} - Dr. ${
          appointment.doctor_details.user.last_name
        }`,
        start: `${appointment.schedule_details.date}T${appointment.schedule_details.start_time}`,
        end: `${appointment.schedule_details.date}T${appointment.schedule_details.end_time}`,
        backgroundColor: getStatusColor(appointment.status),
        borderColor: getStatusColor(appointment.status),
        textColor: getTextColor(appointment.status),
        extendedProps: {
          appointmentId: appointment.id,
          status: appointment.status,
          doctorName: appointment.doctor_details.user.last_name,
          speciality: appointment.doctor_details.speciality,
          appointmentData: appointment,
        },
      }));
    });

    // Calendar configuration
    const calendarOptions = computed(() => ({
      plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
      initialView: "dayGridMonth",
      headerToolbar: {
        left: "prev,next today",
        center: "title",
        right: "dayGridMonth,timeGridWeek,timeGridDay",
      },
      events: events.value,
      eventClick: handleEventClick,
      height: props.height,
      editable: false,
      selectable: false,
      eventDisplay: "block",
      dayMaxEvents: 3,
      moreLinkClick: "popover",
      eventDidMount: function (info) {
        // Add tooltip
        info.el.setAttribute(
          "title",
          getTooltipText(info.event.extendedProps.appointmentData)
        );
      },
    }));

    // Get color based on appointment status
    const getStatusColor = (status) => {
      const colors = {
        pending: "#ffc107", // warning yellow
        confirmed: "#28a745", // success green
        cancelled: "#dc3545", // danger red
        completed: "#17a2b8", // info blue
      };
      return colors[status] || "#6c757d";
    };

    // Get text color for readability
    const getTextColor = (status) => {
      return status === "pending" ? "#000" : "#fff";
    };

    // Generate tooltip text
    const getTooltipText = (appointment) => {
      return `${getDoctorName(appointment)} - ${
        appointment.doctor_details.speciality
      }\n${formatTime(appointment.schedule_details.start_time)} - ${formatTime(
        appointment.schedule_details.end_time
      )}\nStatus: ${appointment.status}`;
    };

    // Handle event click
    const handleEventClick = (info) => {
      selectedAppointment.value = info.event.extendedProps.appointmentData;
      const modal = new bootstrap.Modal(
        document.getElementById("appointmentModal")
      );
      modal.show();
    };

    // Check if appointment can be cancelled
    const canCancelAppointment = computed(() => {
      if (!selectedAppointment.value) return false;

      const canCancel = ["pending", "confirmed"].includes(
        selectedAppointment.value.status
      );
      const notPast = !isPast(selectedAppointment.value.schedule_details?.date);

      return canCancel && notPast;
    });

    // Navigate to full appointment details
    const viewFullDetails = () => {
      if (selectedAppointment.value) {
        router.push(`/appointments/${selectedAppointment.value.id}`);
      }
    };

    // Cancel appointment
    const cancelAppointment = async () => {
      if (!selectedAppointment.value) return;

      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      try {
        const result = await store.dispatch(
          "appointments/cancelAppointment",
          selectedAppointment.value.id
        );

        if (result.success) {
          // Refresh calendar
          calendarRef.value?.getApi().refetchEvents();
          alert("Appointment cancelled successfully!");
        } else {
          alert(
            result.error || "Failed to cancel appointment. Please try again."
          );
        }
      } catch (error) {
        console.error("Failed to cancel appointment", error);
        alert("Failed to cancel appointment. Please try again.");
      }
    };

    // Load appointments
    const loadAppointments = async () => {
      loading.value = true;
      try {
        await store.dispatch("appointments/fetchAppointments");
      } catch (error) {
        console.error("Failed to load appointments", error);
      } finally {
        loading.value = false;
      }
    };

    // Refresh calendar when events change
    const refreshCalendar = () => {
      if (calendarRef.value) {
        calendarRef.value.getApi().refetchEvents();
      }
    };

    onMounted(() => {
      loadAppointments();
    });

    return {
      loading,
      calendarRef,
      calendarOptions,
      selectedAppointment,
      canCancelAppointment,
      handleEventClick,
      viewFullDetails,
      cancelAppointment,
      refreshCalendar,
      getDoctorName,
      formatDate,
      formatTime,
      getStatusClass,
    };
  },
};
</script>

<style scoped>
.patient-calendar-wrapper {
  margin-bottom: 2rem;
}

/* Calendar styling */
:deep(.fc-event) {
  cursor: pointer;
  font-size: 0.875rem;
  border-radius: 4px;
  padding: 2px 4px;
}

:deep(.fc-event:hover) {
  opacity: 0.8;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

:deep(.fc-daygrid-event) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.fc-event-title) {
  font-weight: 500;
}

/* Today highlighting */
:deep(.fc-day-today) {
  background-color: rgba(255, 193, 7, 0.1) !important;
}

/* Legend styling */
.badge {
  font-size: 1rem;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}
</style>
