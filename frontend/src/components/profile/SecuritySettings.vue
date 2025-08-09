<template>
  <div>
    <h5>Two-Factor Authentication</h5>
    <div
      class="d-flex justify-content-between align-items-center mb-4 p-3 border rounded"
    >
      <div>
        <div class="d-flex align-items-center mb-2">
          <i
            :class="
              is2FAEnabled
                ? 'bi bi-shield-check text-success'
                : 'bi bi-shield-exclamation text-warning'
            "
            class="me-2 fs-5"
          ></i>
          <strong>
            {{
              is2FAEnabled
                ? "Two-factor authentication is enabled"
                : "Two-factor authentication is disabled"
            }}
          </strong>
        </div>
        <small class="text-muted">
          {{
            is2FAEnabled
              ? "Your account has enhanced security protection."
              : "Enable 2FA to add an extra layer of security to your account."
          }}
        </small>
      </div>
      <router-link
        to="/security/2fa"
        class="btn"
        :class="is2FAEnabled ? 'btn-outline-primary' : 'btn-warning'"
      >
        <i class="bi bi-gear me-2"></i>
        {{ is2FAEnabled ? "Manage 2FA" : "Enable 2FA" }}
      </router-link>
    </div>

    <hr />

    <h5>Change Password</h5>
    <p class="text-muted mb-3">
      Choose a strong password to keep your account secure.
    </p>

    <form @submit.prevent="changePassword">
      <div class="mb-3">
        <label for="currentPassword" class="form-label">Current Password</label>
        <input
          type="password"
          class="form-control"
          id="currentPassword"
          v-model="passwordForm.currentPassword"
          required
          autocomplete="current-password"
        />
      </div>

      <div class="mb-3">
        <label for="newPassword" class="form-label">New Password</label>
        <input
          type="password"
          class="form-control"
          id="newPassword"
          v-model="passwordForm.newPassword"
          required
          minlength="8"
          autocomplete="new-password"
        />
        <div class="form-text">
          Password must be at least 8 characters long and contain a mix of
          letters, numbers, and special characters.
        </div>
      </div>

      <div class="mb-3">
        <label for="confirmPassword" class="form-label"
          >Confirm New Password</label
        >
        <input
          type="password"
          class="form-control"
          id="confirmPassword"
          v-model="passwordForm.confirmPassword"
          required
          autocomplete="new-password"
          :class="{
            'is-invalid':
              passwordForm.newPassword &&
              passwordForm.confirmPassword &&
              passwordForm.newPassword !== passwordForm.confirmPassword,
          }"
        />
        <div
          v-if="
            passwordForm.newPassword &&
            passwordForm.confirmPassword &&
            passwordForm.newPassword !== passwordForm.confirmPassword
          "
          class="invalid-feedback"
        >
          Passwords do not match
        </div>
      </div>

      <div v-if="passwordError" class="alert alert-danger mb-3">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ passwordError }}
      </div>

      <div v-if="passwordChanged" class="alert alert-success mb-3">
        <i class="bi bi-check-circle me-2"></i>
        Password changed successfully!
      </div>

      <div class="text-end">
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="savingPassword || !isPasswordFormValid"
        >
          <LoadingSpinner v-if="savingPassword" size="sm" class="me-2" />
          <i class="bi bi-key me-2" v-else></i>
          Change Password
        </button>
      </div>
    </form>

    <hr class="my-4" />

    <h5>Account Security</h5>
    <div class="row">
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <h6 class="card-title">
              <i class="bi bi-clock-history me-2"></i>
              Last Login
            </h6>
            <p class="card-text text-muted">
              {{ formatLastLogin() }}
            </p>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <h6 class="card-title">
              <i class="bi bi-shield-check me-2"></i>
              Account Status
            </h6>
            <p class="card-text">
              <span class="badge bg-success">Active & Secure</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from "vue";
import { useStore } from "vuex";
import AuthService from "@/services/auth.service";
import UserService from "@/services/user.service";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";

export default {
  name: "ProfileSecuritySettings",
  components: { LoadingSpinner },
  setup() {
    const store = useStore();
    const currentUser = computed(() => store.getters["auth/currentUser"]);

    const is2FAEnabled = ref(false);
    const profileData = ref({});
    const loading2FAStatus = ref(true);

    const passwordForm = reactive({
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    });
    const savingPassword = ref(false);
    const passwordChanged = ref(false);
    const passwordError = ref("");

    const isPasswordFormValid = computed(() => {
      return (
        passwordForm.currentPassword &&
        passwordForm.newPassword &&
        passwordForm.confirmPassword &&
        passwordForm.newPassword === passwordForm.confirmPassword &&
        passwordForm.newPassword.length >= 8
      );
    });

    const loadProfileData = async () => {
      try {
        const response = await UserService.getUserProfile();
        profileData.value = response.data;
      } catch (error) {
        console.error("Failed to load user profile:", error);
      }
    };

    const load2FAStatus = async () => {
      try {
        const response = await AuthService.get2FAStatus();
        is2FAEnabled.value = response.data.two_fa_enabled;
      } catch (error) {
        console.error("Failed to load 2FA status", error);
        is2FAEnabled.value = currentUser.value?.two_fa_enabled || false;
      } finally {
        loading2FAStatus.value = false;
      }
    };

    const formatLastLogin = () => {
      if (profileData.value.last_login) {
        const lastLogin = new Date(profileData.value.last_login);
        return lastLogin.toLocaleString("en-US", {
          year: "numeric",
          month: "long",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        });
      }
      return "Never";
    };

    const changePassword = async () => {
      passwordError.value = "";
      passwordChanged.value = false;

      if (passwordForm.newPassword !== passwordForm.confirmPassword) {
        passwordError.value = "Passwords do not match";
        return;
      }

      if (passwordForm.newPassword.length < 8) {
        passwordError.value = "Password must be at least 8 characters long";
        return;
      }

      savingPassword.value = true;

      try {
        await UserService.changePassword({
          current_password: passwordForm.currentPassword,
          new_password: passwordForm.newPassword,
        });

        passwordChanged.value = true;
        passwordForm.currentPassword = "";
        passwordForm.newPassword = "";
        passwordForm.confirmPassword = "";

        setTimeout(() => {
          passwordChanged.value = false;
        }, 3000);
      } catch (error) {
        console.error("Failed to change password:", error);
        const errorData = error.response?.data;
        if (Array.isArray(errorData?.error)) {
          passwordError.value = errorData.error.join(". ");
        } else {
          passwordError.value =
            errorData?.error || "Failed to change password. Please try again.";
        }
      } finally {
        savingPassword.value = false;
      }
    };

    onMounted(() => {
      loadProfileData();
      load2FAStatus();
    });

    return {
      is2FAEnabled,
      profileData,
      passwordForm,
      savingPassword,
      passwordChanged,
      passwordError,
      isPasswordFormValid,
      formatLastLogin,
      changePassword,
    };
  },
};
</script>
