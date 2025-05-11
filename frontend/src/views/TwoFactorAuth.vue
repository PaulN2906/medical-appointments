<template>
  <div class="container my-4">
    <h1 class="mb-4">Two-Factor Authentication</h1>

    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">2FA Settings</div>
          <div class="card-body">
            <div v-if="loading" class="text-center p-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else>
              <div v-if="!is2FAEnabled" class="mb-4">
                <h5>Enable Two-Factor Authentication</h5>
                <p>
                  Two-factor authentication adds an extra layer of security to
                  your account by requiring more than just a password to sign
                  in.
                </p>

                <button
                  @click="enable2FA"
                  class="btn btn-primary"
                  :disabled="enabling"
                >
                  <span
                    v-if="enabling"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                  ></span>
                  Enable 2FA
                </button>
              </div>

              <div v-else class="mb-4">
                <div class="alert alert-success">
                  <i class="bi bi-shield-check"></i> Two-factor authentication
                  is enabled for your account.
                </div>

                <button
                  @click="disable2FA"
                  class="btn btn-danger"
                  :disabled="disabling"
                >
                  <span
                    v-if="disabling"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                  ></span>
                  Disable 2FA
                </button>
              </div>

              <div v-if="showSetup" class="mt-4">
                <h5>Setup Instructions</h5>
                <hr />

                <ol class="setup-steps">
                  <li>
                    <p>
                      Download and install an authenticator app on your mobile
                      device:
                    </p>
                    <div class="row">
                      <div class="col-md-4 text-center mb-3">
                        <img
                          src="@/assets/google-authenticator.png"
                          alt="Google Authenticator"
                          class="auth-app-logo"
                        />
                        <p>Google Authenticator</p>
                      </div>
                      <div class="col-md-4 text-center mb-3">
                        <img
                          src="@/assets/authy.png"
                          alt="Authy"
                          class="auth-app-logo"
                        />
                        <p>Authy</p>
                      </div>
                      <div class="col-md-4 text-center mb-3">
                        <img
                          src="@/assets/microsoft-authenticator.png"
                          alt="Microsoft Authenticator"
                          class="auth-app-logo"
                        />
                        <p>Microsoft Authenticator</p>
                      </div>
                    </div>
                  </li>

                  <li>
                    <p>Scan this QR code with your authenticator app:</p>
                    <div class="text-center qr-container">
                      <img
                        :src="qrCodeUrl"
                        alt="QR Code"
                        v-if="qrCodeUrl"
                        class="qr-code"
                      />
                      <div v-else class="qr-placeholder">
                        <span class="spinner-border" role="status"></span>
                      </div>
                    </div>
                    <p class="text-center mt-2">
                      <small
                        >Or enter this key manually:
                        <strong>{{ secretKey }}</strong></small
                      >
                    </p>
                  </li>

                  <li>
                    <p>
                      Enter the verification code from your authenticator app:
                    </p>
                    <div class="row justify-content-center">
                      <div class="col-md-6">
                        <form @submit.prevent="verifyAndEnable">
                          <div class="input-group mb-3">
                            <input
                              type="text"
                              class="form-control"
                              placeholder="6-digit code"
                              v-model="verificationCode"
                              pattern="[0-9]{6}"
                              maxlength="6"
                              required
                            />
                            <button
                              class="btn btn-primary"
                              type="submit"
                              :disabled="verifying"
                            >
                              <span
                                v-if="verifying"
                                class="spinner-border spinner-border-sm me-2"
                                role="status"
                              ></span>
                              Verify
                            </button>
                          </div>
                          <div
                            class="alert alert-danger"
                            v-if="verificationError"
                          >
                            {{ verificationError }}
                          </div>
                        </form>
                      </div>
                    </div>
                  </li>
                </ol>

                <div class="alert alert-info mt-4">
                  <i class="bi bi-info-circle"></i> After enabling 2FA, you'll
                  need to enter a verification code from your authenticator app
                  each time you sign in.
                </div>
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
import AuthService from "@/services/auth.service";

export default {
  name: "TwoFactorAuth",

  setup() {
    const loading = ref(true);
    const is2FAEnabled = ref(false);
    const showSetup = ref(false);
    const enabling = ref(false);
    const disabling = ref(false);
    const verifying = ref(false);
    const qrCodeUrl = ref("");
    const secretKey = ref("");
    const verificationCode = ref("");
    const verificationError = ref("");

    // Incarca statusul 2FA al utilizatorului
    const loadStatus = async () => {
      try {
        // TODO: request la server pentru a obtine statusul 2FA
        // Aici simulam un raspuns
        const user = AuthService.getUser();
        is2FAEnabled.value = user ? user.two_fa_enabled : false;
      } catch (error) {
        console.error("Failed to load 2FA status", error);
      } finally {
        loading.value = false;
      }
    };

    // Initiere proces de activare 2FA
    const enable2FA = async () => {
      enabling.value = true;
      showSetup.value = true;

      try {
        const response = await AuthService.enable2FA();

        // In raspuns ar trebui sa primim un QR code URL si o cheie secreta
        qrCodeUrl.value = response.data.totp_url;
        secretKey.value = response.data.key;
      } catch (error) {
        console.error("Failed to enable 2FA", error);
        alert("Failed to enable 2FA. Please try again.");
        showSetup.value = false;
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
        // Trimitem codul de verificare catre server
        await AuthService.verify2FA(verificationCode.value);

        // Actualizam starea locala
        is2FAEnabled.value = true;
        showSetup.value = false;

        // Actualizam profilul utilizatorului în localStorage
        const user = AuthService.getUser();
        if (user) {
          user.two_fa_enabled = true;
          localStorage.setItem("user", JSON.stringify(user));
        }

        alert("Two-factor authentication has been enabled successfully!");
      } catch (error) {
        console.error("Failed to verify 2FA code", error);
        verificationError.value =
          error.response?.data?.error ||
          "Invalid verification code. Please try again.";
      } finally {
        verifying.value = false;
      }
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

      try {
        // Intr-o implementare reala, am face un request catre server
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulam un delay

        // Actualizam starea locala
        is2FAEnabled.value = false;

        // Actualizam profilul utilizatorului in localStorage
        const user = AuthService.getUser();
        if (user) {
          user.two_fa_enabled = false;
          localStorage.setItem("user", JSON.stringify(user));
        }

        alert("Two-factor authentication has been disabled.");
      } catch (error) {
        console.error("Failed to disable 2FA", error);
        alert("Failed to disable 2FA. Please try again.");
      } finally {
        disabling.value = false;
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
      verifying,
      qrCodeUrl,
      secretKey,
      verificationCode,
      verificationError,
      enable2FA,
      disable2FA,
      verifyAndEnable,
    };
  },
};
</script>

<style scoped>
.setup-steps li {
  margin-bottom: 2rem;
}

.auth-app-logo {
  max-width: 80px;
  height: auto;
}

.qr-container {
  margin: 1rem 0;
}

.qr-code {
  max-width: 200px;
  height: auto;
}

.qr-placeholder {
  width: 200px;
  height: 200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  border-radius: 4px;
}
</style>
