import { createStore } from "vuex";
import auth from "./modules/auth";
import appointments from "./modules/appointments";
import doctors from "./modules/doctors";
import notifications from "./modules/notifications";

export default createStore({
  modules: {
    auth,
    appointments,
    doctors,
    notifications,
  },
});
