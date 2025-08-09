<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">Register</div>
          <div class="card-body">
            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label for="firstname" class="form-label">First Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="firstname"
                  v-model="user.firstName"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="lastname" class="form-label">Last Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="lastname"
                  v-model="user.lastName"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input
                  type="text"
                  class="form-control"
                  id="username"
                  v-model="user.username"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="user.email"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="user.password"
                  required
                />
                <div class="form-text">
                  Password must be at least 8 characters long.
                </div>
              </div>

              <div class="mb-3">
                <label for="confirmPassword" class="form-label"
                  >Confirm Password</label
                >
                <input
                  type="password"
                  class="form-control"
                  id="confirmPassword"
                  v-model="user.confirmPassword"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">User Type</label>
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="radio"
                    name="userType"
                    id="patientType"
                    value="patient"
                    v-model="user.type"
                    checked
                  />
                  <label class="form-check-label" for="patientType">
                    Patient
                  </label>
                </div>
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="radio"
                    name="userType"
                    id="doctorType"
                    value="doctor"
                    v-model="user.type"
                  />
                  <label class="form-check-label" for="doctorType">
                    Doctor
                  </label>
                </div>
              </div>

              <div class="alert alert-danger" v-if="error">{{ error }}</div>

              <button
                type="submit"
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                <LoadingSpinner v-if="loading" size="sm" class="me-2" />
                Register
              </button>
            </form>

            <div class="mt-3 text-center">
              <p>
                Already have an account?
                <router-link to="/login">Login</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, ref } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";

export default {
  name: "Register",

  setup() {
    const store = useStore();
    const router = useRouter();

    const user = reactive({
      firstName: "",
      lastName: "",
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
      type: "patient",
    });

    const loading = ref(false);
    const error = ref("");

    const handleRegister = async () => {
      // Reset error
      error.value = "";

      // Validation
      if (user.password !== user.confirmPassword) {
        error.value = "Passwords do not match";
        return;
      }

      if (user.password.length < 8) {
        error.value = "Password must be at least 8 characters long";
        return;
      }

      loading.value = true;

      try {
        // Prepare data for API
        const userData = {
          username: user.username,
          password: user.password,
          email: user.email,
          first_name: user.firstName,
          last_name: user.lastName,
          user_type: user.type,
        };

        const result = await store.dispatch("auth/register", userData);

        if (result.error) {
          error.value = result.error;
        } else {
          // Registration successful, redirect to login
          router.push("/login");
        }
      } catch (err) {
        error.value = "An unexpected error occurred";
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    return {
      user,
      loading,
      error,
      handleRegister,
    };
  },
};
</script>
