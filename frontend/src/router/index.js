import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

const routes = [
  { path: '/',        component: HomePage },
  { path: '/login',   component: LoginView },
  { path: '/register',component: RegisterView }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
