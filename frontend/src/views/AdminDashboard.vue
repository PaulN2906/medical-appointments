<template>
  <div class="container my-4">
    <h1 class="mb-4">Admin Dashboard</h1>

    <div class="alert alert-success">
      <i class="bi bi-check-circle me-2"></i>
      Admin dashboard is working! You can see this because you're logged in as
      admin.
    </div>

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">Quick Test - All Appointments</div>
          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="appointments.length === 0" class="text-center p-4">
              <p>No appointments found in the system.</p>
            </div>

            <div v-else>
              <p class="mb-3">
                <strong
                  >Total appointments visible to admin:
                  {{ appointments.length }}</strong
                >
              </p>

              <div class="table-responsive">
                <table class="table table-sm">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Patient</th>
                      <th>Doctor</th>
                      <th>Date</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="appointment in appointments.slice(0, 10)"
                      :key="appointment.id"
                    >
                      <td>{{ appointment.id }}</td>
                      <td>{{ getPatientName(appointment) }}</td>
                      <td>{{ getDoctorName(appointment) }}</td>
                      <td>{{ appointment.schedule_details?.date }}</td>
                      <td>
                        <span :class="getStatusClass(appointment.status)">
                          {{ appointment.status }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <small class="text-muted">
                Showing first 10 appointments. This proves admin can see all
                appointments from all doctors/patients.
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import AppointmentService from "@/services/appointment.service";

export default {
  name: "AdminDashboard",

  setup() {
    const loading = ref(true);
    const appointments = ref([]);

    const loadAppointments = async () => {
      try {
        const response = await AppointmentService.getAppointments();
        appointments.value = response.data;
        console.log(`Admin can see ${response.data.length} total appointments`);
      } catch (error) {
        console.error("Failed to load appointments", error);
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
      loadAppointments();
    });

    return {
      loading,
      appointments,
      getPatientName,
      getDoctorName,
      getStatusClass,
    };
  },
};
</script>
