<template>
  <div class="app-container">
    <header class="glass-header">
      <div class="header-content">
        <h1>📑 Sistema de Contratos</h1>
        <nav class="main-nav">
          <router-link to="/cargos">🏢 Cargos</router-link>
          <router-link to="/funcionarios">👥 Funcionários</router-link>
          <router-link to="/modelos">📄 Modelos</router-link>       
          <router-link to="/gerar">🖨️ Gerar Contrato</router-link> 
        </nav>
      </div>
    </header>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade-slide" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

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
</style>