import api from "./api";

export default {
  getDoctors() {
    return api.get("doctors/doctors/");
  },

  getDoctorDetails(id) {
    return api.get(`doctors/doctors/${id}/`);
  },

  getSchedules(doctorId = null) {
    const url = doctorId
      ? `doctors/schedules/?doctor=${doctorId}`
      : "doctors/schedules/";
    return api.get(url);
  },

  createSchedule(scheduleData) {
    return api.post("doctors/schedules/", scheduleData);
  },

  updateSchedule(id, scheduleData) {
    return api.put(`doctors/schedules/${id}/`, scheduleData);
  },
};
