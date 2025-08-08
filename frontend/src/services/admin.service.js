import api from "./api";

export default {
  // Dashboard stats
  getDashboardStats() {
    return api.get("appointments/admin_stats/");
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
    return api.post("appointments/", appointmentData);
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

  deleteSchedule(scheduleId) {
    return api.delete(`doctors/schedules/${scheduleId}/`);
  },

  // User management methods
  getAllUsers() {
    return api.get("auth/users/admin/all/");
  },

  updateUser(userId, userData) {
    return api.put(`auth/users/${userId}/admin/update/`, userData);
  },

  resetUserPassword(userId) {
    return api.post(`auth/users/${userId}/admin/reset-password/`);
  },

  toggleUserActive(userId) {
    return api.post(`auth/users/${userId}/admin/toggle-active/`);
  },
};
