import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import MainLayout from '../views/MainLayout.vue'
import DishesView from '../views/DishesView.vue'
import WindowsView from '../views/WindowsView.vue'
import SeatGroupsView from '../views/SeatGroupsView.vue'
import SeatsView from '../views/SeatsView.vue'
import StudentsView from '../views/StudentsView.vue'
import PredictionView from '../views/PredictionView.vue'
import ReportsView from '../views/ReportsView.vue'
import ConfigView from '../views/ConfigView.vue'

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
    path: '/admin',
    component: MainLayout,
    children: [
      {
        path: 'dishes',
        name: 'Dishes',
        component: DishesView
      },
      {
        path: 'windows',
        name: 'Windows',
        component: WindowsView
      },
      {
        path: 'seat-groups',
        name: 'SeatGroups',
        component: SeatGroupsView
      },
      {
        path: 'seats',
        name: 'Seats',
        component: SeatsView
      },
      {
        path: 'students',
        name: 'Students',
        component: StudentsView
      },
      {
        path: 'prediction',
        name: 'Prediction',
        component: PredictionView
      },
      {
        path: 'reports',
        name: 'Reports',
        component: ReportsView
      },
      {
        path: 'config',
        name: 'Config',
        component: ConfigView
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
