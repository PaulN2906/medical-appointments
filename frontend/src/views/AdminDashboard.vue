<template>
  <div class="container my-4">
    <h1 class="mb-4">Admin Dashboard</h1>

    <!-- Navigation Tabs -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'overview' }"
          href="#"
          @click.prevent="activeTab = 'overview'"
        >
          <i class="bi bi-house me-2"></i>Overview
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'appointments' }"
          href="#"
          @click.prevent="activeTab = 'appointments'"
        >
          <i class="bi bi-calendar me-2"></i>Appointments
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'users' }"
          href="#"
          @click.prevent="activeTab = 'users'"
        >
          <i class="bi bi-people me-2"></i>Users
        </a>
      </li>
    </ul>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Overview Tab -->
      <div v-show="activeTab === 'overview'">
        <AdminOverview />
      </div>

      <!-- Appointments Tab -->
      <div v-show="activeTab === 'appointments'">
        <AdminAppointments />
      </div>

      <!-- Users Tab -->
      <div v-show="activeTab === 'users'">
        <AdminUsers />
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import AdminOverview from "@/components/admin/AdminOverview.vue";
import AdminAppointments from "@/components/admin/AdminAppointments.vue";
import AdminUsers from "@/components/admin/AdminUsers.vue";

export default {
  name: "AdminDashboard",
  components: {
    AdminOverview,
    AdminAppointments,
    AdminUsers,
  },

  setup() {
    const activeTab = ref("overview");

    return {
      activeTab,
    };
  },
};
</script>
