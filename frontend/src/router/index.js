import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PatientView from '../views/PatientView.vue'
import ProfileView from '../views/ProfileView.vue'
import ProcedureListPage from '../views/ProcedureListPage.vue'
import AllergyListPage from '../views/AllergyListPage.vue'
import ProcedimientoDetalle from '../views/ProcedimientoDetalle.vue'

const routes = [
  { path: '/',        component: HomePage },
  { path: '/login', name:'Login',  component: LoginView },
  { path: '/register',component: RegisterView },
  { 
    path: '/profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/patient/:patient_id',
    component: PatientView,
    props: true,
    meta: { requiresAuth: true }
  },
  { path: '/patient/:patient_id/procedimientos',
    component: ProcedureListPage,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/patient/:patient_id/alergias',
    component: AllergyListPage,
    props: true,
    meta: { requiresAuth: true }
  }
  , {
    path: '/patient/:patient_id/procedimientos/:procedure_id',
    component: ProcedimientoDetalle,
    props: true,
    meta: { requiresAuth: true }
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
