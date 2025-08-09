<template>
  <div>
    <div v-if="loadingNotifications" class="text-center p-4">
      <LoadingSpinner />
    </div>

    <div v-else>
      <div class="row mb-4">
        <div class="col-md-8">
          <h5>Email Notifications</h5>
          <p class="text-muted">
            Configure when you want to receive emails about your appointments.
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
                Master switch for all email notifications. When disabled, you
                won't receive any emails.
              </div>
            </div>
          </div>
        </div>

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
              <label class="form-check-label" for="appointmentConfirmations">
                Appointment Confirmations
              </label>
              <div class="form-text">
                Receive emails when your appointments are confirmed by doctors.
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
              <label class="form-check-label" for="appointmentReminders">
                Appointment Reminders
              </label>
              <div class="form-text">
                Receive reminder emails before your scheduled appointments.
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
              <label class="form-check-label" for="appointmentCancellations">
                Appointment Cancellations
              </label>
              <div class="form-text">
                Receive emails when appointments are cancelled or rescheduled.
              </div>
            </div>

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
              <label class="form-check-label" for="systemNotifications">
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
                Get notified about changes to your appointments and profile.
              </div>
            </div>
          </div>
        </div>

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
                Receive occasional updates about new features and offers.
              </div>
            </div>
          </div>
        </div>

        <div v-if="notificationError" class="alert alert-danger mb-3">
          {{ notificationError }}
        </div>

        <div v-if="notificationPrefsSaved" class="alert alert-success mb-3">
          Preferences updated successfully!
        </div>

        <div class="text-end">
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="savingNotificationPrefs"
          >
            <LoadingSpinner
              v-if="savingNotificationPrefs"
              size="sm"
              class="me-2"
            />
            <i class="bi bi-bell me-2" v-else></i>
            Save Preferences
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";
import UserService from "@/services/user.service";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";

export default {
  name: "ProfileNotificationPreferences",
  components: { LoadingSpinner },
  setup() {
    const loadingNotifications = ref(true);
    const savingNotificationPrefs = ref(false);
    const notificationPrefsSaved = ref(false);
    const notificationError = ref("");

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

    const loadNotificationPreferences = async () => {
      try {
        const response = await UserService.getNotificationPreferences();
        const prefs = response.data;
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

    onMounted(() => {
      loadNotificationPreferences();
    });

    return {
      loadingNotifications,
      savingNotificationPrefs,
      notificationPrefsSaved,
      notificationError,
      notificationPrefs,
      saveNotificationPrefs,
      resetNotificationPrefs,
    };
  },
};
</script>
