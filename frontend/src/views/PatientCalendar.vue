<template>
  <div class="container my-4">
    <h1 class="mb-4">My Appointments Calendar</h1>

    <!-- Filter Controls -->
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-body">
            <h6 class="card-title">
              <i class="bi bi-funnel me-2"></i>Filter Appointments
            </h6>
            <div class="btn-group" role="group" aria-label="Status filter">
              <input
                type="radio"
                class="btn-check"
                name="statusFilter"
                id="filterAll"
                value="all"
                v-model="statusFilter"
              />
              <label class="btn btn-outline-primary" for="filterAll">
                All ({{ allCount }})
              </label>

              <input
                type="radio"
                class="btn-check"
                name="statusFilter"
                id="filterUpcoming"
                value="upcoming"
                v-model="statusFilter"
              />
              <label class="btn btn-outline-success" for="filterUpcoming">
                Upcoming ({{ upcomingCount }})
              </label>

              <input
                type="radio"
                class="btn-check"
                name="statusFilter"
                id="filterPending"
                value="pending"
                v-model="statusFilter"
              />
              <label class="btn btn-outline-warning" for="filterPending">
                Pending ({{ pendingCount }})
              </label>

              <input
                type="radio"
                class="btn-check"
                name="statusFilter"
                id="filterPast"
                value="past"
                v-model="statusFilter"
              />
              <label class="btn btn-outline-secondary" for="filterPast">
                Past ({{ pastCount }})
              </label>

              <input
                type="radio"
                class="btn-check"
                name="statusFilter"
                id="filterCancelled"
                value="cancelled"
                v-model="statusFilter"
              />
              <label class="btn btn-outline-danger" for="filterCancelled">
                Cancelled ({{ cancelledCount }})
              </label>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card">
          <div class="card-body text-center">
            <h6 class="card-title">
              <i class="bi bi-plus-circle me-2"></i>Need an Appointment?
            </h6>
            <router-link to="/book-appointment" class="btn btn-success w-100">
              <i class="bi bi-calendar-plus me-2"></i>
              Book New Appointment
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar -->
    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div
            class="card-header d-flex justify-content-between align-items-center"
          >
            <div>
              <i class="bi bi-calendar-event me-2"></i>
              <span>My Appointments</span>
              <small class="text-muted ms-2">
                ({{ getFilterDescription() }})
              </small>
            </div>
            <div class="btn-group btn-group-sm">
              <button
                class="btn"
                :class="
                  viewMode === 'calendar'
                    ? 'btn-primary'
                    : 'btn-outline-primary'
                "
                @click="viewMode = 'calendar'"
              >
                <i class="bi bi-calendar-event"></i> Calendar
              </button>
              <button
                class="btn"
                :class="
                  viewMode === 'list' ? 'btn-primary' : 'btn-outline-primary'
                "
                @click="viewMode = 'list'"
              >
                <i class="bi bi-list-ul"></i> List
              </button>
            </div>
          </div>

          <div class="card-body">
            <!-- Calendar View -->
            <div v-if="viewMode === 'calendar'">
              <PatientCalendar :statusFilter="statusFilter" />
            </div>

            <!-- List View -->
            <div v-else>
              <div
                v-if="filteredAppointments.length === 0"
                class="text-center p-5"
              >
                <i class="bi bi-calendar-x fs-1 text-muted"></i>
                <p class="mt-3 mb-4">
                  No {{ statusFilter }} appointments found.
                </p>
                <router-link
                  v-if="statusFilter === 'upcoming'"
                  to="/book-appointment"
                  class="btn btn-primary"
                >
                  Book Your First Appointment
                </router-link>
              </div>

              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Doctor</th>
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
                      :class="getRowClass(appointment)"
                    >
                      <td>
                        <div>
                          <strong>{{ getDoctorName(appointment) }}</strong>
                          <br />
                          <small class="text-muted">{{
                            appointment.doctor_details?.speciality
                          }}</small>
                        </div>
                      </td>
                      <td>
                        {{ formatDate(appointment.schedule_details?.date) }}
                        <span
                          v-if="isToday(appointment.schedule_details?.date)"
                          class="badge bg-primary ms-2"
                        >
                          Today
                        </span>
                      </td>
                      <td>
                        {{
                          formatTime(appointment.schedule_details?.start_time)
                        }}
                        -
                        {{ formatTime(appointment.schedule_details?.end_time) }}
                      </td>
                      <td>
                        <span :class="getStatusClass(appointment.status)">
                          {{ appointment.status }}
                        </span>
                      </td>
                      <td>
                        <div class="btn-group btn-group-sm">
                          <button
                            @click="viewAppointment(appointment.id)"
                            class="btn btn-outline-info"
                            title="View Details"
                          >
                            <i class="bi bi-eye"></i>
                          </button>
                          <button
                            v-if="canCancelAppointment(appointment)"
                            @click="cancelAppointment(appointment.id)"
                            class="btn btn-outline-danger"
                            title="Cancel"
                          >
                            <i class="bi bi-x-circle"></i>
                          </button>
                        </div>
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

    <!-- Quick Stats -->
    <div class="row mt-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <i class="bi bi-graph-up me-2"></i>Appointment Summary
          </div>
          <div class="card-body">
            <div class="row text-center">
              <div class="col-md-2">
                <h4 class="text-primary">{{ allCount }}</h4>
                <small class="text-muted">Total</small>
              </div>
              <div class="col-md-2">
                <h4 class="text-success">{{ upcomingCount }}</h4>
                <small class="text-muted">Upcoming</small>
              </div>
              <div class="col-md-2">
                <h4 class="text-warning">{{ pendingCount }}</h4>
                <small class="text-muted">Pending</small>
              </div>
              <div class="col-md-2">
                <h4 class="text-info">{{ completedCount }}</h4>
                <small class="text-muted">Completed</small>
              </div>
              <div class="col-md-2">
                <h4 class="text-secondary">{{ pastCount }}</h4>
                <small class="text-muted">Past</small>
              </div>
              <div class="col-md-2">
                <h4 class="text-danger">{{ cancelledCount }}</h4>
                <small class="text-muted">Cancelled</small>
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
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import PatientCalendar from "@/components/calendar/PatientCalendar.vue";
import {
  getDoctorName,
  formatDate,
  formatTime,
  getStatusClass,
  isToday,
  isPast,
  isUpcoming,
} from "@/utils/formatters";

export default {
  name: "PatientCalendarView",
  components: {
    PatientCalendar,
  },

  setup() {
    const store = useStore();
    const router = useRouter();

    const statusFilter = ref("upcoming"); // Default filter
    const viewMode = ref("calendar"); // calendar or list

    // Get appointments from store
    const allAppointments = computed(
      () => store.getters["appointments/allAppointments"]
    );

    // Filtered appointments based on current filter
    const filteredAppointments = computed(() => {
      let filtered = allAppointments.value;

      switch (statusFilter.value) {
        case "upcoming":
          filtered = filtered.filter(
            (apt) =>
              ["pending", "confirmed"].includes(apt.status) &&
              isUpcoming(apt.schedule_details?.date)
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
        case "completed":
          filtered = filtered.filter((apt) => apt.status === "completed");
          break;
        // "all" - no filtering
      }

      // Sort by date and time
      return filtered.sort((a, b) => {
        const dateA = new Date(
          `${a.schedule_details.date}T${a.schedule_details.start_time}`
        );
        const dateB = new Date(
          `${b.schedule_details.date}T${b.schedule_details.start_time}`
        );

        if (statusFilter.value === "upcoming") {
          return dateA - dateB; // Ascending for upcoming
        } else {
          return dateB - dateA; // Descending for past/all
        }
      });
    });

    // Counts for each status
    const allCount = computed(() => allAppointments.value.length);

    const upcomingCount = computed(
      () =>
        allAppointments.value.filter(
          (apt) =>
            ["pending", "confirmed"].includes(apt.status) &&
            isUpcoming(apt.schedule_details?.date)
        ).length
    );

    const pendingCount = computed(
      () =>
        allAppointments.value.filter((apt) => apt.status === "pending").length
    );

    const pastCount = computed(
      () =>
        allAppointments.value.filter(
          (apt) =>
            isPast(apt.schedule_details?.date) || apt.status === "completed"
        ).length
    );

    const cancelledCount = computed(
      () =>
        allAppointments.value.filter((apt) => apt.status === "cancelled").length
    );

    const completedCount = computed(
      () =>
        allAppointments.value.filter((apt) => apt.status === "completed").length
    );

    // Get filter description
    const getFilterDescription = () => {
      const descriptions = {
        all: `Showing all ${allCount.value} appointments`,
        upcoming: `${upcomingCount.value} upcoming appointments`,
        pending: `${pendingCount.value} pending approval`,
        past: `${pastCount.value} past appointments`,
        cancelled: `${cancelledCount.value} cancelled appointments`,
        completed: `${completedCount.value} completed appointments`,
      };
      return descriptions[statusFilter.value] || "";
    };

    // Get row class for table styling
    const getRowClass = (appointment) => {
      if (isToday(appointment.schedule_details?.date)) {
        return "table-warning";
      }
      if (appointment.status === "cancelled") {
        return "table-light text-muted";
      }
      return "";
    };

    // Check if appointment can be cancelled
    const canCancelAppointment = (appointment) => {
      const canCancel = ["pending", "confirmed"].includes(appointment.status);
      const notPast = !isPast(appointment.schedule_details?.date);
      return canCancel && notPast;
    };

    // Actions
    const viewAppointment = (appointmentId) => {
      router.push(`/appointments/${appointmentId}`);
    };

    const cancelAppointment = async (appointmentId) => {
      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      try {
        const result = await store.dispatch(
          "appointments/cancelAppointment",
          appointmentId
        );

        if (result.success) {
          // Appointments will be automatically updated via store
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

    // Load appointments on mount
    const loadAppointments = async () => {
      await store.dispatch("appointments/fetchAppointments");
    };

    onMounted(() => {
      loadAppointments();
    });

    return {
      statusFilter,
      viewMode,
      filteredAppointments,
      allCount,
      upcomingCount,
      pendingCount,
      pastCount,
      cancelledCount,
      completedCount,
      getFilterDescription,
      getRowClass,
      canCancelAppointment,
      viewAppointment,
      cancelAppointment,
      getDoctorName,
      formatDate,
      formatTime,
      getStatusClass,
      isToday,
    };
  },
};
</script>

<style scoped>
.table-warning {
  background-color: rgba(255, 193, 7, 0.1) !important;
}

.table-light {
  background-color: rgba(248, 249, 250, 0.5) !important;
}

.btn-check:checked + .btn-outline-primary {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: #fff;
}

.btn-check:checked + .btn-outline-success {
  background-color: #198754;
  border-color: #198754;
  color: #fff;
}

.btn-check:checked + .btn-outline-warning {
  background-color: #ffc107;
  border-color: #ffc107;
  color: #000;
}

.btn-check:checked + .btn-outline-secondary {
  background-color: #6c757d;
  border-color: #6c757d;
  color: #fff;
}

.btn-check:checked + .btn-outline-danger {
  background-color: #dc3545;
  border-color: #dc3545;
  color: #fff;
}
</style>
