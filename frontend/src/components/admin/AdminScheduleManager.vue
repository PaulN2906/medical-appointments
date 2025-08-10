<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Doctor Schedule Management</h5>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="bi bi-calendar-plus me-2"></i>
        Create Schedule
      </button>
    </div>

    <div class="card-body">
      <!-- Doctor filter -->
      <div class="row mb-3">
        <div class="col-md-6">
          <select class="form-select" v-model="selectedDoctor">
            <option value="">All Doctors</option>
            <option
              v-for="doctor in doctors"
              :key="doctor.id"
              :value="doctor.id"
            >
              Dr. {{ doctor.user.last_name }} {{ doctor.user.first_name }} -
              {{ doctor.speciality }}
            </option>
          </select>
        </div>
      </div>

      <!-- Schedule list -->
      <div v-if="loading" class="text-center p-4">
        <LoadingSpinner />
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Doctor</th>
              <th>Date</th>
              <th>Time</th>
              <th>Available</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="schedule in filteredSchedules" :key="schedule.id">
              <td>{{ schedule.doctor_name }}</td>
              <td>{{ formatDate(schedule.date) }}</td>
              <td>
                {{ formatTime(schedule.start_time) }} -
                {{ formatTime(schedule.end_time) }}
              </td>
              <td>
                <span
                  :class="
                    schedule.is_available
                      ? 'badge bg-success'
                      : 'badge bg-danger'
                  "
                >
                  {{ schedule.is_available ? "Available" : "Booked" }}
                </span>
              </td>
              <td>
                <button
                  class="btn btn-sm btn-outline-danger"
                  @click="deleteSchedule(schedule.id)"
                  v-if="schedule.is_available"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Schedule Modal -->
    <div
      class="modal fade"
      :class="{ show: showCreateModal }"
      :style="{ display: showCreateModal ? 'block' : 'none' }"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Schedule for Doctor</h5>
            <button
              type="button"
              class="btn-close"
              @click="showCreateModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createSchedule">
              <div class="mb-3">
                <label class="form-label">Doctor *</label>
                <select
                  class="form-select"
                  v-model="scheduleForm.doctor"
                  required
                >
                  <option value="">Select doctor...</option>
                  <option
                    v-for="doctor in doctors"
                    :key="doctor.id"
                    :value="doctor.id"
                  >
                    Dr. {{ doctor.user.last_name }}
                    {{ doctor.user.first_name }} - {{ doctor.speciality }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Date *</label>
                <input
                  type="date"
                  class="form-control"
                  v-model="scheduleForm.date"
                  required
                />
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Start Time *</label>
                  <input
                    type="time"
                    class="form-control"
                    v-model="scheduleForm.start_time"
                    required
                  />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">End Time *</label>
                  <input
                    type="time"
                    class="form-control"
                    v-model="scheduleForm.end_time"
                    required
                  />
                </div>
              </div>

              <div v-if="scheduleError" class="alert alert-danger">
                {{ scheduleError }}
              </div>

              <div class="text-end">
                <button
                  type="button"
                  class="btn btn-secondary me-2"
                  @click="showCreateModal = false"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="creatingSchedule"
                >
                  <LoadingSpinner
                    v-if="creatingSchedule"
                    size="sm"
                    class="me-2"
                  />
                  Create Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showCreateModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from "vue";
import AdminService from "@/services/admin.service";

export default {
  name: "AdminScheduleManager",

  setup() {
    const loading = ref(true);
    const creatingSchedule = ref(false);
    const showCreateModal = ref(false);
    const scheduleError = ref("");

    const doctors = ref([]);
    const schedules = ref([]);
    const selectedDoctor = ref("");

    const scheduleForm = reactive({
      doctor: "",
      date: "",
      start_time: "",
      end_time: "",
    });

    const filteredSchedules = computed(() => {
      if (!selectedDoctor.value) return schedules.value;
      return schedules.value.filter(
        (schedule) => schedule.doctor === parseInt(selectedDoctor.value)
      );
    });

    const loadData = async () => {
      try {
        const [usersResponse, schedulesResponse] = await Promise.all([
          AdminService.getAllUsers(),
          AdminService.getAllSchedules(),
        ]);

        const data = usersResponse.data.results || [];
        doctors.value = data
          .filter((u) => u.role === "doctor")
          .map((u) => ({
            id: u.id,
            speciality: u.speciality,
            user: {
              id: u.id,
              first_name: u.first_name,
              last_name: u.last_name,
              email: u.email,
            },
          }));
        schedules.value = schedulesResponse.data;
      } catch (error) {
        console.error("Failed to load schedule data", error);
      } finally {
        loading.value = false;
      }
    };

    const createSchedule = async () => {
      creatingSchedule.value = true;
      scheduleError.value = "";

      try {
        const scheduleData = {
          doctor: scheduleForm.doctor,
          date: scheduleForm.date,
          start_time: scheduleForm.start_time + ":00",
          end_time: scheduleForm.end_time + ":00",
          is_available: true,
        };

        await AdminService.createScheduleForDoctor(scheduleData);

        showCreateModal.value = false;
        resetForm();
        await loadData();
      } catch (error) {
        console.error("Failed to create schedule", error);
        scheduleError.value =
          error.response?.data?.error || "Failed to create schedule";
      } finally {
        creatingSchedule.value = false;
      }
    };

    const deleteSchedule = async (scheduleId) => {
      // Confirma stergerea
      if (
        !confirm(
          "Are you sure you want to delete this schedule? This action cannot be undone."
        )
      ) {
        return;
      }

      try {
        // Apeleaza endpoint-ul pentru stergerea programului
        await AdminService.deleteSchedule(scheduleId);

        // Actualizeaza lista locala eliminand programul sters
        schedules.value = schedules.value.filter(
          (schedule) => schedule.id !== scheduleId
        );

        console.log(`Schedule ${scheduleId} deleted successfully`);
      } catch (error) {
        console.error("Failed to delete schedule", error);

        // Afiseaza eroarea pentru utilizator
        const errorMessage =
          error.response?.data?.error ||
          "Failed to delete schedule. Please try again.";
        alert(errorMessage);
      }
    };

    const resetForm = () => {
      Object.keys(scheduleForm).forEach((key) => (scheduleForm[key] = ""));
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString();
    };

    const formatTime = (timeString) => {
      return timeString.slice(0, 5);
    };

    onMounted(() => {
      loadData();
    });

    return {
      loading,
      creatingSchedule,
      showCreateModal,
      scheduleError,
      doctors,
      schedules,
      selectedDoctor,
      scheduleForm,
      filteredSchedules,
      createSchedule,
      deleteSchedule,
      formatDate,
      formatTime,
    };
  },
};
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
