<template>
  <div>
    <section class="hero-section">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h1 class="display-4 mb-4">Book Medical Appointments Online</h1>
            <p class="lead mb-4">
              Schedule your medical appointments easily and securely. Connect
              with doctors and manage your healthcare needs from anywhere.
            </p>
            <div class="d-flex">
              <router-link
                v-if="!isAuthenticated"
                to="/register"
                class="btn btn-primary btn-lg me-3"
              >
                Get Started
              </router-link>
              <router-link
                v-else
                to="/dashboard"
                class="btn btn-primary btn-lg me-3"
              >
                Dashboard
              </router-link>
              <router-link
                v-if="!isAuthenticated"
                to="/login"
                class="btn btn-outline-secondary btn-lg"
              >
                Sign In
              </router-link>
              <router-link
                v-else
                to="/book-appointment"
                class="btn btn-outline-secondary btn-lg"
              >
                Book Appointment
              </router-link>
            </div>
          </div>
          <div class="col-md-6">
            <img
              src="@/assets/doctor-patient.svg"
              alt="Doctor and Patient"
              class="img-fluid"
            />
          </div>
        </div>
      </div>
    </section>

    <section class="features-section py-5 bg-light">
      <div class="container">
        <h2 class="text-center mb-5">How It Works</h2>
        <div class="row">
          <div class="col-md-4 mb-4">
            <div class="card h-100">
              <div class="card-body text-center">
                <div class="feature-icon mb-3">
                  <i class="bi bi-search fs-1"></i>
                </div>
                <h3 class="card-title">Find a Doctor</h3>
                <p class="card-text">
                  Browse through our list of qualified doctors and specialists.
                </p>
              </div>
            </div>
          </div>
          <div class="col-md-4 mb-4">
            <div class="card h-100">
              <div class="card-body text-center">
                <div class="feature-icon mb-3">
                  <i class="bi bi-calendar-check fs-1"></i>
                </div>
                <h3 class="card-title">Book Appointment</h3>
                <p class="card-text">
                  Select available time slots and book your appointment
                  instantly.
                </p>
              </div>
            </div>
          </div>
          <div class="col-md-4 mb-4">
            <div class="card h-100">
              <div class="card-body text-center">
                <div class="feature-icon mb-3">
                  <i class="bi bi-bell fs-1"></i>
                </div>
                <h3 class="card-title">Get Reminders</h3>
                <p class="card-text">
                  Receive email notifications and reminders for your
                  appointments.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="benefits-section py-5">
      <div class="container">
        <h2 class="text-center mb-5">Benefits</h2>
        <div class="row">
          <div class="col-lg-6 mb-4">
            <div class="d-flex">
              <div class="flex-shrink-0">
                <i class="bi bi-shield-check fs-2 text-primary"></i>
              </div>
              <div class="ms-3">
                <h4>Secure Authentication</h4>
                <p>
                  Our platform uses two-factor authentication to ensure your
                  account is secure.
                </p>
              </div>
            </div>
          </div>
          <div class="col-lg-6 mb-4">
            <div class="d-flex">
              <div class="flex-shrink-0">
                <i class="bi bi-clock-history fs-2 text-primary"></i>
              </div>
              <div class="ms-3">
                <h4>Real-time Availability</h4>
                <p>
                  See doctors' availability in real-time and book instantly.
                </p>
              </div>
            </div>
          </div>
          <div class="col-lg-6 mb-4">
            <div class="d-flex">
              <div class="flex-shrink-0">
                <i class="bi bi-phone fs-2 text-primary"></i>
              </div>
              <div class="ms-3">
                <h4>Accessible Anywhere</h4>
                <p>
                  Access your appointments and medical schedule from any device.
                </p>
              </div>
            </div>
          </div>
          <div class="col-lg-6 mb-4">
            <div class="d-flex">
              <div class="flex-shrink-0">
                <i class="bi bi-bell fs-2 text-primary"></i>
              </div>
              <div class="ms-3">
                <h4>Email Notifications</h4>
                <p>
                  Receive timely notifications about your appointments and
                  updates.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="cta-section py-5 bg-primary text-white">
      <div class="container text-center">
        <h2 class="mb-4">Ready to take control of your healthcare?</h2>
        <p class="lead mb-4">
          Join thousands of users who manage their medical appointments online.
        </p>
        <router-link
          v-if="!isAuthenticated"
          to="/register"
          class="btn btn-light btn-lg"
        >
          Sign Up Now
        </router-link>
        <router-link v-else to="/book-appointment" class="btn btn-light btn-lg">
          Book Appointment
        </router-link>
      </div>
    </section>
  </div>
</template>

<script>
import { computed } from "vue";
import { useStore } from "vuex";

export default {
  name: "Home",

  setup() {
    const store = useStore();

    const isAuthenticated = computed(
      () => store.getters["auth/isAuthenticated"]
    );

    return {
      isAuthenticated,
    };
  },
};
</script>

<style scoped>
.hero-section {
  padding: 80px 0;
  background-color: #f8f9fa;
}

.feature-icon {
  color: #0d6efd;
}

.cta-section {
  padding: 60px 0;
}
</style>
