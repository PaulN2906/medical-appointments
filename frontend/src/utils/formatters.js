export const getDoctorName = (appointment) => {
  if (appointment?.doctor_details?.user) {
    const user = appointment.doctor_details.user;
    return `Dr. ${user.first_name} ${user.last_name}`;
  }
  return "Unknown Doctor";
};

export const getPatientName = (appointment) => {
  if (appointment?.patient_details?.user) {
    const user = appointment.patient_details.user;
    return `${user.first_name} ${user.last_name}`;
  }
  return "Unknown Patient";
};

export const formatDate = (
  dateString,
  options = { year: "numeric", month: "long", day: "numeric" }
) => {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString(undefined, options);
};

export const formatTime = (timeString) => {
  if (!timeString) return "";
  const timeParts = timeString.split(":");
  const date = new Date();
  date.setHours(parseInt(timeParts[0], 10));
  date.setMinutes(parseInt(timeParts[1], 10));
  return date.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  });
};

export const formatDateTime = (
  dateTimeString,
  options = {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }
) => {
  if (!dateTimeString) return "";
  return new Date(dateTimeString).toLocaleString(undefined, options);
};

export const getStatusClass = (status) => {
  const statusClasses = {
    pending: "badge bg-warning",
    confirmed: "badge bg-success",
    cancelled: "badge bg-danger",
    completed: "badge bg-info",
  };
  return statusClasses[status] || "badge bg-secondary";
};

export const isToday = (dateString) => {
  if (!dateString) return false;
  const appointmentDate = new Date(dateString + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  appointmentDate.setHours(0, 0, 0, 0);
  return appointmentDate.getTime() === today.getTime();
};

export const isPast = (dateString) => {
  if (!dateString) return false;
  const appointmentDate = new Date(dateString + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  appointmentDate.setHours(0, 0, 0, 0);
  return appointmentDate < today;
};

export const isUpcoming = (dateString) => {
  if (!dateString) return false;
  const appointmentDate = new Date(dateString + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  appointmentDate.setHours(0, 0, 0, 0);
  return appointmentDate >= today;
};

export const getDaysUntil = (dateString) => {
  if (!dateString) return "";
  const appointmentDate = new Date(dateString + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  appointmentDate.setHours(0, 0, 0, 0);
  const diffTime = appointmentDate - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Tomorrow";
  if (diffDays > 0) return `In ${diffDays} days`;
  return `${Math.abs(diffDays)} days ago`;
};
