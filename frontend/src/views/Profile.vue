<template>
  <div class="container my-4">
    <h1 class="mb-4">My Profile</h1>

    <div class="row">
      <div class="col-md-3 mb-4">
        <div class="list-group">
          <a
            href="#"
            @click.prevent="activeTab = 'personal'"
            class="list-group-item list-group-item-action"
            :class="{ active: activeTab === 'personal' }"
          >
            <i class="bi bi-person me-2"></i> Personal Information
          </a>
          <a
            href="#"
            @click.prevent="activeTab = 'security'"
            class="list-group-item list-group-item-action"
            :class="{ active: activeTab === 'security' }"
          >
            <i class="bi bi-shield-lock me-2"></i> Security
          </a>
          <a
            href="#"
            @click.prevent="activeTab = 'notifications'"
            class="list-group-item list-group-item-action"
            :class="{ active: activeTab === 'notifications' }"
          >
            <i class="bi bi-bell me-2"></i> Notification Preferences
          </a>
        </div>
      </div>

      <div class="col-md-9">
        <div class="card">
          <div class="card-header">
            {{ getActiveTabTitle() }}
          </div>
          <div class="card-body">
            <!-- Personal Information Tab -->
            <div v-if="activeTab === 'personal'">
              <form @submit.prevent="savePersonalInfo">
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label for="firstName" class="form-label">First Name</label>
                    <input
                      type="text"
                      class="form-control"
                      id="firstName"
                      v-model="personalInfo.firstName"
                      required
                    />
                  </div>
                  <div class="col-md-6">
                    <label for="lastName" class="form-label">Last Name</label>
                    <input
                      type="text"
                      class="form-control"
                      id="lastName"
                      v-model="personalInfo.lastName"
                      required
                    />
                  </div>
                </div>

                <div class="mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    v-model="personalInfo.email"
                    required
                    readonly
                  />
                  <div class="form-text">Email cannot be changed.</div>
                </div>

                <div class="mb-3">
                  <label for="phone" class="form-label">Phone Number</label>
                  <input
                    type="tel"
                    class="form-control"
                    id="phone"
                    v-model="personalInfo.phone"
                  />
                </div>

                <div v-if="userType === 'patient'" class="mb-3">
                  <label for="birthDate" class="form-label"
                    >Date of Birth</label
                  >
                  <input
                    type="date"
                    class="form-control"
                    id="birthDate"
                    v-model="personalInfo.birthDate"
                  />
                </div>

                <div v-if="userType === 'doctor'" class="mb-3">
                  <label for="speciality" class="form-label">Speciality</label>
                  <input
                    type="text"
                    class="form-control"
                    id="speciality"
                    v-model="personalInfo.speciality"
                  />
                </div>

                <div v-if="userType === 'doctor'" class="mb-3">
                  <label for="description" class="form-label"
                    >Professional Description</label
                  >
                  <textarea
                    class="form-control"
                    id="description"
                    v-model="personalInfo.description"
                    rows="4"
                  ></textarea>
                </div>

                <div v-if="personalInfoSaved" class="alert alert-success mb-3">
                  Personal information updated successfully!
                </div>

                <div class="text-end">
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="savingPersonalInfo"
                  >
                    <span
                      v-if="savingPersonalInfo"
                      class="spinner-border spinner-border-sm me-2"
                      role="status"
                    ></span>
                    Save Changes
                  </button>
                </div>
              </form>
            </div>

            <!-- Security Tab -->
            <div v-if="activeTab === 'security'">
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
                  <label for="currentPassword" class="form-label"
                    >Current Password</label
                  >
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
                  <label for="newPassword" class="form-label"
                    >New Password</label
                  >
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
                    Password must be at least 8 characters long and contain a
                    mix of letters, numbers, and special characters.
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
                        passwordForm.newPassword !==
                          passwordForm.confirmPassword,
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
                    <span
                      v-if="savingPassword"
                      class="spinner-border spinner-border-sm me-2"
                      role="status"
                    ></span>
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

            <!-- Notification Preferences Tab -->
            <div v-if="activeTab === 'notifications'">
              <div class="form-check form-switch mb-3">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="emailNotifications"
                  v-model="notificationPrefs.email"
                />
                <label class="form-check-label" for="emailNotifications">
                  Email Notifications
                </label>
                <div class="form-text">
                  Receive appointment confirmations, reminders, and updates via
                  email.
                </div>
              </div>

              <div class="form-check form-switch mb-3">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="reminderNotifications"
                  v-model="notificationPrefs.reminders"
                />
                <label class="form-check-label" for="reminderNotifications">
                  Appointment Reminders
                </label>
                <div class="form-text">
                  Receive reminders 24 hours before your scheduled appointments.
                </div>
              </div>

              <div class="form-check form-switch mb-3">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="statusNotifications"
                  v-model="notificationPrefs.statusUpdates"
                />
                <label class="form-check-label" for="statusNotifications">
                  Status Update Notifications
                </label>
                <div class="form-text">
                  Receive notifications when your appointments are confirmed,
                  cancelled, or rescheduled.
                </div>
              </div>

              <div
                v-if="notificationPrefsSaved"
                class="alert alert-success mb-3"
              >
                Notification preferences updated successfully!
              </div>

              <div class="text-end">
                <button
                  @click="saveNotificationPrefs"
                  class="btn btn-primary"
                  :disabled="savingNotificationPrefs"
                >
                  <span
                    v-if="savingNotificationPrefs"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                  ></span>
                  Save Preferences
                </button>
              </div>
            </div>
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

export default {
  name: "Profile",

  setup() {
    const store = useStore();
    const activeTab = ref("personal");

    // Starea utilizatorului curent
    const currentUser = computed(() => store.getters["auth/currentUser"]);
    const userType = computed(() => {
      return currentUser.value?.role || "patient";
    });

    // Starea 2FA
    const is2FAEnabled = ref(false);
    const loading2FAStatus = ref(true);

    // Formulare pentru diferite secțiuni
    const personalInfo = reactive({
      firstName: "",
      lastName: "",
      email: "",
      phone: "",
      birthDate: "",
      speciality: "",
      description: "",
    });

    const passwordForm = reactive({
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    });

    const notificationPrefs = reactive({
      email: true,
      reminders: true,
      statusUpdates: true,
    });

    // Stari pentru salvarea formularelor
    const savingPersonalInfo = ref(false);
    const personalInfoSaved = ref(false);
    const savingPassword = ref(false);
    const passwordChanged = ref(false);
    const passwordError = ref("");
    const savingNotificationPrefs = ref(false);
    const notificationPrefsSaved = ref(false);

    // Computed pentru validarea formularului de parola
    const isPasswordFormValid = computed(() => {
      return (
        passwordForm.currentPassword &&
        passwordForm.newPassword &&
        passwordForm.confirmPassword &&
        passwordForm.newPassword === passwordForm.confirmPassword &&
        passwordForm.newPassword.length >= 8
      );
    });

    // Incarca datele utilizatorului
    const loadUserData = () => {
      if (currentUser.value) {
        personalInfo.firstName = currentUser.value.first_name || "";
        personalInfo.lastName = currentUser.value.last_name || "";
        personalInfo.email = currentUser.value.email || "";

        // In implementarea reala, ai incarca si celelalte date din profil
        personalInfo.phone = ""; // placeholder
        personalInfo.birthDate = ""; // placeholder
        personalInfo.speciality = ""; // pentru medici
        personalInfo.description = ""; // pentru medici

        // Placeholder pentru preferintele de notificare
        notificationPrefs.email = true;
        notificationPrefs.reminders = true;
        notificationPrefs.statusUpdates = true;
      }
    };

    // Incarca statusul 2FA
    const load2FAStatus = async () => {
      try {
        const response = await AuthService.get2FAStatus();
        is2FAEnabled.value = response.data.two_fa_enabled;
      } catch (error) {
        console.error("Failed to load 2FA status", error);
        // Fallback la informatia din localStorage
        is2FAEnabled.value = currentUser.value?.two_fa_enabled || false;
      } finally {
        loading2FAStatus.value = false;
      }
    };

    // Obtine titlul pentru tabul activ
    const getActiveTabTitle = () => {
      const titles = {
        personal: "Personal Information",
        security: "Security Settings",
        notifications: "Notification Preferences",
      };

      return titles[activeTab.value] || "Settings";
    };

    // Formateaza data ultimei autentificari
    const formatLastLogin = () => {
      // Placeholder - in implementarea reală ai primi aceasta de la server
      const lastLogin = new Date();
      lastLogin.setHours(lastLogin.getHours() - 2); // Simuleaza acum 2 ore

      return lastLogin.toLocaleString("ro-RO", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    // Salveaza informatiile personale
    const savePersonalInfo = async () => {
      savingPersonalInfo.value = true;
      personalInfoSaved.value = false;

      try {
        // TODO: request catre server
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulam un delay

        // TODO: Actualizam utilizatorul in store
        //const updatedUser = {
        //  ...currentUser.value,
        //  first_name: personalInfo.firstName,
        //  last_name: personalInfo.lastName,
        //  // etc.
        //};

        // TODO: actualizare utilizator in store
        // store.commit('auth/setUser', updatedUser);

        personalInfoSaved.value = true;

        // Ascunde mesajul de success dupa 3 secunde
        setTimeout(() => {
          personalInfoSaved.value = false;
        }, 3000);
      } catch (error) {
        console.error("Failed to save personal information", error);
      } finally {
        savingPersonalInfo.value = false;
      }
    };

    // Schimba parola
    const changePassword = async () => {
      passwordError.value = "";
      passwordChanged.value = false;

      // Valideaza noua parola
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
        // TODO: request catre server
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulăm un delay

        passwordChanged.value = true;

        // Reset form
        passwordForm.currentPassword = "";
        passwordForm.newPassword = "";
        passwordForm.confirmPassword = "";

        // Ascunde mesajul de success dupa 3 secunde
        setTimeout(() => {
          passwordChanged.value = false;
        }, 3000);
      } catch (error) {
        console.error("Failed to change password", error);
        passwordError.value =
          error.response?.data?.error ||
          "Failed to change password. Please try again.";
      } finally {
        savingPassword.value = false;
      }
    };

    // Salveaza preferintele de notificare
    const saveNotificationPrefs = async () => {
      savingNotificationPrefs.value = true;
      notificationPrefsSaved.value = false;

      try {
        // TODO: request catre server
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulam un delay

        notificationPrefsSaved.value = true;

        // Ascunde mesajul de success dupa 3 secunde
        setTimeout(() => {
          notificationPrefsSaved.value = false;
        }, 3000);
      } catch (error) {
        console.error("Failed to save notification preferences", error);
      } finally {
        savingNotificationPrefs.value = false;
      }
    };

    onMounted(() => {
      loadUserData();
      load2FAStatus();
    });

    return {
      activeTab,
      currentUser,
      userType,
      is2FAEnabled,
      loading2FAStatus,
      personalInfo,
      passwordForm,
      notificationPrefs,
      savingPersonalInfo,
      personalInfoSaved,
      savingPassword,
      passwordChanged,
      passwordError,
      savingNotificationPrefs,
      notificationPrefsSaved,
      isPasswordFormValid,
      getActiveTabTitle,
      formatLastLogin,
      savePersonalInfo,
      changePassword,
      saveNotificationPrefs,
    };
  },
};
</script>

<style scoped>
/* Stilizare specifica pentru pagina de profil */
</style>
