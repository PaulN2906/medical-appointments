<template>
  <div class="container my-4">
    <h1 class="mb-4">Two-Factor Authentication</h1>

    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">2FA Settings</div>
          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <LoadingSpinner />
            </div>

            <div v-else>
              <div v-if="!is2FAEnabled" class="mb-4">
                <h5>Enable Two-Factor Authentication</h5>
                <p>
                  Two-factor authentication adds an extra layer of security to
                  your account by requiring more than just a password to sign
                  in.
                </p>

                <div class="alert alert-info">
                  <i class="bi bi-info-circle"></i>
                  <strong>Benefits of 2FA:</strong>
                  <ul class="mb-0 mt-2">
                    <li>
                      Protects your account even if your password is compromised
                    </li>
                    <li>
                      Prevents unauthorized access to your medical information
                    </li>
                    <li>Required for accessing sensitive medical features</li>
                  </ul>
                </div>

                <button
                  @click="enable2FA"
                  class="btn btn-primary"
                  :disabled="enabling"
                >
                  <LoadingSpinner v-if="enabling" size="sm" class="me-2" />
                  Enable 2FA
                </button>
              </div>

              <div v-else class="mb-4">
                <div class="alert alert-success">
                  <i class="bi bi-shield-check"></i> Two-factor authentication
                  is enabled for your account.
                </div>

                <div class="d-flex gap-2">
                  <button
                    @click="disable2FA"
                    class="btn btn-danger"
                    :disabled="disabling"
                  >
                    <LoadingSpinner v-if="disabling" size="sm" class="me-2" />
                    Disable 2FA
                  </button>

                  <button
                    @click="regenerate2FA"
                    class="btn btn-warning"
                    :disabled="regenerating"
                  >
                    <LoadingSpinner
                      v-if="regenerating"
                      size="sm"
                      class="me-2"
                    />
                    Regenerate Backup Codes
                  </button>
                </div>
              </div>

              <div v-if="showSetup" class="mt-4">
                <h5>Setup Instructions</h5>
                <hr />

                <div class="row">
                  <div class="col-md-6">
                    <ol class="setup-steps">
                      <li>
                        <p>
                          <strong>Download an authenticator app:</strong>
                        </p>
                        <div class="d-flex flex-wrap gap-3 mb-3">
                          <div class="text-center">
                            <div
                              class="auth-app-icon bg-primary text-white rounded-circle d-flex align-items-center justify-content-center"
                            >
                              <i class="bi bi-google"></i>
                            </div>
                            <small>Google Authenticator</small>
                          </div>
                          <div class="text-center">
                            <div
                              class="auth-app-icon bg-success text-white rounded-circle d-flex align-items-center justify-content-center"
                            >
                              <i class="bi bi-shield-check"></i>
                            </div>
                            <small>Authy</small>
                          </div>
                          <div class="text-center">
                            <div
                              class="auth-app-icon bg-info text-white rounded-circle d-flex align-items-center justify-content-center"
                            >
                              <i class="bi bi-microsoft"></i>
                            </div>
                            <small>Microsoft Authenticator</small>
                          </div>
                        </div>
                      </li>

                      <li>
                        <p>
                          <strong>Scan the QR code:</strong>
                        </p>
                        <div class="qr-container mb-3">
                          <img
                            :src="qrCodeUrl"
                            alt="QR Code"
                            v-if="qrCodeUrl"
                            class="qr-code img-fluid"
                          />
                          <div v-else class="qr-placeholder">
                            <LoadingSpinner />
                          </div>
                        </div>

                        <div class="alert alert-secondary">
                          <small>
                            <strong>Can't scan?</strong> Enter this key
                            manually:<br />
                            <code>{{ secretKey }}</code>
                          </small>
                        </div>
                      </li>
                    </ol>
                  </div>

                  <div class="col-md-6">
                    <div class="card bg-light">
                      <div class="card-body">
                        <h6 class="card-title">
                          <i class="bi bi-3-circle"></i> Verify Setup
                        </h6>

                        <form @submit.prevent="verifyAndEnable">
                          <div class="mb-3">
                            <label for="verificationCode" class="form-label">
                              Enter verification code from your app:
                            </label>
                            <input
                              type="text"
                              class="form-control form-control-lg text-center"
                              id="verificationCode"
                              placeholder="000000"
                              v-model="verificationCode"
                              pattern="[0-9]{6}"
                              maxlength="6"
                              required
                              autocomplete="off"
                            />
                            <div class="form-text">
                              Enter the 6-digit code from your authenticator app
                            </div>
                          </div>

                          <div
                            class="alert alert-danger"
                            v-if="verificationError"
                          >
                            <i class="bi bi-exclamation-triangle"></i>
                            {{ verificationError }}
                          </div>

                          <div class="d-grid gap-2">
                            <button
                              class="btn btn-success"
                              type="submit"
                              :disabled="
                                verifying || verificationCode.length !== 6
                              "
                            >
                              <LoadingSpinner
                                v-if="verifying"
                                size="sm"
                                class="me-2"
                              />
                              <i class="bi bi-check-circle me-2" v-else></i>
                              Complete Setup
                            </button>

                            <button
                              type="button"
                              class="btn btn-outline-secondary"
                              @click="cancelSetup"
                            >
                              Cancel
                            </button>
                          </div>
                        </form>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="alert alert-warning mt-4">
                  <i class="bi bi-exclamation-triangle"></i>
                  <strong>Important:</strong> After enabling 2FA, you'll need to
                  enter a verification code from your authenticator app each
                  time you sign in. Make sure to save your secret key in a
                  secure location as a backup.
                </div>
              </div>

              <!-- Error Display -->
              <div v-if="error" class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                {{ error }}
              </div>

              <!-- Success Messages -->
              <div v-if="successMessage" class="alert alert-success">
                <i class="bi bi-check-circle"></i>
                {{ successMessage }}
              </div>

              <div v-if="backupCodes.length" class="alert alert-secondary mt-3">
                <h5 class="mb-2">New Backup Codes</h5>
                <ul class="list-unstyled mb-0">
                  <li v-for="code in backupCodes" :key="code">
                    <code>{{ code }}</code>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useStore } from "vuex";
import AuthService from "@/services/auth.service";

export default {
  name: "TwoFactorAuth",

  setup() {
    const store = useStore();
    const loading = ref(true);
    const is2FAEnabled = ref(false);
    const showSetup = ref(false);
    const enabling = ref(false);
    const disabling = ref(false);
    const regenerating = ref(false);
    const verifying = ref(false);
    const qrCodeUrl = ref("");
    const secretKey = ref("");
    const verificationCode = ref("");
    const verificationError = ref("");
    const error = ref("");
    const successMessage = ref("");
    const backupCodes = ref([]);

    // Incarca statusul 2FA al utilizatorului
    const loadStatus = async () => {
      try {
        const response = await AuthService.get2FAStatus();
        is2FAEnabled.value = response.data.two_fa_enabled;
      } catch (error) {
        console.error("Failed to load 2FA status", error);
        error.value = "Failed to load 2FA status. Please refresh the page.";
      } finally {
        loading.value = false;
      }
    };

    // Initiere proces de activare 2FA
    const enable2FA = async () => {
      enabling.value = true;
      error.value = "";

      try {
        const response = await AuthService.enable2FA();

        qrCodeUrl.value = response.data.qr_code;
        secretKey.value = response.data.key;
        showSetup.value = true;
      } catch (err) {
        console.error("Failed to enable 2FA", err);
        error.value =
          err.response?.data?.error ||
          "Failed to enable 2FA. Please try again.";
      } finally {
        enabling.value = false;
      }
    };

    // Verifica codul si finalizeaza activarea 2FA
    const verifyAndEnable = async () => {
      if (verificationCode.value.length !== 6) {
        verificationError.value = "Please enter a 6-digit code";
        return;
      }

      verifying.value = true;
      verificationError.value = "";

      try {
        await AuthService.confirm2FA(verificationCode.value);

        // Actualizeaza starea locala
        is2FAEnabled.value = true;
        showSetup.value = false;

        const user = store.getters["auth/currentUser"];
        if (user) {
          store.commit("auth/setUser", { ...user, two_fa_enabled: true });
        }

        successMessage.value =
          "Two-factor authentication has been enabled successfully!";

        // Curata mesajul dupa 5 secunde
        setTimeout(() => {
          successMessage.value = "";
        }, 5000);

        // Reset setup state
        verificationCode.value = "";
        qrCodeUrl.value = "";
        secretKey.value = "";
      } catch (err) {
        console.error("Failed to verify 2FA code", err);
        verificationError.value =
          err.response?.data?.error ||
          "Invalid verification code. Please try again.";
      } finally {
        verifying.value = false;
      }
    };

    // Anuleaza procesul de setup
    const cancelSetup = () => {
      showSetup.value = false;
      verificationCode.value = "";
      verificationError.value = "";
      qrCodeUrl.value = "";
      secretKey.value = "";
    };

    // Dezactiveaza 2FA
    const disable2FA = async () => {
      if (
        !confirm(
          "Are you sure you want to disable two-factor authentication? This will make your account less secure."
        )
      ) {
        return;
      }

      disabling.value = true;
      error.value = "";

      try {
        await AuthService.disable2FA();

        // Actualizeaza starea locala
        is2FAEnabled.value = false;

        const user = store.getters["auth/currentUser"];
        if (user) {
          store.commit("auth/setUser", { ...user, two_fa_enabled: false });
        }

        successMessage.value = "Two-factor authentication has been disabled.";

        // Curata mesajul dupa 5 secunde
        setTimeout(() => {
          successMessage.value = "";
        }, 5000);
      } catch (err) {
        console.error("Failed to disable 2FA", err);
        error.value =
          err.response?.data?.error ||
          "Failed to disable 2FA. Please try again.";
      } finally {
        disabling.value = false;
      }
    };

    // Regenereaza codurile de backup
    const regenerate2FA = async () => {
      if (
        !confirm(
          "Are you sure you want to regenerate your backup codes? Your old codes will no longer work."
        )
      ) {
        return;
      }

      regenerating.value = true;
      error.value = "";

      try {
        const response = await AuthService.regenerateBackupCodes();
        backupCodes.value = response.data.backup_codes || [];
        successMessage.value = "Backup codes have been regenerated.";

        setTimeout(() => {
          successMessage.value = "";
        }, 5000);
      } catch (err) {
        console.error("Failed to regenerate backup codes", err);
        error.value = "Failed to regenerate backup codes. Please try again.";
      } finally {
        regenerating.value = false;
      }
    };

    onMounted(() => {
      loadStatus();
    });

    return {
      loading,
      is2FAEnabled,
      showSetup,
      enabling,
      disabling,
      regenerating,
      verifying,
      qrCodeUrl,
      secretKey,
      verificationCode,
      verificationError,
      error,
      successMessage,
      backupCodes,
      enable2FA,
      disable2FA,
      regenerate2FA,
      verifyAndEnable,
      cancelSetup,
    };
  },
};
</script>

<style scoped>
.setup-steps li {
  margin-bottom: 1.5rem;
}

.auth-app-icon {
  width: 50px;
  height: 50px;
  font-size: 1.2rem;
}

.qr-container {
  text-align: center;
}

.qr-code {
  max-width: 200px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 10px;
  background: white;
}

.qr-placeholder {
  width: 200px;
  height: 200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.form-control-lg {
  font-family: "Courier New", monospace;
  letter-spacing: 2px;
}

code {
  font-size: 1.1rem;
  padding: 0.25rem 0.5rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  word-break: break-all;
}
</style>
