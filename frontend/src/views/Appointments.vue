<template>
  <div class="container my-4">
    <h1 class="mb-4">My Appointments</h1>

    <!-- Filter Tabs -->
    <div class="row mb-4">
      <div class="col-md-12">
        <ul class="nav nav-tabs">
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: activeFilter === 'upcoming' }"
              href="#"
              @click.prevent="setFilter('upcoming')"
            >
              Upcoming
              <span class="badge bg-primary ms-1">{{ upcomingCount }}</span>
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: activeFilter === 'past' }"
              href="#"
              @click.prevent="setFilter('past')"
            >
              Past <span class="badge bg-secondary ms-1">{{ pastCount }}</span>
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: activeFilter === 'cancelled' }"
              href="#"
              @click.prevent="setFilter('cancelled')"
            >
              Cancelled
              <span class="badge bg-danger ms-1">{{ cancelledCount }}</span>
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: activeFilter === 'all' }"
              href="#"
              @click.prevent="setFilter('all')"
            >
              All <span class="badge bg-info ms-1">{{ allCount }}</span>
            </a>
          </li>
        </ul>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div
            class="card-header d-flex justify-content-between align-items-center"
          >
            <div>
              {{ getFilterTitle() }}
              <small class="text-muted ms-2"
                >({{ filteredAppointments.length }} appointments)</small
              >
            </div>
            <router-link
              v-if="isPatient"
              to="/book-appointment"
              class="btn btn-primary"
            >
              <i class="bi bi-plus"></i> New Appointment
            </router-link>
          </div>

          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <LoadingSpinner />
            </div>

            <div
              v-else-if="filteredAppointments.length === 0"
              class="text-center p-5"
            >
              <div class="mb-3">
                <i class="bi bi-calendar-x fs-1 text-muted"></i>
              </div>
              <p class="mb-4">
                You don't have any {{ activeFilter }} appointments.
              </p>
              <router-link
                v-if="isPatient && activeFilter === 'upcoming'"
                to="/book-appointment"
                class="btn btn-primary"
              >
                Book Your First Appointment
              </router-link>
            </div>

            <div v-else>
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>{{ isDoctor ? "Patient" : "Doctor" }}</th>
                      <th>Date</th>
                      <th>Time</th>
                      <th>Status</th>
                      <th v-if="activeFilter === 'upcoming'">Days Until</th>
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
                        {{
                          isDoctor
                            ? getPatientName(appointment)
                            : getDoctorName(appointment)
                        }}
                      </td>
                      <td>
                        {{ formatDate(appointment.schedule_details.date) }}
                        <span
                          v-if="isToday(appointment.schedule_details.date)"
                          class="badge bg-primary ms-2"
                          >Today</span
                        >
                        <span
                          v-else-if="isPast(appointment.schedule_details.date)"
                          class="badge bg-secondary ms-2"
                          >Past</span
                        >
                      </td>
                      <td>
                        {{
                          formatTime(appointment.schedule_details.start_time)
                        }}
                      </td>
                      <td>
                        <span :class="getStatusClass(appointment.status)">
                          {{ appointment.status }}
                        </span>
                      </td>
                      <td v-if="activeFilter === 'upcoming'">
                        <small class="text-muted">
                          {{ getDaysUntil(appointment.schedule_details.date) }}
                        </small>
                      </td>
                      <td>
                        <button
                          @click="viewAppointment(appointment.id)"
                          class="btn btn-sm btn-info me-2"
                        >
                          View
                        </button>
                        <button
                          v-if="isDoctor && appointment.status === 'pending'"
                          @click="confirmAppointment(appointment.id)"
                          class="btn btn-sm btn-success me-2"
                        >
                          Confirm
                        </button>
                        <button
                          v-if="
                            (appointment.status === 'pending' ||
                              appointment.status === 'confirmed') &&
                            !isPast(appointment.schedule_details.date)
                          "
                          @click="cancelAppointment(appointment.id)"
                          class="btn btn-sm btn-danger"
                        >
                          Cancel
                        </button>
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
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";
import {
  isToday,
  isPast,
  isUpcoming,
  getDaysUntil,
  getDoctorName,
  getPatientName,
  formatDate,
  formatTime,
  getStatusClass,
} from "@/utils/formatters";

export default {
  name: "Appointments",

  setup() {
    const route = useRoute();
    const router = useRouter();
    const store = useStore();

    const loading = computed(() => store.getters["appointments/isLoading"]);
    const appointments = computed(
      () => store.getters["appointments/allAppointments"]
    );
    const activeFilter = ref("upcoming"); // Default to upcoming

    // Get current user and role
    const currentUser = computed(() => store.getters["auth/currentUser"]);
    const isDoctor = computed(() => currentUser.value?.role === "doctor");
    const isPatient = computed(() => currentUser.value?.role === "patient");

    // Computed properties for counts
    const upcomingCount = computed(() => {
      return appointments.value.filter(
        (apt) =>
          ["pending", "confirmed"].includes(apt.status) &&
          isUpcoming(apt.schedule_details?.date)
      ).length;
    });

    const pastCount = computed(() => {
      return appointments.value.filter(
        (apt) =>
          isPast(apt.schedule_details?.date) || apt.status === "completed"
      ).length;
    });

    const cancelledCount = computed(() => {
      return appointments.value.filter((apt) => apt.status === "cancelled")
        .length;
    });

    const allCount = computed(() => appointments.value.length);

    // Filter appointments based on active filter
    const filteredAppointments = computed(() => {
      let filtered = [];

      switch (activeFilter.value) {
        case "upcoming":
          filtered = appointments.value.filter(
            (apt) =>
              ["pending", "confirmed"].includes(apt.status) &&
              isUpcoming(apt.schedule_details?.date)
          );
          break;
        case "pending":
          filtered = appointments.value.filter(
            (apt) => apt.status === "pending"
          );
          break;
        case "past":
          filtered = appointments.value.filter(
            (apt) =>
              isPast(apt.schedule_details?.date) || apt.status === "completed"
          );
          break;
        case "cancelled":
          filtered = appointments.value.filter(
            (apt) => apt.status === "cancelled"
          );
          break;
        default:
          filtered = appointments.value;
      }

      // Sort appointments
      return filtered.sort((a, b) => {
        if (["upcoming", "pending"].includes(activeFilter.value)) {
          // For upcoming: sort by date, then time (earliest first)
          const dateComparison = a.schedule_details.date.localeCompare(
            b.schedule_details.date
          );
          if (dateComparison !== 0) return dateComparison;
          return a.schedule_details.start_time.localeCompare(
            b.schedule_details.start_time
          );
        } else {
          // For past/cancelled/all: sort by date descending (most recent first)
          const dateComparison = b.schedule_details.date.localeCompare(
            a.schedule_details.date
          );
          if (dateComparison !== 0) return dateComparison;
          return b.schedule_details.start_time.localeCompare(
            a.schedule_details.start_time
          );
        }
      });
    });

    // Set filter and update URL
    const setFilter = (filter) => {
      activeFilter.value = filter;
      // Update URL query parameter
      router.push({
        query: { filter: filter !== "upcoming" ? filter : undefined },
      });
    };

    // Get filter title
    const getFilterTitle = () => {
      const titles = {
        upcoming: "Upcoming Appointments",
        pending: "Pending Appointments",
        past: "Past Appointments",
        cancelled: "Cancelled Appointments",
        all: "All Appointments",
      };
      return titles[activeFilter.value] || "Appointments";
    };

    // Get row class for styling
    const getRowClass = (appointment) => {
      if (isToday(appointment.schedule_details?.date)) {
        return "table-warning";
      }
      if (appointment.status === "cancelled") {
        return "table-light text-muted";
      }
      if (isPast(appointment.schedule_details?.date)) {
        return "table-light";
      }
      return "";
    };

    // Load appointments
    const loadAppointments = async () => {
      await store.dispatch("appointments/fetchAppointments");
    };

    // Navigate to appointment details
    const viewAppointment = (id) => {
      router.push(`/appointments/${id}`);
    };

    // Confirm appointment (for doctors)
    const confirmAppointment = async (id) => {
      const { success, error } = await store.dispatch(
        "appointments/confirmAppointment",
        id
      );
      if (!success) {
        console.error("Failed to confirm appointment", error);
        alert(error || "Failed to confirm appointment");
      }
    };

    // Cancel appointment
    const cancelAppointment = async (id) => {
      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      const { success, error } = await store.dispatch(
        "appointments/cancelAppointment",
        id
      );
      if (!success) {
        console.error("Failed to cancel appointment", error);
        alert(error || "Failed to cancel appointment");
      }
    };

    onMounted(() => {
      // Check for filter in query params
      const queryFilter = route.query.filter;
      if (
        ["upcoming", "pending", "past", "cancelled", "all"].includes(
          queryFilter
        )
      ) {
        activeFilter.value = queryFilter;
      }

      loadAppointments();
    });

    return {
      loading,
      appointments,
      activeFilter,
      filteredAppointments,
      currentUser,
      isDoctor,
      isPatient,
      upcomingCount,
      pastCount,
      cancelledCount,
      allCount,
      isToday,
      isPast,
      getDaysUntil,
      setFilter,
      getFilterTitle,
      getRowClass,
      viewAppointment,
      confirmAppointment,
      cancelAppointment,
      getDoctorName,
      getPatientName,
      formatDate,
      formatTime,
      getStatusClass,
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
</style>
