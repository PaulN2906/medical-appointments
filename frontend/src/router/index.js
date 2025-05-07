import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import DoctorDashboard from '../views/DoctorDashboard.vue'
import PatientDashboard from '../views/PatientDashboard.vue'
import AppointmentForm from '../views/AppointmentForm.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/doctor-dashboard',
    name: 'DoctorDashboard',
    component: DoctorDashboard,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/patient-dashboard',
    name: 'PatientDashboard',
    component: PatientDashboard,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/appointment-form',
    name: 'AppointmentForm',
    component: AppointmentForm,
    meta: { requiresAuth: true, role: 'patient' }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Guard pentru rute protejate
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token') !== null
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({ name: 'Login' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router;
