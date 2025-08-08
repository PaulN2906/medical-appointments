<template>
  <div>
    <!-- Header cu actions -->
    <div class="row mb-4">
      <div class="col-md-8">
        <h5>Appointments Management</h5>
        <p class="text-muted mb-0">
          View and manage all appointments in the system
        </p>
      </div>
      <div class="col-md-4 text-end">
        <button class="btn btn-primary" @click="showCreateModal = true">
          <i class="bi bi-calendar-plus me-2"></i>
          Create Appointment
        </button>
      </div>
    </div>

    <!-- Schedule management -->
    <div class="row mb-3">
      <div class="col-md-12">
        <ul class="nav nav-pills">
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: subTab === 'appointments' }"
              href="#"
              @click.prevent="subTab = 'appointments'"
            >
              <i class="bi bi-calendar-check me-2"></i>Appointments
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ active: subTab === 'schedules' }"
              href="#"
              @click.prevent="subTab = 'schedules'"
            >
              <i class="bi bi-calendar-plus me-2"></i>Doctor Schedules
            </a>
          </li>
        </ul>
      </div>
    </div>

    <!-- Modifica continutul sa fie conditional -->
    <div v-if="subTab === 'appointments'">
      <!-- Existing appointments content -->
    </div>

    <div v-if="subTab === 'schedules'">
      <AdminScheduleManager />
    </div>

    <!-- Filter si Search -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input
            type="text"
            class="form-control"
            placeholder="Search by patient or doctor name..."
            v-model="searchTerm"
          />
        </div>
      </div>
      <div class="col-md-3">
        <select class="form-select" v-model="statusFilter">
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="confirmed">Confirmed</option>
          <option value="cancelled">Cancelled</option>
          <option value="completed">Completed</option>
        </select>
      </div>
      <div class="col-md-3">
        <input
          type="date"
          class="form-control"
          v-model="dateFilter"
          title="Filter by date"
        />
      </div>
    </div>

    <!-- Appointments Table -->
    <div class="card">
      <div
        class="card-header d-flex justify-content-between align-items-center"
      >
        <span>All Appointments ({{ filteredAppointments.length }})</span>
        <div class="btn-group btn-group-sm">
          <button
            class="btn"
            :class="
              viewMode === 'table' ? 'btn-primary' : 'btn-outline-primary'
            "
            @click="viewMode = 'table'"
          >
            <i class="bi bi-table"></i> Table
          </button>
          <button
            class="btn"
            :class="
              viewMode === 'cards' ? 'btn-primary' : 'btn-outline-primary'
            "
            @click="viewMode = 'cards'"
          >
            <i class="bi bi-grid"></i> Cards
          </button>
        </div>
      </div>

      <div class="card-body">
        <div v-if="loading" class="text-center p-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div
          v-else-if="filteredAppointments.length === 0"
          class="text-center p-4"
        >
          <i class="bi bi-calendar-x fs-1 text-muted"></i>
          <p class="mt-2">No appointments found matching your criteria.</p>
        </div>

        <!-- Table View -->
        <div v-else-if="viewMode === 'table'" class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Date & Time</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="appointment in paginatedAppointments"
                :key="appointment.id"
              >
                <td>{{ appointment.id }}</td>
                <td>{{ getPatientName(appointment) }}</td>
                <td>{{ getDoctorName(appointment) }}</td>
                <td>
                  <div>
                    {{
                      formatDate(appointment.schedule_details?.date, {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })
                    }}
                  </div>
                  <small class="text-muted">
                    {{ formatTime(appointment.schedule_details?.start_time) }} -
                    {{ formatTime(appointment.schedule_details?.end_time) }}
                  </small>
                </td>
                <td>
                  <span :class="getStatusClass(appointment.status)">
                    {{ appointment.status }}
                  </span>
                </td>
                <td>
                  <small>
                    {{
                      formatDateTime(appointment.created_at, {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })
                    }}
                  </small>
                </td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button
                      v-if="appointment.status === 'pending'"
                      @click="confirmAppointment(appointment.id)"
                      class="btn btn-outline-success"
                      title="Confirm"
                    >
                      <i class="bi bi-check"></i>
                    </button>
                    <button
                      v-if="
                        ['pending', 'confirmed'].includes(appointment.status)
                      "
                      @click="cancelAppointment(appointment.id)"
                      class="btn btn-outline-danger"
                      title="Cancel"
                    >
                      <i class="bi bi-x"></i>
                    </button>
                    <button
                      @click="viewAppointment(appointment.id)"
                      class="btn btn-outline-info"
                      title="View Details"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Cards View -->
        <div v-else class="row">
          <div
            class="col-md-6 col-lg-4 mb-3"
            v-for="appointment in paginatedAppointments"
            :key="appointment.id"
          >
            <div class="card h-100">
              <div class="card-body">
                <div
                  class="d-flex justify-content-between align-items-start mb-2"
                >
                  <h6 class="card-title mb-0"># {{ appointment.id }}</h6>
                  <span :class="getStatusClass(appointment.status)">
                    {{ appointment.status }}
                  </span>
                </div>

                <p class="card-text">
                  <strong>Patient:</strong> {{ getPatientName(appointment)
                  }}<br />
                  <strong>Doctor:</strong> {{ getDoctorName(appointment)
                  }}<br />
                  <strong>Date:</strong>
                  {{
                    formatDate(appointment.schedule_details?.date, {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                    })
                  }}<br />
                  <strong>Time:</strong>
                  {{ formatTime(appointment.schedule_details?.start_time) }}
                </p>

                <div class="btn-group btn-group-sm w-100">
                  <button
                    v-if="appointment.status === 'pending'"
                    @click="confirmAppointment(appointment.id)"
                    class="btn btn-success"
                  >
                    <i class="bi bi-check me-1"></i>Confirm
                  </button>
                  <button
                    v-if="['pending', 'confirmed'].includes(appointment.status)"
                    @click="cancelAppointment(appointment.id)"
                    class="btn btn-danger"
                  >
                    <i class="bi bi-x me-1"></i>Cancel
                  </button>
                  <button
                    @click="viewAppointment(appointment.id)"
                    class="btn btn-info"
                  >
                    <i class="bi bi-eye me-1"></i>View
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="d-flex justify-content-center mt-4">
          <nav>
            <ul class="pagination">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" href="#" @click.prevent="currentPage = 1"
                  >First</a
                >
              </li>
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" href="#" @click.prevent="currentPage--"
                  >Previous</a
                >
              </li>
              <li
                class="page-item"
                :class="{ active: currentPage === page }"
                v-for="page in visiblePages"
                :key="page"
              >
                <a
                  class="page-link"
                  href="#"
                  @click.prevent="currentPage = page"
                  >{{ page }}</a
                >
              </li>
              <li
                class="page-item"
                :class="{ disabled: currentPage === totalPages }"
              >
                <a class="page-link" href="#" @click.prevent="currentPage++"
                  >Next</a
                >
              </li>
              <li
                class="page-item"
                :class="{ disabled: currentPage === totalPages }"
              >
                <a
                  class="page-link"
                  href="#"
                  @click.prevent="currentPage = totalPages"
                  >Last</a
                >
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- Create Appointment Modal -->
    <div
      class="modal fade"
      :class="{ show: showCreateModal }"
      :style="{ display: showCreateModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create New Appointment</h5>
            <button
              type="button"
              class="btn-close"
              @click="showCreateModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <AdminCreateAppointment @created="handleAppointmentCreated" />
          </div>
        </div>
      </div>
    </div>
    <div v-if="showCreateModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import AppointmentService from "@/services/appointment.service";
import AdminCreateAppointment from "./AdminCreateAppointment.vue";
import AdminScheduleManager from "./AdminScheduleManager.vue";
import {
  getDoctorName,
  getPatientName,
  formatDate,
  formatTime,
  formatDateTime,
  getStatusClass,
} from "@/utils/formatters";

export default {
  name: "AdminAppointments",
  components: {
    AdminCreateAppointment,
    AdminScheduleManager,
  },

  setup() {
    const router = useRouter();
    const loading = ref(true);
    const appointments = ref([]);
    const searchTerm = ref("");
    const statusFilter = ref("");
    const dateFilter = ref("");
    const viewMode = ref("table");
    const showCreateModal = ref(false);
    const subTab = ref("appointments");

    // Pagination
    const currentPage = ref(1);
    const itemsPerPage = 10;

    const loadAppointments = async () => {
      try {
        const response = await AppointmentService.getAppointments();
        appointments.value = response.data;
        console.log(`Loaded ${response.data.length} appointments for admin`);
      } catch (error) {
        console.error("Failed to load appointments", error);
      } finally {
        loading.value = false;
      }
    };

    // Computed filters
    const filteredAppointments = computed(() => {
      let filtered = appointments.value;

      // Search filter
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase();
        filtered = filtered.filter((appointment) => {
          const patientName = getPatientName(appointment).toLowerCase();
          const doctorName = getDoctorName(appointment).toLowerCase();
          return patientName.includes(term) || doctorName.includes(term);
        });
      }

      // Status filter
      if (statusFilter.value) {
        filtered = filtered.filter(
          (appointment) => appointment.status === statusFilter.value
        );
      }

      // Date filter
      if (dateFilter.value) {
        filtered = filtered.filter(
          (appointment) =>
            appointment.schedule_details?.date === dateFilter.value
        );
      }

      return filtered.sort(
        (a, b) => new Date(b.created_at) - new Date(a.created_at)
      );
    });

    // Pagination computed
    const totalPages = computed(() =>
      Math.ceil(filteredAppointments.value.length / itemsPerPage)
    );

    const paginatedAppointments = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      const end = start + itemsPerPage;
      return filteredAppointments.value.slice(start, end);
    });

    const visiblePages = computed(() => {
      const pages = [];
      const start = Math.max(1, currentPage.value - 2);
      const end = Math.min(totalPages.value, currentPage.value + 2);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    });

    // Watch for filter changes to reset pagination
    watch([searchTerm, statusFilter, dateFilter], () => {
      currentPage.value = 1;
    });

    // Actions
    const confirmAppointment = async (appointmentId) => {
      try {
        await AppointmentService.confirmAppointment(appointmentId);
        await loadAppointments(); // Refresh data
      } catch (error) {
        console.error("Failed to confirm appointment", error);
        alert("Failed to confirm appointment");
      }
    };

    const cancelAppointment = async (appointmentId) => {
      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      try {
        await AppointmentService.cancelAppointment(appointmentId);
        await loadAppointments(); // Refresh data
      } catch (error) {
        console.error("Failed to cancel appointment", error);
        alert("Failed to cancel appointment");
      }
    };

    const viewAppointment = (appointmentId) => {
      router.push(`/appointments/${appointmentId}`);
    };

    const handleAppointmentCreated = () => {
      showCreateModal.value = false;
      loadAppointments(); // Refresh data
    };

    onMounted(() => {
      loadAppointments();
    });

    return {
      loading,
      appointments,
      searchTerm,
      statusFilter,
      dateFilter,
      viewMode,
      showCreateModal,
      currentPage,
      filteredAppointments,
      paginatedAppointments,
      totalPages,
      visiblePages,
      confirmAppointment,
      cancelAppointment,
      viewAppointment,
      handleAppointmentCreated,
      getPatientName,
      getDoctorName,
      formatDate,
      formatTime,
      formatDateTime,
      getStatusClass,
      subTab,
    };
  },
};
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
