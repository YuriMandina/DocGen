// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import RolesView from '../views/RolesView.vue'

import EmployeesView from '../views/EmployeesView.vue'
import TemplatesView from '../views/TemplatesView.vue'
import GenerateView from '../views/GenerateView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/cargos' },
    { path: '/cargos', name: 'cargos', component: RolesView },
    { path: '/funcionarios', name: 'funcionarios', component: EmployeesView },
    { path: '/modelos', name: 'modelos', component: TemplatesView },
    { path: '/gerar', name: 'gerar', component: GenerateView }
  ]
})

export default router