<template>
  <div>
    <!-- Header cu actions -->
    <div class="row mb-4">
      <div class="col-md-8">
        <h5>Users Management</h5>
        <p class="text-muted mb-0">View and manage all users in the system</p>
      </div>
      <div class="col-md-4 text-end">
        <div class="btn-group">
          <button
            class="btn btn-success"
            @click="
              showCreateModal = true;
              createUserType = 'doctor';
            "
          >
            <i class="bi bi-person-plus me-2"></i>
            Create Doctor
          </button>
          <button
            class="btn btn-info"
            @click="
              showCreateModal = true;
              createUserType = 'patient';
            "
          >
            <i class="bi bi-people-fill me-2"></i>
            Create Patient
          </button>
        </div>
      </div>
    </div>

    <!-- User Type Tabs -->
    <div class="row mb-4">
      <div class="col-md-12">
        <ul class="nav nav-pills justify-content-center">
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: activeUserTab === 'doctors' }"
              href="#"
              @click.prevent="activeUserTab = 'doctors'"
            >
              <i class="bi bi-person-badge me-2"></i>
              Doctors ({{ doctors.length }})
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: activeUserTab === 'patients' }"
              href="#"
              @click.prevent="activeUserTab = 'patients'"
            >
              <i class="bi bi-people me-2"></i>
              Patients ({{ patients.length }})
            </a>
          </li>
        </ul>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="row mb-4">
      <div class="col-md-6 mx-auto">
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input
            type="text"
            class="form-control"
            placeholder="Search by name or email..."
            v-model="searchTerm"
          />
        </div>
      </div>
    </div>

    <!-- Doctors Tab -->
    <div v-if="activeUserTab === 'doctors'">
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">All Doctors</h6>
        </div>
        <div class="card-body">
          <div v-if="loadingDoctors" class="text-center p-4">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <div v-else-if="filteredDoctors.length === 0" class="text-center p-4">
            <i class="bi bi-person-x fs-1 text-muted"></i>
            <p class="mt-2">No doctors found matching your search.</p>
          </div>

          <div v-else class="row">
            <div
              class="col-md-6 col-lg-4 mb-4"
              v-for="doctor in filteredDoctors"
              :key="doctor.id"
            >
              <div class="card h-100">
                <div class="card-body">
                  <div
                    class="d-flex justify-content-between align-items-start mb-2"
                  >
                    <h6 class="card-title mb-0">
                      Dr. {{ doctor.user.last_name }}
                      {{ doctor.user.first_name }}
                      <span
                        v-if="!doctor.is_active"
                        class="badge bg-danger ms-2"
                        >Inactive</span
                      >
                    </h6>
                    <span class="badge bg-success">Doctor</span>
                  </div>

                  <p class="text-muted mb-2">{{ doctor.speciality }}</p>

                  <div class="mb-2">
                    <small class="text-muted">
                      <i class="bi bi-envelope me-1"></i>
                      {{ doctor.user.email }}
                    </small>
                  </div>

                  <div class="mb-3">
                    <small class="text-muted">
                      <i class="bi bi-calendar-check me-1"></i>
                      Joined: {{ formatDate(doctor.user.date_joined) }}
                    </small>
                  </div>

                  <div class="btn-group btn-group-sm w-100">
                    <button
                      class="btn btn-outline-primary"
                      @click="editUser(doctor.user, 'doctor')"
                    >
                      <i class="bi bi-pencil me-1"></i>Edit
                    </button>
                    <button
                      class="btn btn-outline-warning"
                      @click="resetPassword(doctor.user.id)"
                    >
                      <i class="bi bi-key me-1"></i>Reset PWD
                    </button>
                    <button
                      class="btn btn-outline-danger"
                      @click="deactivateUser(doctor.user.id)"
                      :disabled="!doctor.user.is_active"
                    >
                      <i class="bi bi-person-x me-1"></i>
                      {{ doctor.user.is_active ? "Deactivate" : "Inactive" }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Patients Tab -->
    <div v-if="activeUserTab === 'patients'">
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">All Patients</h6>
        </div>
        <div class="card-body">
          <div v-if="loadingPatients" class="text-center p-4">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <div
            v-else-if="filteredPatients.length === 0"
            class="text-center p-4"
          >
            <i class="bi bi-people-fill fs-1 text-muted"></i>
            <p class="mt-2">No patients found matching your search.</p>
          </div>

          <div v-else class="row">
            <div
              class="col-md-6 col-lg-4 mb-4"
              v-for="patient in filteredPatients"
              :key="patient.id"
            >
              <div class="card h-100">
                <div class="card-body">
                  <div
                    class="d-flex justify-content-between align-items-start mb-2"
                  >
                    <h6 class="card-title mb-0">
                      {{ patient.user.first_name }} {{ patient.user.last_name }}
                      <span
                        v-if="!patient.is_active"
                        class="badge bg-danger ms-2"
                        >Inactive</span
                      >
                    </h6>
                    <span class="badge bg-info">Patient</span>
                  </div>

                  <div class="mb-2">
                    <small class="text-muted">
                      <i class="bi bi-envelope me-1"></i>
                      {{ patient.user.email }}
                    </small>
                  </div>

                  <div class="mb-2" v-if="patient.date_of_birth">
                    <small class="text-muted">
                      <i class="bi bi-cake me-1"></i>
                      Born: {{ formatDate(patient.date_of_birth) }}
                    </small>
                  </div>

                  <div class="mb-3">
                    <small class="text-muted">
                      <i class="bi bi-calendar-check me-1"></i>
                      Joined: {{ formatDate(patient.user.date_joined) }}
                    </small>
                  </div>

                  <div class="btn-group btn-group-sm w-100">
                    <button
                      class="btn btn-outline-primary"
                      @click="editUser(patient.user, 'patient')"
                    >
                      <i class="bi bi-pencil me-1"></i>Edit
                    </button>
                    <button
                      class="btn btn-outline-warning"
                      @click="resetPassword(patient.user.id)"
                    >
                      <i class="bi bi-key me-1"></i>Reset PWD
                    </button>
                    <button
                      class="btn btn-outline-danger"
                      @click="deactivateUser(patient.user.id)"
                      :disabled="!patient.user.is_active"
                    >
                      <i class="bi bi-person-x me-1"></i>
                      {{ patient.user.is_active ? "Deactivate" : "Inactive" }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create User Modal -->
    <div
      class="modal fade"
      :class="{ show: showCreateModal }"
      :style="{ display: showCreateModal ? 'block' : 'none' }"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              Create New
              {{ createUserType === "doctor" ? "Doctor" : "Patient" }}
            </h5>
            <button
              type="button"
              class="btn-close"
              @click="showCreateModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <AdminCreateUser
              :userType="createUserType"
              @created="handleUserCreated"
              @cancelled="showCreateModal = false"
            />
          </div>
        </div>
      </div>
    </div>
    <div v-if="showCreateModal" class="modal-backdrop fade show"></div>

    <!-- Edit User Modal -->
    <div
      class="modal fade"
      :class="{ show: showEditModal }"
      :style="{ display: showEditModal ? 'block' : 'none' }"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit User</h5>
            <button
              type="button"
              class="btn-close"
              @click="showEditModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <AdminEditUser
              :user="editingUser"
              :userType="editingUserType"
              @updated="handleUserUpdated"
              @cancelled="showEditModal = false"
            />
          </div>
        </div>
      </div>
    </div>
    <div v-if="showEditModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import AdminService from "@/services/admin.service";
import AdminCreateUser from "./AdminCreateUser.vue";
import AdminEditUser from "./AdminEditUser.vue";

export default {
  name: "AdminUsers",
  components: {
    AdminCreateUser,
    AdminEditUser,
  },

  setup() {
    const loadingDoctors = ref(true);
    const loadingPatients = ref(true);
    const doctors = ref([]);
    const patients = ref([]);

    const activeUserTab = ref("doctors");
    const searchTerm = ref("");

    const showCreateModal = ref(false);
    const createUserType = ref("doctor");

    const showEditModal = ref(false);
    const editingUser = ref(null);
    const editingUserType = ref("");

    const loadDoctors = async () => {
      try {
        const response = await AdminService.getAllDoctors();
        doctors.value = response.data;
      } catch (error) {
        console.error("Failed to load doctors", error);
      } finally {
        loadingDoctors.value = false;
      }
    };

    const loadPatients = async () => {
      try {
        const response = await AdminService.getAllPatients();
        patients.value = response.data;
      } catch (error) {
        console.error("Failed to load patients", error);
      } finally {
        loadingPatients.value = false;
      }
    };

    // Computed filters
    const filteredDoctors = computed(() => {
      if (!searchTerm.value) return doctors.value;

      const term = searchTerm.value.toLowerCase();
      return doctors.value.filter((doctor) => {
        const fullName =
          `${doctor.user.first_name} ${doctor.user.last_name}`.toLowerCase();
        const email = doctor.user.email.toLowerCase();
        const speciality = doctor.speciality.toLowerCase();

        return (
          fullName.includes(term) ||
          email.includes(term) ||
          speciality.includes(term)
        );
      });
    });

    const filteredPatients = computed(() => {
      if (!searchTerm.value) return patients.value;

      const term = searchTerm.value.toLowerCase();
      return patients.value.filter((patient) => {
        const fullName =
          `${patient.user.first_name} ${patient.user.last_name}`.toLowerCase();
        const email = patient.user.email.toLowerCase();

        return fullName.includes(term) || email.includes(term);
      });
    });

    // Actions
    const editUser = (user, userType) => {
      editingUser.value = { ...user };
      editingUserType.value = userType;
      showEditModal.value = true;
    };

    const resetPassword = async (userId, userEmail) => {
      if (
        !confirm(
          `Are you sure you want to reset the password for ${userEmail}? A temporary password will be generated.`
        )
      ) {
        return;
      }

      try {
        const response = await AdminService.resetUserPassword(userId);

        // Show the temporary password (in practica, s-ar trimite prin email)
        alert(
          `Password reset successfully!\n\n` +
            `Temporary password: ${response.data.temporary_password}\n\n` +
            `Please securely share this with the user. They should change it on first login.`
        );

        console.log("Password reset for user:", userId);
      } catch (error) {
        console.error("Failed to reset password", error);
        const errorMsg =
          error.response?.data?.error || "Failed to reset password";
        alert(`Error: ${errorMsg}`);
      }
    };

    const deactivateUser = async (userId, username, isActive) => {
      const action = isActive ? "deactivate" : "activate";

      if (
        !confirm(
          `Are you sure you want to ${action} user "${username}"?${
            isActive ? " They will not be able to log in." : ""
          }`
        )
      ) {
        return;
      }

      try {
        const response = await AdminService.toggleUserActive(userId);

        // Update the local state
        const updateUserInList = (list) => {
          const userIndex = list.findIndex((user) => user.id === userId);
          if (userIndex !== -1) {
            list[userIndex].is_active = response.data.is_active;
          }
        };

        updateUserInList(doctors.value);
        updateUserInList(patients.value);

        const newStatus = response.data.is_active ? "activated" : "deactivated";
        alert(`User "${username}" has been ${newStatus} successfully.`);
      } catch (error) {
        console.error("Failed to toggle user status", error);
        const errorMsg =
          error.response?.data?.error || "Failed to update user status";
        alert(`Error: ${errorMsg}`);
      }
    };

    const handleUserCreated = () => {
      showCreateModal.value = false;
      loadDoctors();
      loadPatients();
    };

    const handleUserUpdated = () => {
      showEditModal.value = false;
      loadDoctors();
      loadPatients();
    };

    // Helper functions
    const formatDate = (dateString) => {
      if (!dateString) return "";
      const options = { year: "numeric", month: "short", day: "numeric" };
      return new Date(dateString).toLocaleDateString(undefined, options);
    };

    onMounted(() => {
      loadDoctors();
      loadPatients();
    });

    return {
      loadingDoctors,
      loadingPatients,
      doctors,
      patients,
      activeUserTab,
      searchTerm,
      showCreateModal,
      createUserType,
      showEditModal,
      editingUser,
      editingUserType,
      filteredDoctors,
      filteredPatients,
      editUser,
      resetPassword,
      deactivateUser,
      handleUserCreated,
      handleUserUpdated,
      formatDate,
    };
  },
};
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
