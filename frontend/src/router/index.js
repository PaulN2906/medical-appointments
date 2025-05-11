import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import DoctorDashboard from "../views/DoctorDashboard.vue";
import PatientDashboard from "../views/PatientDashboard.vue";
import BookAppointment from "../views/BookAppointment.vue";
import AppointmentDetails from "../views/AppointmentDetails.vue";
import Profile from "../views/Profile.vue";
import AppointmentConfirmation from "../views/AppointmentConfirmation.vue";
import AuthService from "@/services/auth.service";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: { requiresGuest: true },
  },
  {
    path: "/register",
    name: "Register",
    component: Register,
    meta: { requiresGuest: true },
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: PatientDashboard, // Determina tipul de dashboard in functie de rol
    meta: { requiresAuth: true },
  },
  {
    path: "/doctor-dashboard",
    name: "DoctorDashboard",
    component: DoctorDashboard,
    meta: { requiresAuth: true, role: "doctor" },
  },
  {
    path: "/appointments",
    name: "Appointments",
    component: () => import("../views/Appointments.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/appointments/:id",
    name: "AppointmentDetails",
    component: AppointmentDetails,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: "/book-appointment",
    name: "BookAppointment",
    component: BookAppointment,
    meta: { requiresAuth: true, role: "patient" },
  },
  {
    path: "/appointment-confirmation",
    name: "AppointmentConfirmation",
    component: AppointmentConfirmation,
    meta: { requiresAuth: true },
  },
  {
    path: "/profile",
    name: "Profile",
    component: Profile,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// Navigatie guard pentru a verifica autentificarea si rolurile
router.beforeEach((to, from, next) => {
  const isAuthenticated = AuthService.isLoggedIn();

  // Verifica daca ruta necesita autentificare
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({ name: "Login" });
    } else {
      // Verifica rolul utilizatorului daca este specificat in meta
      const user = AuthService.getUser();
      if (to.meta.role && user.role !== to.meta.role) {
        next({ name: "Dashboard" }); // Redirectioneaza la dashboard-ul potrivit
      } else {
        next();
      }
    }
  }
  // Verifica daca ruta este doar pentru vizitatori (neautentificati)
  else if (to.matched.some((record) => record.meta.requiresGuest)) {
    if (isAuthenticated) {
      next({ name: "Dashboard" });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
