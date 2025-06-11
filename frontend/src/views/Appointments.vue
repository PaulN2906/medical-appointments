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
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
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
import AppointmentService from "@/services/appointment.service";

export default {
  name: "Appointments",

  setup() {
    const route = useRoute();
    const router = useRouter();
    const store = useStore();

    const loading = ref(true);
    const appointments = ref([]);
    const activeFilter = ref("upcoming"); // Default to upcoming

    // Get current user and role
    const currentUser = computed(() => store.getters["auth/currentUser"]);
    const isDoctor = computed(() => currentUser.value?.role === "doctor");
    const isPatient = computed(() => currentUser.value?.role === "patient");

    // Helper functions for date comparison
    const isToday = (dateString) => {
      const appointmentDate = new Date(dateString + "T00:00:00");
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      appointmentDate.setHours(0, 0, 0, 0);

      return appointmentDate.getTime() === today.getTime();
    };

    const isPast = (dateString) => {
      const appointmentDate = new Date(dateString + "T00:00:00");
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      appointmentDate.setHours(0, 0, 0, 0);

      return appointmentDate < today;
    };

    const isUpcoming = (dateString) => {
      const appointmentDate = new Date(dateString + "T00:00:00");
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      appointmentDate.setHours(0, 0, 0, 0);

      return appointmentDate >= today;
    };

    // Helper function to get days until appointment
    const getDaysUntil = (dateString) => {
      const appointmentDate = new Date(dateString + "T00:00:00");
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      appointmentDate.setHours(0, 0, 0, 0);

      const diffTime = appointmentDate - today;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      if (diffDays === 0) return "Today";
      if (diffDays === 1) return "Tomorrow";
      if (diffDays > 0) return `In ${diffDays} days`;
      return `${Math.abs(diffDays)} days ago`;
    };

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
        if (activeFilter.value === "upcoming") {
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
      try {
        const response = await AppointmentService.getAppointments();
        appointments.value = response.data;
      } catch (error) {
        console.error("Failed to load appointments", error);
      } finally {
        loading.value = false;
      }
    };

    // Navigate to appointment details
    const viewAppointment = (id) => {
      router.push(`/appointments/${id}`);
    };

    // Confirm appointment (for doctors)
    const confirmAppointment = async (id) => {
      try {
        await AppointmentService.confirmAppointment(id);
        // Reload appointments
        await loadAppointments();
      } catch (error) {
        console.error("Failed to confirm appointment", error);
        alert("Failed to confirm appointment");
      }
    };

    // Cancel appointment
    const cancelAppointment = async (id) => {
      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      try {
        await AppointmentService.cancelAppointment(id);
        // Reload appointments
        await loadAppointments();
      } catch (error) {
        console.error("Failed to cancel appointment", error);
        alert("Failed to cancel appointment");
      }
    };

    // Format helpers
    const getDoctorName = (appointment) => {
      if (appointment.doctor_details?.user) {
        const user = appointment.doctor_details.user;
        return `Dr. ${user.first_name} ${user.last_name}`;
      }
      return "Unknown Doctor";
    };

    const getPatientName = (appointment) => {
      if (appointment.patient_details?.user) {
        const user = appointment.patient_details.user;
        return `${user.first_name} ${user.last_name}`;
      }
      return "Unknown Patient";
    };

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

    const getStatusClass = (status) => {
      const statusClasses = {
        pending: "badge bg-warning",
        confirmed: "badge bg-success",
        cancelled: "badge bg-danger",
        completed: "badge bg-info",
      };
      return statusClasses[status] || "badge bg-secondary";
    };

    onMounted(() => {
      // Check for filter in query params
      const queryFilter = route.query.filter;
      if (["upcoming", "past", "cancelled", "all"].includes(queryFilter)) {
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
