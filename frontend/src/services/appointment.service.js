import api from "./api";

export default {
  getAppointments() {
    return api.get("appointments/appointments/");
  },

  createAppointment(appointmentData) {
    return api.post("appointments/appointments/", appointmentData);
  },

  confirmAppointment(id) {
    return api.post(`appointments/appointments/${id}/confirm/`);
  },

  cancelAppointment(id) {
    return api.post(`appointments/appointments/${id}/cancel/`);
  },

  getAppointmentDetails(id) {
    return api.get(`appointments/appointments/${id}/`);
  },
};
