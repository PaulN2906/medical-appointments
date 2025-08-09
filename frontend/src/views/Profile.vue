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
            <ProfilePersonalInfo v-if="activeTab === 'personal'" />
            <ProfileSecuritySettings v-if="activeTab === 'security'" />
            <ProfileNotificationPreferences
              v-if="activeTab === 'notifications'"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import ProfilePersonalInfo from "@/components/profile/PersonalInfo.vue";
import ProfileSecuritySettings from "@/components/profile/SecuritySettings.vue";
import ProfileNotificationPreferences from "@/components/profile/NotificationPreferences.vue";

export default {
  name: "Profile",
  components: {
    ProfilePersonalInfo,
    ProfileSecuritySettings,
    ProfileNotificationPreferences,
  },
  setup() {
    const activeTab = ref("personal");

    const getActiveTabTitle = () => {
      const titles = {
        personal: "Personal Information",
        security: "Security Settings",
        notifications: "Notification Preferences",
      };
      return titles[activeTab.value] || "Settings";
    };

    return {
      activeTab,
      getActiveTabTitle,
    };
  },
};
</script>
