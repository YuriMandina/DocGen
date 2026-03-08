<template>
  <div class="auth-container scale-in">
    <div class="card auth-card">
      <div class="text-center mb-4">
        <div class="logo-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
        </div>
        <h1 class="page-title mt-3">Acessar o Sistema</h1>
        <p class="text-muted">Insira suas credenciais corporativas.</p>
      </div>

      <form @submit.prevent="fazerLogin" class="form-grid">
        <div class="input-group btn-full">
          <label class="input-label">E-mail Corporativo</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" /></svg>
            <input v-model="form.username" type="email" required class="modern-input with-icon" :disabled="isLoading" placeholder="E-mail" />
          </div>
        </div>

        <div class="input-group btn-full">
          <label class="input-label">Senha</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
            <input v-model="form.password" type="password" required class="modern-input with-icon" :disabled="isLoading" placeholder="Sua senha" />
          </div>
        </div>

        <div v-if="erro" class="btn-full feedback-toast toast-error mt-2">
          {{ erro }}
        </div>

        <div class="btn-full mt-3">
          <button type="submit" class="btn-primary w-full" :disabled="isLoading">
            <span v-if="isLoading" class="spinner"></span>
            {{ isLoading ? 'Autenticando...' : 'Entrar no DocGen' }}
          </button>
        </div>
      </form>

      <div class="text-center mt-4">
        <p class="text-muted">Ainda não possui conta? <router-link to="/registro" class="link-primary">Registre-se aqui</router-link>.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

// Emite um evento para o App.vue saber que logou e mostrar o menu
const emit = defineEmits(['login-success']);
const router = useRouter();
const isLoading = ref(false);
const erro = ref('');

const form = ref({ username: '', password: '' });

const fazerLogin = async () => {
  isLoading.value = true;
  erro.value = '';
  
  try {
    // 1. O FastAPI espera os dados de login no formato form-urlencoded
    const params = new URLSearchParams();
    params.append('username', form.value.username);
    params.append('password', form.value.password);
    
    // 2. Busca o Token
    const resToken = await api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    // Salva o token temporariamente para a próxima requisição
    localStorage.setItem('@DocGen:token', resToken.data.access_token);
    
    // 3. Busca os dados do Usuário usando a rota /me que criamos
    const resUser = await api.get('/auth/me');
    localStorage.setItem('@DocGen:user', JSON.stringify(resUser.data));
    
    // 4. Avisa o Vue que o login deu certo e redireciona
    emit('login-success');
    router.push('/cargos');

  } catch (err) {
    // Limpa se der erro
    localStorage.removeItem('@DocGen:token');
    localStorage.removeItem('@DocGen:user');
    
    if (err.response?.status === 403) {
      erro.value = "Sua conta ainda não foi aprovada pelo Administrador da sua empresa.";
    } else {
      erro.value = err.response?.data?.detail || 'Credenciais inválidas. Tente novamente.';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; padding: 4rem 1rem; }
.card { background: var(--surface, #ffffff); padding: 2.5rem; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); border: 1px solid var(--border, #e2e8f0); }
.auth-card { max-width: 420px; width: 100%; }

/* Cabeçalho do Card */
.logo-wrapper { background: #e0e7ff; color: var(--primary, #4f46e5); width: 4rem; height: 4rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
.logo-wrapper svg { width: 2rem; height: 2rem; }
.mb-4 { margin-bottom: 1.5rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 1rem; }
.mt-4 { margin-top: 1.5rem; }
.text-center { text-align: center; }
.page-title { font-size: 1.8rem; font-weight: 700; color: var(--text-main, #0f172a); margin: 0 0 0.5rem 0; letter-spacing: -0.025em; }
.text-muted { color: var(--text-muted, #64748b); font-size: 0.95rem; line-height: 1.5; margin: 0; }

/* Formulários */
.form-grid { display: grid; grid-template-columns: 1fr; gap: 1.25rem; }
.input-group { display: flex; flex-direction: column; gap: 0.5rem; }
.btn-full { grid-column: 1 / -1; }
.input-label { font-size: 0.875rem; font-weight: 600; color: var(--text-main, #0f172a); text-align: left; }

/* Wrapper para o ícone não ficar gigante */
.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 1rem; width: 1.25rem; height: 1.25rem; color: var(--text-muted, #64748b); pointer-events: none; }

.modern-input { width: 100%; padding: 0.75rem 1rem; font-size: 0.95rem; line-height: 1.5; color: var(--text-main); background-color: var(--bg-color, #f8fafc); border: 1px solid var(--border, #e2e8f0); border-radius: 0.5rem; transition: all 0.2s ease; outline: none; box-sizing: border-box; }
.modern-input.with-icon { padding-left: 2.75rem; }
.modern-input:focus { background-color: #fff; border-color: var(--primary, #4f46e5); box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1); }
.modern-input:disabled { background-color: #f1f5f9; cursor: not-allowed; opacity: 0.7; }

/* Botões */
button { display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; font-weight: 500; font-size: 1rem; padding: 0.85rem 1.5rem; border-radius: 0.5rem; border: none; cursor: pointer; transition: all 0.2s ease; width: 100%; box-sizing: border-box; }
button:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
button:disabled { opacity: 0.6; cursor: not-allowed; transform: none !important; box-shadow: none !important; }

.btn-primary { background-color: var(--primary, #4f46e5); color: white; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.btn-primary:hover:not(:disabled) { background-color: var(--primary-hover, #4338ca); transform: translateY(-1px); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }

.link-primary { color: var(--primary); font-weight: 600; text-decoration: none; }
.link-primary:hover { text-decoration: underline; }

/* Spinner e Animação */
.spinner { width: 1.25rem; height: 1.25rem; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: white; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.scale-in { animation: scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) backwards; }
@keyframes scaleIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }

/* Feedbacks */
.feedback-toast { padding: 0.75rem 1rem; border-radius: 0.5rem; font-size: 0.9rem; font-weight: 500; text-align: center; }
.toast-error { background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
</style>