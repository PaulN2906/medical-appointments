import DoctorService from "@/services/doctor.service";

export default {
  namespaced: true,

  state: {
    doctors: [],
    schedules: [],
    loading: false,
    error: null,
  },

  mutations: {
    setDoctors(state, doctors) {
      state.doctors = doctors;
    },
    setSchedules(state, schedules) {
      state.schedules = schedules;
    },
    setLoading(state, loading) {
      state.loading = loading;
    },
    setError(state, error) {
      state.error = error;
    },
    addSchedule(state, schedule) {
      state.schedules.push(schedule);
    },
    updateSchedule(state, updatedSchedule) {
      const index = state.schedules.findIndex(
        (s) => s.id === updatedSchedule.id
      );
      if (index !== -1) {
        state.schedules.splice(index, 1, updatedSchedule);
      }
    },
  },

  actions: {
    async fetchDoctors({ commit }) {
      commit("setLoading", true);
      commit("setError", null);

      try {
        const response = await DoctorService.getDoctors();
        commit("setDoctors", response.data);
      } catch (error) {
        commit(
          "setError",
          error.response?.data?.error || "Failed to load doctors"
        );
        console.error("Error fetching doctors:", error);
      } finally {
        commit("setLoading", false);
      }
    },

    async fetchSchedules({ commit }, doctorId = null) {
      commit("setLoading", true);
      commit("setError", null);

      try {
        const response = await DoctorService.getSchedules(doctorId);
        commit("setSchedules", response.data);
      } catch (error) {
        commit(
          "setError",
          error.response?.data?.error || "Failed to load schedules"
        );
        console.error("Error fetching schedules:", error);
      } finally {
        commit("setLoading", false);
      }
    },

    async createSchedule({ commit }, scheduleData) {
      commit("setLoading", true);
      commit("setError", null);

      try {
        const response = await DoctorService.createSchedule(scheduleData);
        commit("addSchedule", response.data);
        return { success: true, schedule: response.data };
      } catch (error) {
        commit(
          "setError",
          error.response?.data?.error || "Failed to create schedule"
        );
        console.error("Error creating schedule:", error);
        return {
          success: false,
          error: error.response?.data?.error || "Failed to create schedule",
        };
      } finally {
        commit("setLoading", false);
      }
    },

    async updateSchedule({ commit }, { id, scheduleData }) {
      commit("setLoading", true);
      commit("setError", null);

      try {
        const response = await DoctorService.updateSchedule(id, scheduleData);
        commit("updateSchedule", response.data);
        return { success: true, schedule: response.data };
      } catch (error) {
        commit(
          "setError",
          error.response?.data?.error || "Failed to update schedule"
        );
        console.error("Error updating schedule:", error);
        return {
          success: false,
          error: error.response?.data?.error || "Failed to update schedule",
        };
      } finally {
        commit("setLoading", false);
      }
    },
  },

  getters: {
    allDoctors: (state) => state.doctors,
    doctorById: (state) => (id) => state.doctors.find((d) => d.id === id),
    allSchedules: (state) => state.schedules,
    availableSchedules: (state) =>
      state.schedules.filter((s) => s.is_available),
    scheduleById: (state) => (id) => state.schedules.find((s) => s.id === id),
    isLoading: (state) => state.loading,
    hasError: (state) => !!state.error,
    errorMessage: (state) => state.error,
  },
};
