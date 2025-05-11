import AppointmentService from "@/services/appointment.service";

export default {
  namespaced: true,

  state: {
    appointments: [],
    loading: false,
    error: null,
  },

  mutations: {
    setAppointments(state, appointments) {
      state.appointments = appointments;
    },
    setLoading(state, loading) {
      state.loading = loading;
    },
    setError(state, error) {
      state.error = error;
    },
    addAppointment(state, appointment) {
      state.appointments.push(appointment);
    },
    updateAppointment(state, updatedAppointment) {
      const index = state.appointments.findIndex(
        (a) => a.id === updatedAppointment.id
      );
      if (index !== -1) {
        state.appointments.splice(index, 1, updatedAppointment);
      }
    },
  },

  actions: {
    async fetchAppointments({ commit }) {
      commit("setLoading", true);
      commit("setError", null);

      try {
        const response = await AppointmentService.getAppointments();
        commit("setAppointments", response.data);
      } catch (error) {
        commit(
          "setError",
          error.response?.data?.error || "Failed to load appointments"
        );
        console.error("Error fetching appointments:", error);
      } finally {
        commit("setLoading", false);
      }
    },

    async createAppointment({ commit }, appointmentData) {
      commit("setLoading", true);
      commit("setError", null);

      try {
        const response = await AppointmentService.createAppointment(
          appointmentData
        );
        commit("addAppointment", response.data);
        return { success: true, appointment: response.data };
      } catch (error) {
        commit(
          "setError",
          error.response?.data?.error || "Failed to create appointment"
        );
        console.error("Error creating appointment:", error);
        return {
          success: false,
          error: error.response?.data?.error || "Failed to create appointment",
        };
      } finally {
        commit("setLoading", false);
      }
    },

    async confirmAppointment({ commit }, appointmentId) {
      commit("setLoading", true);
      commit("setError", null);

      try {
        const response = await AppointmentService.confirmAppointment(
          appointmentId
        );
        const updatedAppointment = { ...response.data, status: "confirmed" };
        commit("updateAppointment", updatedAppointment);
        return { success: true };
      } catch (error) {
        commit(
          "setError",
          error.response?.data?.error || "Failed to confirm appointment"
        );
        console.error("Error confirming appointment:", error);
        return {
          success: false,
          error: error.response?.data?.error || "Failed to confirm appointment",
        };
      } finally {
        commit("setLoading", false);
      }
    },

    async cancelAppointment({ commit }, appointmentId) {
      commit("setLoading", true);
      commit("setError", null);

      try {
        const response = await AppointmentService.cancelAppointment(
          appointmentId
        );
        const updatedAppointment = { ...response.data, status: "cancelled" };
        commit("updateAppointment", updatedAppointment);
        return { success: true };
      } catch (error) {
        commit(
          "setError",
          error.response?.data?.error || "Failed to cancel appointment"
        );
        console.error("Error cancelling appointment:", error);
        return {
          success: false,
          error: error.response?.data?.error || "Failed to cancel appointment",
        };
      } finally {
        commit("setLoading", false);
      }
    },
  },

  getters: {
    allAppointments: (state) => state.appointments,
    appointmentById: (state) => (id) =>
      state.appointments.find((a) => a.id === id),
    appointmentsByStatus: (state) => (status) =>
      state.appointments.filter((a) => a.status === status),
    isLoading: (state) => state.loading,
    hasError: (state) => !!state.error,
    errorMessage: (state) => state.error,
  },
};
