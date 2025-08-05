<template>
  <div>
    <div class="row mb-4">
      <!-- Stats Cards -->
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <h3 class="text-primary">{{ stats.total_appointments || 0 }}</h3>
            <p class="mb-0">Total Appointments</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <h3 class="text-success">{{ stats.appointments_today || 0 }}</h3>
            <p class="mb-0">Today's Appointments</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <h3 class="text-info">{{ stats.total_doctors || 0 }}</h3>
            <p class="mb-0">Total Doctors</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <h3 class="text-warning">{{ stats.total_patients || 0 }}</h3>
            <p class="mb-0">Total Patients</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Status Breakdown -->
    <div class="row mb-4" v-if="stats.appointments_by_status">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Appointments by Status</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div
                class="col-md-3 text-center mb-2"
                v-for="(count, status) in stats.appointments_by_status"
                :key="status"
              >
                <span :class="getStatusClass(status)" class="fs-5 px-3 py-2">
                  {{ status }}: {{ count }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Appointments -->
    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Recent Appointments</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div
              v-else-if="stats.recent_appointments?.length === 0"
              class="text-center p-4"
            >
              <p>No recent appointments found.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="appointment in stats.recent_appointments"
                    :key="appointment.id"
                  >
                    <td>{{ appointment.id }}</td>
                    <td>{{ getPatientName(appointment) }}</td>
                    <td>{{ getDoctorName(appointment) }}</td>
                    <td>{{ appointment.schedule_details?.date }}</td>
                    <td>
                      {{ formatTime(appointment.schedule_details?.start_time) }}
                    </td>
                    <td>
                      <span :class="getStatusClass(appointment.status)">
                        {{ appointment.status }}
                      </span>
                    </td>
                    <td>{{ formatDateTime(appointment.created_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import AdminService from "@/services/admin.service";

export default {
  name: "AdminOverview",

  setup() {
    const loading = ref(true);
    const stats = ref({});

    const loadStats = async () => {
      try {
        const response = await AdminService.getDashboardStats();
        stats.value = response.data;
        console.log("Admin stats loaded:", response.data);
      } catch (error) {
        console.error("Failed to load admin stats", error);
      } finally {
        loading.value = false;
      }
    };

    const getPatientName = (appointment) => {
      if (appointment.patient_details?.user) {
        const user = appointment.patient_details.user;
        return `${user.first_name} ${user.last_name}`;
      }
      return "Unknown Patient";
    };

    const getDoctorName = (appointment) => {
      if (appointment.doctor_details?.user) {
        const user = appointment.doctor_details.user;
        return `Dr. ${user.last_name} ${user.first_name}`;
      }
      return "Unknown Doctor";
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

    const formatDateTime = (dateTimeString) => {
      if (!dateTimeString) return "";
      const options = {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      };
      return new Date(dateTimeString).toLocaleString(undefined, options);
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
      loadStats();
    });

    return {
      loading,
      stats,
      getPatientName,
      getDoctorName,
      formatTime,
      formatDateTime,
      getStatusClass,
    };
  },
};
</script>
