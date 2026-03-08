<template>
  <div class="app-container">
    <header class="glass-header" v-if="isLoggedIn">
      <div class="header-content flex-between">
        <div>
          <h1>📑 DocGen</h1>
          <p class="text-muted" style="margin: 0; font-size: 0.85rem;">
            Olá, <strong>{{ currentUser.full_name }}</strong> 
            <span v-if="currentUser.is_master" class="badge-master">👑 Master</span>
          </p>
        </div>
        
        <div class="nav-wrapper">
          <nav class="main-nav">
            <router-link to="/cargos">🏢 Cargos</router-link>
            <router-link to="/funcionarios">👥 Funcionários</router-link>
            <router-link to="/modelos">📄 Modelos</router-link>       
            <router-link to="/gerar">🖨️ Gerar</router-link> 
            <router-link v-if="currentUser.is_master" to="/aprovacoes" class="master-link">🛡️ Aprovações</router-link> 
          </nav>
          <button @click="logout" class="btn-logout" title="Sair do sistema">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
          </button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade-slide" mode="out-in">
          <component :is="Component" @login-success="atualizarSessao" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoggedIn = ref(false);
const currentUser = ref({});

const atualizarSessao = () => {
  const token = localStorage.getItem('@DocGen:token');
  const user = localStorage.getItem('@DocGen:user');
  
  if (token && user) {
    isLoggedIn.value = true;
    currentUser.value = JSON.parse(user);
  } else {
    isLoggedIn.value = false;
    currentUser.value = {};
  }
};

const logout = () => {
  localStorage.removeItem('@DocGen:token');
  localStorage.removeItem('@DocGen:user');
  atualizarSessao();
  router.push('/login');
};

// Verifica a sessão quando o app carrega
onMounted(() => {
  atualizarSessao();
});
</script>

<style>
/* Importando a fonte Inter do Google */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Variáveis CSS para manter o padrão de cores */
:root {
  --primary: #4f46e5;      /* Azul índigo moderno */
  --primary-hover: #4338ca;
  --secondary: #10b981;    /* Verde sucesso */
  --secondary-hover: #059669;
  --bg-color: #f8fafc;     /* Fundo cinza super claro */
  --surface: #ffffff;      /* Fundo dos cartões */
  --text-main: #0f172a;
  --text-muted: #64748b;
  --border: #e2e8f0;
}

body {
  font-family: 'Inter', sans-serif;
  margin: 0;
  padding: 0;
  background-color: var(--bg-color);
  color: var(--text-main);
  -webkit-font-smoothing: antialiased;
}

.app-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

/* Efeito "Glassmorphism" no cabeçalho */
.glass-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 20px;
  z-index: 100;
}

.header-content h1 {
  margin: 0 0 15px 0;
  font-size: 1.8rem;
  color: var(--primary);
  font-weight: 700;
}

.main-nav {
  display: flex;
  gap: 10px;
}

.main-nav a {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.main-nav a:hover {
  background-color: #f1f5f9;
  color: var(--primary);
}

.main-nav a.router-link-active {
  background-color: var(--primary);
  color: white;
  box-shadow: 0 2px 4px rgba(79, 70, 229, 0.3);
}

/* Animação de entrada e saída das páginas */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.flex-between { display: flex; justify-content: space-between; align-items: center; }
.nav-wrapper { display: flex; align-items: center; gap: 1rem; }
.badge-master { background: #fef08a; color: #854d0e; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-left: 5px; }
.master-link { border-bottom: 2px solid #eab308 !important; }
.btn-logout { background: transparent; border: none; color: #ef4444; padding: 8px; cursor: pointer; border-radius: 6px; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.btn-logout:hover { background: #fef2f2; }
.btn-logout svg { width: 1.5rem; height: 1.5rem; }
</style>