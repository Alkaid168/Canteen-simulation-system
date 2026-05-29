import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import PartySizeView from '../views/PartySizeView.vue'
import MenuView from '../views/MenuView.vue'
import OrderResultView from '../views/OrderResultView.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/party-size',
    name: 'PartySize',
    component: PartySizeView
  },
  {
    path: '/menu',
    name: 'Menu',
    component: MenuView
  },
  {
    path: '/order-result',
    name: 'OrderResult',
    component: OrderResultView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
