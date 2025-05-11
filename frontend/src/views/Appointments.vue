<template>
  <div class="container my-4">
    <h1 class="mb-4">My Appointments</h1>

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div
            class="card-header d-flex justify-content-between align-items-center"
          >
            <div>Your Appointments</div>
            <router-link to="/book-appointment" class="btn btn-primary">
              <i class="bi bi-plus"></i> New Appointment
            </router-link>
          </div>

          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="appointments.length === 0" class="text-center p-5">
              <p class="mb-4">You don't have any appointments yet.</p>
              <router-link to="/book-appointment" class="btn btn-primary">
                Book Your First Appointment
              </router-link>
            </div>

            <div v-else>
              <div class="table-responsive">
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
                      v-for="appointment in appointments"
                      :key="appointment.id"
                    >
                      <td>Dr. Example</td>
                      <td>May 10, 2025</td>
                      <td>10:00 AM</td>
                      <td>
                        <span class="badge bg-success">Confirmed</span>
                      </td>
                      <td>
                        <button class="btn btn-sm btn-info me-2">View</button>
                        <button class="btn btn-sm btn-danger">Cancel</button>
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
export default {
  name: "Appointments",
  data() {
    return {
      loading: false,
      appointments: [],
    };
  },
  mounted() {
    // In a real implementation, you'd load appointments from API
    this.appointments = []; // Empty for demo
  },
};
</script>
