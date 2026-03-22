import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PatientView from '../views/PatientView.vue'
import ProfileView from '../views/ProfileView.vue'
import ProcedureListPage from '../views/ProcedureListPage.vue'
import AllergyListPage from '../views/AllergyListPage.vue'
import ProcedureDetail from '../views/ProcedureDetail.vue'
import ExportView from '../views/ExportView.vue'
import ImportView from '../views/ImportView.vue'

const routes = [
  { path: '/', component: HomePage },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/patient/:patient_id',
    name: 'Patient',
    component: PatientView,
    props: true,
    meta: { requiresAuth: true, requiresMenu: true }
  },
  {
    path: '/patient/:patient_id/procedimientos',
    name: 'ProcedureList',
    component: ProcedureListPage,
    props: true,
    meta: { requiresAuth: true, requiresMenu: true }
  },
  {
    path: '/patient/:patient_id/alergias',
    name: 'AllergyList',
    component: AllergyListPage,
    props: true,
    meta: { requiresAuth: true, requiresMenu: true }
  },
  {
    path: '/patient/:patient_id/procedimientos/:procedure_id',
    name: 'ProcedureDetail',
    component: ProcedureDetail,
    props: true,
    meta: { requiresAuth: true, requiresMenu: true }
  },
  {
    path: '/export',
    name: 'Export',
    component: ExportView,
    props: true,
    meta: { requiresAuth: true, requiresMenu: true }
  },
  {
    path: '/import',
    name: 'Import',
    component: ImportView,
    props: true,
    meta: { requiresAuth: true, requiresMenu: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

function hasValidToken() {
  const token = localStorage.getItem('token')
  return !!token && token !== 'undefined' && token !== 'null' && token.trim() !== ''
}

router.beforeEach((to, from, next) => {
  const isAuthenticated = hasValidToken()

  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next({ name: 'Login' })
    return
  }

  if ((to.name === 'Login' || to.name === 'Register') && isAuthenticated) {
    next({ name: 'Profile' })
    return
  }

  next()
})

export default router