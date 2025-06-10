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
              <div v-if="loadingProfile" class="text-center p-4">
                <div class="spinner-border" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>

              <div v-else-if="personalInfoError" class="alert alert-danger">
                {{ personalInfoError }}
              </div>

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
              <div v-if="loadingNotifications" class="text-center p-4">
                <div class="spinner-border" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>

              <div v-else>
                <div class="row mb-4">
                  <div class="col-md-8">
                    <h5>Email Notifications</h5>
                    <p class="text-muted">
                      Configure when you want to receive emails about your
                      appointments.
                    </p>
                  </div>
                  <div class="col-md-4 text-end">
                    <button
                      @click="resetNotificationPrefs"
                      class="btn btn-outline-secondary btn-sm"
                      :disabled="savingNotificationPrefs"
                    >
                      Reset to Defaults
                    </button>
                  </div>
                </div>

                <form @submit.prevent="saveNotificationPrefs">
                  <!-- Master Email Toggle -->
                  <div class="card mb-3">
                    <div class="card-body">
                      <div class="form-check form-switch">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          id="emailEnabled"
                          v-model="notificationPrefs.email_enabled"
                        />
                        <label class="form-check-label" for="emailEnabled">
                          <strong>Enable Email Notifications</strong>
                        </label>
                        <div class="form-text">
                          Master switch for all email notifications. When
                          disabled, you won't receive any emails.
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Email Notification Types -->
                  <div
                    class="card mb-3"
                    :class="{ 'opacity-50': !notificationPrefs.email_enabled }"
                  >
                    <div class="card-header">
                      <h6 class="mb-0">Email Types</h6>
                    </div>
                    <div class="card-body">
                      <div class="form-check form-switch mb-3">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          id="appointmentConfirmations"
                          v-model="notificationPrefs.appointment_confirmations"
                          :disabled="!notificationPrefs.email_enabled"
                        />
                        <label
                          class="form-check-label"
                          for="appointmentConfirmations"
                        >
                          Appointment Confirmations
                        </label>
                        <div class="form-text">
                          Receive emails when your appointments are confirmed by
                          doctors.
                        </div>
                      </div>

                      <div class="form-check form-switch mb-3">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          id="appointmentReminders"
                          v-model="notificationPrefs.appointment_reminders"
                          :disabled="!notificationPrefs.email_enabled"
                        />
                        <label
                          class="form-check-label"
                          for="appointmentReminders"
                        >
                          Appointment Reminders
                        </label>
                        <div class="form-text">
                          Receive reminder emails before your scheduled
                          appointments.
                        </div>
                      </div>

                      <div class="form-check form-switch mb-3">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          id="appointmentCancellations"
                          v-model="notificationPrefs.appointment_cancellations"
                          :disabled="!notificationPrefs.email_enabled"
                        />
                        <label
                          class="form-check-label"
                          for="appointmentCancellations"
                        >
                          Appointment Cancellations
                        </label>
                        <div class="form-text">
                          Receive emails when appointments are cancelled or
                          rescheduled.
                        </div>
                      </div>

                      <!-- Reminder Timing -->
                      <div
                        class="mb-3"
                        v-if="
                          notificationPrefs.appointment_reminders &&
                          notificationPrefs.email_enabled
                        "
                      >
                        <label for="reminderHours" class="form-label"
                          >Reminder Timing</label
                        >
                        <select
                          class="form-select"
                          id="reminderHours"
                          v-model="notificationPrefs.reminder_hours_before"
                        >
                          <option value="1">1 hour before</option>
                          <option value="2">2 hours before</option>
                          <option value="6">6 hours before</option>
                          <option value="12">12 hours before</option>
                          <option value="24">24 hours before (default)</option>
                          <option value="48">48 hours before</option>
                        </select>
                        <div class="form-text">
                          When to send appointment reminder emails.
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- System Notifications -->
                  <div class="card mb-3">
                    <div class="card-header">
                      <h6 class="mb-0">In-App Notifications</h6>
                    </div>
                    <div class="card-body">
                      <div class="form-check form-switch mb-3">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          id="systemNotifications"
                          v-model="notificationPrefs.system_notifications"
                        />
                        <label
                          class="form-check-label"
                          for="systemNotifications"
                        >
                          System Notifications
                        </label>
                        <div class="form-text">
                          Show notifications within the application interface.
                        </div>
                      </div>

                      <div class="form-check form-switch mb-3">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          id="statusUpdates"
                          v-model="notificationPrefs.status_updates"
                          :disabled="!notificationPrefs.system_notifications"
                        />
                        <label class="form-check-label" for="statusUpdates">
                          Status Update Notifications
                        </label>
                        <div class="form-text">
                          Get notified about changes to your appointments and
                          profile.
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Marketing (Optional) -->
                  <div class="card mb-3">
                    <div class="card-header">
                      <h6 class="mb-0">Optional Communications</h6>
                    </div>
                    <div class="card-body">
                      <div class="form-check form-switch">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          id="marketingEmails"
                          v-model="notificationPrefs.marketing_emails"
                        />
                        <label class="form-check-label" for="marketingEmails">
                          Marketing Emails
                        </label>
                        <div class="form-text">
                          Receive emails about new features, health tips, and
                          promotional content.
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Error/Success Messages -->
                  <div v-if="notificationError" class="alert alert-danger mb-3">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    {{ notificationError }}
                  </div>

                  <div
                    v-if="notificationPrefsSaved"
                    class="alert alert-success mb-3"
                  >
                    <i class="bi bi-check-circle me-2"></i>
                    Notification preferences updated successfully!
                  </div>

                  <!-- Save Button -->
                  <div class="text-end">
                    <button
                      type="submit"
                      class="btn btn-primary"
                      :disabled="savingNotificationPrefs"
                    >
                      <span
                        v-if="savingNotificationPrefs"
                        class="spinner-border spinner-border-sm me-2"
                        role="status"
                      ></span>
                      <i class="bi bi-bell me-2" v-else></i>
                      Save Preferences
                    </button>
                  </div>
                </form>
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
import UserService from "@/services/user.service";

export default {
  name: "Profile",

  setup() {
    const store = useStore();
    const activeTab = ref("personal");

    // Loading states
    const loadingProfile = ref(true);
    const loadingNotifications = ref(true);
    const loading2FAStatus = ref(true);

    // Current user from store
    const currentUser = computed(() => store.getters["auth/currentUser"]);
    const userType = computed(() => {
      return currentUser.value?.role || "patient";
    });

    // 2FA status
    const is2FAEnabled = ref(false);

    // Complete profile data
    const profileData = ref({});

    // Form data (reactive for two-way binding)
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
      email_enabled: true,
      appointment_confirmations: true,
      appointment_reminders: true,
      appointment_cancellations: true,
      system_notifications: true,
      status_updates: true,
      reminder_hours_before: 24,
      marketing_emails: false,
    });

    // Form states
    const savingPersonalInfo = ref(false);
    const personalInfoSaved = ref(false);
    const personalInfoError = ref("");

    const savingPassword = ref(false);
    const passwordChanged = ref(false);
    const passwordError = ref("");

    const savingNotificationPrefs = ref(false);
    const notificationPrefsSaved = ref(false);
    const notificationError = ref("");

    // Computed validations
    const isPasswordFormValid = computed(() => {
      return (
        passwordForm.currentPassword &&
        passwordForm.newPassword &&
        passwordForm.confirmPassword &&
        passwordForm.newPassword === passwordForm.confirmPassword &&
        passwordForm.newPassword.length >= 8
      );
    });

    // Load complete user profile from server
    const loadUserProfile = async () => {
      try {
        const response = await UserService.getUserProfile();
        profileData.value = response.data;

        // Populate form fields
        personalInfo.firstName = profileData.value.first_name || "";
        personalInfo.lastName = profileData.value.last_name || "";
        personalInfo.email = profileData.value.email || "";
        personalInfo.phone = profileData.value.phone_number || "";

        // Role-specific fields
        if (userType.value === "doctor") {
          personalInfo.speciality = profileData.value.speciality || "";
          personalInfo.description = profileData.value.description || "";
        } else if (userType.value === "patient") {
          personalInfo.birthDate = profileData.value.date_of_birth || "";
        }

      } catch (error) {
        console.error("Failed to load user profile:", error);
        personalInfoError.value =
          "Failed to load profile data. Please refresh the page.";
      } finally {
        loadingProfile.value = false;
      }
    };

    // Load 2FA status
    const load2FAStatus = async () => {
      try {
        const response = await AuthService.get2FAStatus();
        is2FAEnabled.value = response.data.two_fa_enabled;
      } catch (error) {
        console.error("Failed to load 2FA status", error);
        // Fallback to localStorage data
        is2FAEnabled.value = currentUser.value?.two_fa_enabled || false;
      } finally {
        loading2FAStatus.value = false;
      }
    };

    // Get active tab title
    const getActiveTabTitle = () => {
      const titles = {
        personal: "Personal Information",
        security: "Security Settings",
        notifications: "Notification Preferences",
      };
      return titles[activeTab.value] || "Settings";
    };

    // Format last login date
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

    // Save personal information
    const savePersonalInfo = async () => {
      savingPersonalInfo.value = true;
      personalInfoSaved.value = false;
      personalInfoError.value = "";

      try {
        const updateData = {
          first_name: personalInfo.firstName,
          last_name: personalInfo.lastName,
          phone_number: personalInfo.phone,
        };

        // Add role-specific data
        if (userType.value === "doctor") {
          updateData.speciality = personalInfo.speciality;
          updateData.description = personalInfo.description;
        } else if (userType.value === "patient") {
          updateData.date_of_birth = personalInfo.birthDate;
        }

        const response = await UserService.updateProfile(updateData);

        // Update local profile data
        profileData.value = response.data;

        // Update store with new user data
        const updatedUser = {
          ...currentUser.value,
          first_name: response.data.first_name,
          last_name: response.data.last_name,
        };
        store.commit("auth/setUser", updatedUser);

        // Update localStorage
        AuthService.saveUserData(updatedUser);

        personalInfoSaved.value = true;

        // Hide success message after 3 seconds
        setTimeout(() => {
          personalInfoSaved.value = false;
        }, 3000);
      } catch (error) {
        console.error("Failed to save personal information:", error);
        personalInfoError.value =
          error.response?.data?.error ||
          "Failed to save personal information. Please try again.";
      } finally {
        savingPersonalInfo.value = false;
      }
    };

    // Change password
    const changePassword = async () => {
      passwordError.value = "";
      passwordChanged.value = false;

      // Client-side validation
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
        const response = await UserService.changePassword({
          current_password: passwordForm.currentPassword,
          new_password: passwordForm.newPassword,
        });

        // Update token if returned (old tokens are invalidated)
        if (response.data.token) {
          store.commit("auth/setToken", response.data.token);
        }

        passwordChanged.value = true;

        // Reset form
        passwordForm.currentPassword = "";
        passwordForm.newPassword = "";
        passwordForm.confirmPassword = "";

        // Hide success message after 3 seconds
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

    // Load notification preferences from server
    const loadNotificationPreferences = async () => {
      try {
        const response = await UserService.getNotificationPreferences();
        const prefs = response.data;

        // Update reactive object with server data
        Object.assign(notificationPrefs, {
          email_enabled: prefs.email_enabled,
          appointment_confirmations: prefs.appointment_confirmations,
          appointment_reminders: prefs.appointment_reminders,
          appointment_cancellations: prefs.appointment_cancellations,
          system_notifications: prefs.system_notifications,
          status_updates: prefs.status_updates,
          reminder_hours_before: prefs.reminder_hours_before,
          marketing_emails: prefs.marketing_emails,
        });
      } catch (error) {
        console.error("Failed to load notification preferences:", error);
        notificationError.value =
          "Failed to load notification preferences. Using defaults.";
      } finally {
        loadingNotifications.value = false;
      }
    };

    // Save notification preferences - REAL IMPLEMENTATION
    const saveNotificationPrefs = async () => {
      savingNotificationPrefs.value = true;
      notificationPrefsSaved.value = false;
      notificationError.value = "";

      try {
        await UserService.updateNotificationPreferences(notificationPrefs);

        notificationPrefsSaved.value = true;

        setTimeout(() => {
          notificationPrefsSaved.value = false;
        }, 3000);
      } catch (error) {
        console.error("Failed to save notification preferences:", error);
        notificationError.value =
          error.response?.data?.error ||
          "Failed to save notification preferences. Please try again.";
      } finally {
        savingNotificationPrefs.value = false;
      }
    };

    // Reset notification preferences to defaults
    const resetNotificationPrefs = async () => {
      if (
        !confirm(
          "Are you sure you want to reset all notification preferences to their default values?"
        )
      ) {
        return;
      }

      savingNotificationPrefs.value = true;
      notificationError.value = "";

      try {
        const response = await UserService.resetNotificationPreferences();
        const prefs = response.data.preferences;

        // Update reactive object with defaults
        Object.assign(notificationPrefs, {
          email_enabled: prefs.email_enabled,
          appointment_confirmations: prefs.appointment_confirmations,
          appointment_reminders: prefs.appointment_reminders,
          appointment_cancellations: prefs.appointment_cancellations,
          system_notifications: prefs.system_notifications,
          status_updates: prefs.status_updates,
          reminder_hours_before: prefs.reminder_hours_before,
          marketing_emails: prefs.marketing_emails,
        });

        notificationPrefsSaved.value = true;

        setTimeout(() => {
          notificationPrefsSaved.value = false;
        }, 3000);
      } catch (error) {
        console.error("Failed to reset notification preferences:", error);
        notificationError.value =
          error.response?.data?.error ||
          "Failed to reset notification preferences. Please try again.";
      } finally {
        savingNotificationPrefs.value = false;
      }
    };

    // Initialize component
    onMounted(() => {
      loadUserProfile();
      loadNotificationPreferences();
      load2FAStatus();
    });

    return {
      // State
      activeTab,
      loadingProfile,
      loadingNotifications,
      notificationError,
      currentUser,
      userType,
      is2FAEnabled,
      profileData,

      // Forms
      personalInfo,
      passwordForm,
      notificationPrefs,

      // Form states
      savingPersonalInfo,
      personalInfoSaved,
      personalInfoError,
      savingPassword,
      passwordChanged,
      passwordError,
      savingNotificationPrefs,
      notificationPrefsSaved,

      // Computed
      isPasswordFormValid,

      // Methods
      getActiveTabTitle,
      formatLastLogin,
      savePersonalInfo,
      changePassword,
      saveNotificationPrefs,
      resetNotificationPrefs,
    };
  },
};
</script>
