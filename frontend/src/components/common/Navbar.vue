<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container">
      <router-link class="navbar-brand" to="/">
        Medical Appointments
      </router-link>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item" v-if="isAuthenticated">
            <router-link class="nav-link" to="/dashboard">
              Dashboard
            </router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated && isDoctor">
            <router-link class="nav-link" to="/doctor-schedule">
              My Schedule
            </router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated && isPatient">
            <router-link class="nav-link" to="/appointments">
              My Appointments
            </router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated && isPatient">
            <router-link class="nav-link" to="/book-appointment">
              Book Appointment
            </router-link>
          </li>
        </ul>

        <ul class="navbar-nav ms-auto">
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="nav-link" to="/login">Login</router-link>
          </li>
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="nav-link" to="/register">Register</router-link>
          </li>
          <li class="nav-item dropdown" v-if="isAuthenticated">
            <a
              class="nav-link dropdown-toggle"
              href="#"
              id="userDropdown"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              {{ currentUser ? currentUser.email : "User" }}
            </a>
            <ul
              class="dropdown-menu dropdown-menu-end"
              aria-labelledby="userDropdown"
            >
              <li>
                <router-link class="dropdown-item" to="/profile">
                  Profile
                </router-link>
              </li>
              <li>
                <hr class="dropdown-divider" />
              </li>
              <li>
                <a class="dropdown-item" href="#" @click.prevent="logout">
                  Logout
                </a>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";

export default {
  name: "Navbar",

  setup() {
    const store = useStore();
    const router = useRouter();

    const isAuthenticated = computed(
      () => store.getters["auth/isAuthenticated"]
    );
    const currentUser = computed(() => store.getters["auth/currentUser"]);

    const isDoctor = computed(() => currentUser.value?.role === "doctor");
    const isPatient = computed(() => currentUser.value?.role === "patient");

    const logout = () => {
      store.dispatch("auth/logout");
      router.push("/login");
    };

    return {
      isAuthenticated,
      currentUser,
      isDoctor,
      isPatient,
      logout,
    };
  },
};
</script>
