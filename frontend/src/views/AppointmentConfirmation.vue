<template>
  <div class="container my-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card text-center">
          <div class="card-header bg-success text-white">
            <h4 class="mb-0">Appointment Confirmed</h4>
          </div>
          <div class="card-body py-5">
            <div class="mb-4">
              <i
                class="bi bi-check-circle-fill text-success"
                style="font-size: 4rem"
              ></i>
            </div>
            <h2 class="mb-3">Thank You!</h2>
            <p class="lead mb-4">
              Your appointment has been successfully booked.
            </p>
            <p>You will receive a confirmation email shortly.</p>

            <div class="mt-4">
              <router-link to="/dashboard" class="btn btn-primary me-3">
                Go to Dashboard
              </router-link>
              <router-link
                to="/patient-calendar"
                class="btn btn-outline-secondary"
              >
                View My Calendar
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AppointmentConfirmation",
};
</script>
