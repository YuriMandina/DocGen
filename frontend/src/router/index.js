// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import RolesView from '../views/RolesView.vue'
import EmployeesView from '../views/EmployeesView.vue'
import TemplatesView from '../views/TemplatesView.vue'
import GenerateView from '../views/GenerateView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import SettingsView from '../views/SettingsView.vue'

const routes = [
  { path: '/', redirect: '/cargos' },
  { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
  { path: '/registro', name: 'registro', component: RegisterView, meta: { public: true } },
  
  // Rotas Protegidas
  { path: '/cargos', name: 'cargos', component: RolesView, meta: { requiresAuth: true } },
  { path: '/funcionarios', name: 'funcionarios', component: EmployeesView, meta: { requiresAuth: true } },
  { path: '/modelos', name: 'modelos', component: TemplatesView, meta: { requiresAuth: true } },
  { path: '/gerar', name: 'gerar', component: GenerateView, meta: { requiresAuth: true } },
  { path: '/configuracoes', name: 'configuracoes', component: SettingsView, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Proteção de Rotas (Guardião)
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('@DocGen:token');
  const user = JSON.parse(localStorage.getItem('@DocGen:user') || '{}');

  if (to.meta.requiresAuth && !token) {
    next({ name: 'login' });
  } else if (to.meta.requiresMaster && !user.is_master) {
    next({ name: 'cargos' }); // Bloqueia quem não é Master de ver aprovações
  } else if (to.meta.public && token) {
    next({ name: 'cargos' }); // Se já está logado, não deixa ir pra tela de login
  } else {
    next();
  }
})

export default router