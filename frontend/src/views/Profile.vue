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
                class="d-flex justify-content-between align-items-center mb-4"
              >
                <div>
                  <p class="mb-0">
                    {{
                      is2FAEnabled
                        ? "Two-factor authentication is enabled."
                        : "Two-factor authentication is not enabled."
                    }}
                  </p>
                  <small class="text-muted">
                    {{
                      is2FAEnabled
                        ? "Your account is more secure."
                        : "Enable for additional security."
                    }}
                  </small>
                </div>
                <router-link to="/security/2fa" class="btn btn-outline-primary">
                  {{ is2FAEnabled ? "Manage 2FA" : "Enable 2FA" }}
                </router-link>
              </div>

              <hr />

              <h5>Change Password</h5>
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
                  />
                  <div class="form-text">
                    Password must be at least 8 characters long.
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
                  />
                </div>

                <div v-if="passwordError" class="alert alert-danger mb-3">
                  {{ passwordError }}
                </div>

                <div v-if="passwordChanged" class="alert alert-success mb-3">
                  Password changed successfully!
                </div>

                <div class="text-end">
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="savingPassword"
                  >
                    <span
                      v-if="savingPassword"
                      class="spinner-border spinner-border-sm me-2"
                      role="status"
                    ></span>
                    Change Password
                  </button>
                </div>
              </form>
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

export default {
  name: "Profile",

  setup() {
    const store = useStore();
    const activeTab = ref("personal");

    // Starea utilizatorului curent
    const currentUser = computed(() => store.getters["auth/currentUser"]);
    const userType = computed(() => {
      // În implementarea reală, ai detecta tipul utilizatorului din datele stocate
      return currentUser.value?.role || "patient";
    });
    const is2FAEnabled = computed(() => {
      return currentUser.value?.two_fa_enabled || false;
    });

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

    // Stări pentru salvarea formularelor
    const savingPersonalInfo = ref(false);
    const personalInfoSaved = ref(false);
    const savingPassword = ref(false);
    const passwordChanged = ref(false);
    const passwordError = ref("");
    const savingNotificationPrefs = ref(false);
    const notificationPrefsSaved = ref(false);

    // Încarcă datele utilizatorului
    const loadUserData = () => {
      if (currentUser.value) {
        personalInfo.firstName = currentUser.value.first_name || "";
        personalInfo.lastName = currentUser.value.last_name || "";
        personalInfo.email = currentUser.value.email || "";

        // În implementarea reală, ai încărca și celelalte date din profil
        personalInfo.phone = ""; // placeholder
        personalInfo.birthDate = ""; // placeholder
        personalInfo.speciality = ""; // pentru medici
        personalInfo.description = ""; // pentru medici

        // Placeholder pentru preferințele de notificare
        notificationPrefs.email = true;
        notificationPrefs.reminders = true;
        notificationPrefs.statusUpdates = true;
      }
    };

    // Obține titlul pentru tabul activ
    const getActiveTabTitle = () => {
      const titles = {
        personal: "Personal Information",
        security: "Security Settings",
        notifications: "Notification Preferences",
      };

      return titles[activeTab.value] || "Settings";
    };

    // Salveaza informatiile personale
    const savePersonalInfo = async () => {
      savingPersonalInfo.value = true;
      personalInfoSaved.value = false;

      try {
        // TTODO: request catre server
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
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulam un delay

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
        passwordError.value = "Failed to change password. Please try again.";
      } finally {
        savingPassword.value = false;
      }
    };

    // Salveaza preferințele de notificare
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
    });

    return {
      activeTab,
      currentUser,
      userType,
      is2FAEnabled,
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
      getActiveTabTitle,
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
