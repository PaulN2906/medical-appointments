<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">Login</div>
          <div class="card-body">
            <!-- Formular pentru autentificare standard -->
            <form @submit.prevent="handleLogin" v-if="!requires2FA">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input
                  type="text"
                  class="form-control"
                  id="username"
                  v-model="credentials.username"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="credentials.password"
                  required
                />
              </div>

              <div class="alert alert-danger" v-if="error">
                {{ error }}
              </div>

              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span
                  v-if="loading"
                  class="spinner-border spinner-border-sm"
                  role="status"
                ></span>
                Login
              </button>
            </form>

            <!-- Formular pentru 2FA -->
            <form @submit.prevent="handle2FA" v-if="requires2FA">
              <div class="mb-3">
                <label for="twoFactorCode" class="form-label"
                  >2FA Verification Code</label
                >
                <input
                  type="text"
                  class="form-control"
                  id="twoFactorCode"
                  v-model="twoFactorCode"
                  required
                />
                <small class="form-text text-muted"
                  >Enter the code from your authenticator app</small
                >
              </div>

              <div class="alert alert-danger" v-if="error2FA">
                {{ error2FA }}
              </div>

              <button
                type="submit"
                class="btn btn-primary"
                :disabled="loading2FA"
              >
                <span
                  v-if="loading2FA"
                  class="spinner-border spinner-border-sm"
                  role="status"
                ></span>
                Verify
              </button>
            </form>

            <div class="mt-3">
              <p>
                Don't have an account?
                <router-link to="/register">Register</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";

export default {
  name: "Login",

  setup() {
    const store = useStore();
    const router = useRouter();

    const credentials = ref({
      username: "",
      password: "",
    });

    const twoFactorCode = ref("");
    const error = ref("");
    const error2FA = ref("");
    const loading = ref(false);
    const loading2FA = ref(false);

    const requires2FA = computed(() => store.getters["auth/requires2FA"]);

    const handleLogin = async () => {
      loading.value = true;
      error.value = "";

      try {
        const result = await store.dispatch("auth/login", credentials.value);

        if (result.error) {
          error.value = result.error;
        } else if (!result.requires2FA) {
          router.push("/dashboard");
        }
      } catch (err) {
        error.value = "An unexpected error occurred";
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const handle2FA = async () => {
      loading2FA.value = true;
      error2FA.value = "";

      try {
        const result = await store.dispatch(
          "auth/verify2FA",
          twoFactorCode.value
        );

        if (result.error) {
          error2FA.value = result.error;
        } else {
          router.push("/dashboard");
        }
      } catch (err) {
        error2FA.value = "An unexpected error occurred during 2FA verification";
        console.error(err);
      } finally {
        loading2FA.value = false;
      }
    };

    return {
      credentials,
      twoFactorCode,
      error,
      error2FA,
      loading,
      loading2FA,
      requires2FA,
      handleLogin,
      handle2FA,
    };
  },
};
</script>
