<template>
  <div class="view-container">
    <header class="page-header scale-in">
      <div>
        <h1 class="page-title">🛡️ Painel de Aprovações</h1>
        <p class="text-muted">Como Master, você é responsável por liberar o acesso dos funcionários do RH da sua empresa.</p>
      </div>
    </header>

    <section class="card scale-in" style="animation-delay: 0.05s;">
      <div class="table-header">
        <h2 class="section-title m-0">Solicitações Pendentes</h2>
        <span class="badge">{{ pendingUsers.length }} aguardando</span>
      </div>

      <div class="table-container mt-3">
        <div v-if="isLoading" class="loading-state">
          <span class="spinner-large"></span>
          <p class="text-muted">Buscando solicitações...</p>
        </div>

        <table v-else class="modern-table">
          <thead>
            <tr>
              <th width="30%">Nome do Usuário</th>
              <th width="25%">E-mail Corporativo</th>
              <th width="20%">CPF</th>
              <th width="25%" class="text-right">Ação</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="pendingUsers.length === 0">
              <td colspan="4">
                <div class="empty-state">
                  <div class="empty-icon-wrapper" style="background: #ecfdf5; color: #10b981;">
                    <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  </div>
                  <h3>Tudo limpo por aqui!</h3>
                  <p class="text-muted">Nenhum usuário aguardando aprovação na sua empresa no momento.</p>
                </div>
              </td>
            </tr>
            <tr v-for="user in pendingUsers" :key="user.id" class="table-row">
              <td class="font-medium">{{ user.full_name }}</td>
              <td class="text-muted">{{ user.username }}</td>
              <td class="font-mono">{{ user.cpf }}</td>
              <td class="actions-cell">
                <button 
                  @click="aprovarUsuario(user)" 
                  class="btn-success" 
                  :disabled="isApproving === user.id"
                >
                  <span v-if="isApproving === user.id" class="spinner" style="width: 1rem; height: 1rem;"></span>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 1.25rem; height: 1.25rem;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                  {{ isApproving === user.id ? 'Aprovando...' : 'Aprovar Acesso' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <transition name="fade">
        <div v-if="mensagem" class="feedback-toast mt-3" :class="erro ? 'toast-error' : 'toast-success'">
          {{ mensagem }}
        </div>
      </transition>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const pendingUsers = ref([]);
const isLoading = ref(true);
const isApproving = ref(null);

const mensagem = ref('');
const erro = ref(false);

const mostrarFeedback = (msg, isErro = false) => {
  mensagem.value = msg;
  erro.value = isErro;
  setTimeout(() => { mensagem.value = ''; }, 4000);
};

const buscarPendentes = async () => {
  isLoading.value = true;
  try {
    const res = await api.get('/users/pending');
    pendingUsers.value = res.data;
  } catch {
    mostrarFeedback("Erro ao carregar solicitações.", true);
  } finally {
    isLoading.value = false;
  }
};

const aprovarUsuario = async (user) => {
  isApproving.value = user.id;
  try {
    await api.put(`/users/${user.id}/approve`);
    mostrarFeedback(`Acesso de ${user.full_name} liberado com sucesso!`);
    await buscarPendentes(); // Recarrega a lista
  } catch (err) {
    mostrarFeedback(err.response?.data?.detail || "Erro ao aprovar usuário.", true);
  } finally {
    isApproving.value = null;
  }
};

onMounted(() => {
  buscarPendentes();
});
</script>

<style scoped>
/* Aproveitando as variáveis e o design global do seu sistema */
.view-container { display: flex; flex-direction: column; gap: 2rem; padding-bottom: 2rem; }
.page-header { margin-bottom: 0.5rem; }
.page-title { font-size: 1.8rem; font-weight: 700; color: var(--text-main); margin: 0 0 0.5rem 0; letter-spacing: -0.025em; }
.section-title { font-size: 1.25rem; font-weight: 600; color: var(--text-main); margin: 0; }
.text-muted { color: var(--text-muted); font-size: 0.95rem; line-height: 1.5; margin: 0; }
.font-medium { font-weight: 500; }
.font-mono { font-family: ui-monospace, monospace; font-size: 0.9em; letter-spacing: 0.05em; color: var(--text-muted); }

.card { background: var(--surface); padding: 1.5rem 2rem; border-radius: 1rem; box-shadow: var(--shadow-sm); border: 1px solid var(--border); }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.badge { background: #e0e7ff; color: var(--primary-hover); padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; }

.table-container { border: 1px solid var(--border); border-radius: 0.75rem; overflow: hidden; background: white; }
.modern-table { width: 100%; border-collapse: collapse; text-align: left; }
.modern-table th { background-color: #f8fafc; padding: 1rem 1.5rem; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); border-bottom: 1px solid var(--border); }
.modern-table td { padding: 1rem 1.5rem; border-bottom: 1px solid var(--border); color: var(--text-main); vertical-align: middle; }
.modern-table tr:last-child td { border-bottom: none; }
.table-row:hover { background-color: #f8fafc; }
.actions-cell { display: flex; justify-content: flex-end; }

button { display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; font-weight: 500; font-size: 0.9rem; padding: 0.6rem 1rem; border-radius: 0.5rem; border: none; cursor: pointer; transition: all 0.2s; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-success { background-color: var(--secondary); color: white; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.btn-success:hover:not(:disabled) { background-color: var(--secondary-hover); transform: translateY(-1px); }

.empty-state, .loading-state { padding: 4rem 2rem; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.empty-icon-wrapper { background: #f1f5f9; padding: 1rem; border-radius: 50%; margin-bottom: 1rem; }
.empty-icon { width: 2.5rem; height: 2.5rem; }
.empty-state h3 { margin: 0 0 0.5rem 0; color: var(--text-main); font-size: 1.1rem; }
.spinner { width: 1.25rem; height: 1.25rem; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: currentColor; animation: spin 0.8s linear infinite; }
.spinner-large { width: 2.5rem; height: 2.5rem; border: 3px solid #e2e8f0; border-radius: 50%; border-top-color: var(--primary); animation: spin 0.8s linear infinite; margin-bottom: 1rem; }

@keyframes spin { to { transform: rotate(360deg); } }
.scale-in { animation: scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) backwards; }
@keyframes scaleIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.feedback-toast { padding: 0.75rem 1rem; border-radius: 0.5rem; font-size: 0.9rem; font-weight: 500; text-align: center; }
.toast-success { background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.toast-error { background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
</style>