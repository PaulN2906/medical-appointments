import api from "./api";

export default {
  getAppointments() {
    return api.get("appointments/");
  },

  createAppointment(appointmentData) {
    return api.post("appointments/", appointmentData);
  },

  confirmAppointment(id) {
    return api.post(`appointments/${id}/confirm/`);
  },

  cancelAppointment(id) {
    return api.post(`appointments/${id}/cancel/`);
  },

  getAppointmentDetails(id) {
    return api.get(`appointments/${id}/`);
  },
};
