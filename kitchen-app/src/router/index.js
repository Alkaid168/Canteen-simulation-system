import { createRouter, createWebHistory } from 'vue-router'
import WindowSelectView from '../views/WindowSelectView.vue'
import OrderListView from '../views/OrderListView.vue'

const routes = [
  {
    path: '/',
    name: 'WindowSelect',
    component: WindowSelectView
  },
  {
    path: '/orders/:windowId',
    name: 'OrderList',
    component: OrderListView,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
