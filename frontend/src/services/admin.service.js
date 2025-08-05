import api from "./api";

export default {
  // Dashboard stats
  getDashboardStats() {
    return api.get("appointments/appointments/admin_stats/");
  },

  // Users management
  getAllDoctors() {
    return api.get("doctors/doctors/");
  },

  getAllPatients() {
    return api.get("patients/patients/");
  },

  // Quick appointment booking pentru admin
  createAppointmentAsAdmin(appointmentData) {
    return api.post("appointments/appointments/", appointmentData);
  },

  // User creation
  createUser(userData) {
    return api.post("auth/users/register/", userData);
  },

  // Schedule management
  getAllSchedules() {
    return api.get("doctors/schedules/");
  },

  createScheduleForDoctor(scheduleData) {
    return api.post("doctors/schedules/", scheduleData);
  },

  bulkCreateSchedules(schedules) {
    return api.post("doctors/schedules/bulk_create/", schedules);
  },
};
