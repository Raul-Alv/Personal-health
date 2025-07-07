import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PatientView from '../views/PatientView.vue'
import ProfileView from '../views/ProfileView.vue'

const routes = [
  { path: '/',        component: HomePage },
  { path: '/login',   component: LoginView },
  { path: '/register',component: RegisterView },
  { path: '/profile', component: ProfileView },
  {
    path: '/patient/:patient_id',
    component: PatientView,
    props: true
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
