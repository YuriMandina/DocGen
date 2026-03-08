<template>
  <div class="view-container">
    <header class="page-header scale-in">
      <div>
        <h1 class="page-title">⚙️ Configurações da Conta</h1>
        <p class="text-muted">Gerencie seus dados pessoais, credenciais de segurança e acessos da equipe.</p>
      </div>
    </header>

    <section class="card scale-in p-0 overflow-hidden" style="animation-delay: 0.05s;">
      
      <div class="tabs-nav">
        <button class="tab-btn" :class="{ active: abaAtiva === 'dados' }" @click="abaAtiva = 'dados'">
          Meus Dados
        </button>
        <button class="tab-btn" :class="{ active: abaAtiva === 'senha' }" @click="abaAtiva = 'senha'">
          Segurança (Senha)
        </button>
        <button v-if="currentUser.is_master" class="tab-btn master-tab" :class="{ active: abaAtiva === 'acesso' }" @click="abaAtiva = 'acesso'">
          🛡️ Controle de Acesso
        </button>
      </div>

      <div v-if="abaAtiva === 'dados'" class="tab-content fade-in">
        <h2 class="section-title">Informações Pessoais</h2>
        <form @submit.prevent="salvarDados" class="form-grid">
          <div class="input-group btn-full">
            <label class="input-label">Nome Completo</label>
            <input v-model="formDados.full_name" type="text" required class="modern-input" :disabled="isLoading" />
          </div>
          <div class="input-group">
            <label class="input-label">CPF</label>
            <input v-model="formDados.cpf" @input="formDados.cpf = mascaraCPF($event.target.value)" type="text" required class="modern-input" :disabled="isLoading" maxlength="14" />
          </div>
          <div class="input-group">
            <label class="input-label">E-mail Corporativo</label>
            <input v-model="formDados.username" type="email" required class="modern-input" :disabled="isLoading" />
          </div>

          <div class="btn-full mt-3">
            <button type="submit" class="btn-primary" style="width: auto;" :disabled="isLoading">
              <span v-if="isLoading" class="spinner"></span>
              {{ isLoading ? 'Salvando...' : 'Salvar Alterações' }}
            </button>
          </div>
        </form>
      </div>

      <div v-if="abaAtiva === 'senha'" class="tab-content fade-in">
        <h2 class="section-title">Alterar Senha de Acesso</h2>
        <form @submit.prevent="salvarSenha" class="form-grid">
          <div class="input-group btn-full">
            <label class="input-label">Senha Atual</label>
            <input v-model="formSenha.current_password" type="password" required class="modern-input" :disabled="isLoading" placeholder="Digite sua senha atual" />
          </div>
          <div class="input-group">
            <label class="input-label">Nova Senha</label>
            <input v-model="formSenha.new_password" type="password" required class="modern-input" :disabled="isLoading" minlength="8" placeholder="Mínimo de 8 caracteres" />
          </div>
          <div class="input-group">
            <label class="input-label">Confirmar Nova Senha</label>
            <input v-model="formSenha.confirm_new_password" type="password" required class="modern-input" :disabled="isLoading" minlength="8" placeholder="Repita a nova senha" />
          </div>

          <div class="btn-full mt-3">
            <button type="submit" class="btn-success" style="width: auto;" :disabled="isLoading">
              <span v-if="isLoading" class="spinner"></span>
              {{ isLoading ? 'Atualizando...' : 'Atualizar Senha' }}
            </button>
          </div>
        </form>
      </div>

      <div v-if="abaAtiva === 'acesso' && currentUser.is_master" class="tab-content fade-in">
        <div class="table-header">
          <h2 class="section-title m-0">Equipe do RH ({{ usuariosEmpresa.length }})</h2>
          <button @click="buscarUsuarios" class="btn-ghost btn-sm" title="Recarregar">🔄 Atualizar</button>
        </div>
        
        <div class="table-container mt-3">
          <table class="modern-table">
            <thead>
              <tr>
                <th>Nome do Usuário</th>
                <th>E-mail</th>
                <th>Status</th>
                <th class="text-right">Ação</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="usuariosEmpresa.length === 0">
                <td colspan="4" class="text-center py-4 text-muted">Nenhum outro usuário cadastrado na sua empresa.</td>
              </tr>
              <tr v-for="user in usuariosEmpresa" :key="user.id" class="table-row">
                <td class="font-medium">{{ user.full_name }} <span v-if="user.is_master" class="badge-master-sm">Master</span></td>
                <td class="text-muted">{{ user.username }}</td>
                <td>
                  <span :class="user.is_approved ? 'badge-success' : 'badge-danger'">
                    {{ user.is_approved ? 'Aprovado' : 'Bloqueado' }}
                  </span>
                </td>
                <td class="actions-cell">
                  <button v-if="!user.is_approved" @click="alterarAcesso(user, 'approve')" class="btn-success btn-sm">Liberar Acesso</button>
                  <button v-else-if="!user.is_master" @click="alterarAcesso(user, 'revoke')" class="btn-danger btn-sm">Revogar Acesso</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <transition name="fade">
        <div v-if="mensagem" class="feedback-toast m-4" :class="erro ? 'toast-error' : 'toast-success'">
          {{ mensagem }}
        </div>
      </transition>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const abaAtiva = ref('dados');
const isLoading = ref(false);
const mensagem = ref('');
const erro = ref(false);

const currentUser = ref(JSON.parse(localStorage.getItem('@DocGen:user') || '{}'));

// Formulários
const formDados = ref({ full_name: '', cpf: '', username: '' });
const formSenha = ref({ current_password: '', new_password: '', confirm_new_password: '' });
const usuariosEmpresa = ref([]);

// Inicialização
onMounted(() => {
  // Preenche o formulário de dados com o usuário atual do localStorage
  formDados.value.full_name = currentUser.value.full_name;
  formDados.value.cpf = currentUser.value.cpf;
  formDados.value.username = currentUser.value.username;

  if (currentUser.value.is_master) {
    buscarUsuarios();
  }
});

// Máscara de CPF
const mascaraCPF = (v) => {
  v = v.replace(/\D/g, "");
  if (v.length <= 11) {
    v = v.replace(/(\d{3})(\d)/, "$1.$2");
    v = v.replace(/(\d{3})(\d)/, "$1.$2");
    v = v.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
  }
  return v;
};

const mostrarFeedback = (msg, isErro = false) => {
  mensagem.value = msg;
  erro.value = isErro;
  setTimeout(() => { mensagem.value = ''; }, 5000);
};

// --- ABA 1: SALVAR DADOS ---
const salvarDados = async () => {
  isLoading.value = true;
  mensagem.value = '';
  
  try {
    const res = await api.put('/auth/me', formDados.value);
    // Atualiza o localStorage com os novos dados
    localStorage.setItem('@DocGen:user', JSON.stringify(res.data));
    currentUser.value = res.data;
    
    // Dispara evento global (gambiarra do Vue) para o header do App.vue se atualizar
    window.dispatchEvent(new Event('storage'));
    
    mostrarFeedback("Dados cadastrais atualizados com sucesso!");
  } catch (err) {
    mostrarFeedback(err.response?.data?.detail || "Erro ao atualizar dados.", true);
  } finally {
    isLoading.value = false;
  }
};

// --- ABA 2: TROCAR SENHA ---
const salvarSenha = async () => {
  if (formSenha.value.new_password !== formSenha.value.confirm_new_password) {
    mostrarFeedback("A confirmação da nova senha não confere.", true);
    return;
  }

  isLoading.value = true;
  mensagem.value = '';
  
  try {
    await api.put('/auth/password', formSenha.value);
    mostrarFeedback("Senha atualizada! Use a nova senha no próximo login.");
    formSenha.value = { current_password: '', new_password: '', confirm_new_password: '' };
  } catch (err) {
    mostrarFeedback(err.response?.data?.detail || "Erro ao trocar senha. Verifique sua senha atual.", true);
  } finally {
    isLoading.value = false;
  }
};

// --- ABA 3: CONTROLE DE ACESSO ---
const buscarUsuarios = async () => {
  try {
    const res = await api.get('/users/company');
    usuariosEmpresa.value = res.data;
  } catch (err) {
    console.error("Erro ao carregar usuários.", err);
  }
};

const alterarAcesso = async (user, action) => {
  if (action === 'revoke' && !confirm(`Tem certeza que deseja bloquear o acesso de ${user.full_name}?`)) return;
  
  try {
    await api.put(`/users/${user.id}/${action}`);
    mostrarFeedback(`Acesso de ${user.full_name} foi ${action === 'approve' ? 'liberado' : 'bloqueado'}.`);
    await buscarUsuarios(); // Recarrega tabela
  } catch (err) {
    mostrarFeedback(err.response?.data?.detail || "Erro ao alterar acesso.", true);
  }
};
</script>

<style scoped>
/* Reutilização base do seu design */
.view-container { display: flex; flex-direction: column; gap: 2rem; padding-bottom: 2rem; max-width: 900px; margin: 0 auto;}
.page-title { font-size: 1.8rem; font-weight: 700; color: var(--text-main); margin: 0 0 0.5rem 0; letter-spacing: -0.025em; }
.section-title { font-size: 1.25rem; font-weight: 600; color: var(--text-main); margin: 0 0 1.5rem 0; border-bottom: 2px solid var(--border); padding-bottom: 0.75rem;}
.text-muted { color: var(--text-muted); font-size: 0.95rem; line-height: 1.5; margin: 0; }
.card { background: var(--surface); border-radius: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05); border: 1px solid var(--border); }
.p-0 { padding: 0 !important; }
.m-4 { margin: 1.5rem; }
.overflow-hidden { overflow: hidden; }

/* Navegação das Abas */
.tabs-nav { display: flex; background: #f8fafc; border-bottom: 1px solid var(--border); }
.tab-btn { flex: 1; padding: 1.25rem 1rem; background: transparent; border: none; border-bottom: 3px solid transparent; color: var(--text-muted); font-weight: 600; font-size: 1rem; cursor: pointer; transition: all 0.2s ease; outline: none; }
.tab-btn:hover { background: #f1f5f9; color: var(--text-main); }
.tab-btn.active { background: white; color: var(--primary); border-bottom-color: var(--primary); }
.master-tab.active { color: #854d0e; border-bottom-color: #eab308; }
.tab-content { padding: 2rem; }

/* Formulários */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.input-group { display: flex; flex-direction: column; gap: 0.5rem; }
.btn-full { grid-column: 1 / -1; }
.input-label { font-size: 0.875rem; font-weight: 600; color: var(--text-main); }
.modern-input { width: 100%; padding: 0.75rem 1rem; font-size: 0.95rem; line-height: 1.5; color: var(--text-main); background-color: var(--bg-color); border: 1px solid var(--border); border-radius: 0.5rem; transition: all 0.2s ease; outline: none; box-sizing: border-box;}
.modern-input:focus { background-color: #fff; border-color: var(--primary); box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1); }
.modern-input:disabled { background-color: #f1f5f9; cursor: not-allowed; opacity: 0.7; }

/* Botões */
button { display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; font-weight: 500; font-size: 0.95rem; padding: 0.75rem 1.5rem; border-radius: 0.5rem; border: none; cursor: pointer; transition: all 0.2s ease; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background-color: var(--primary); color: white; }
.btn-primary:hover:not(:disabled) { background-color: var(--primary-hover); transform: translateY(-1px); }
.btn-success { background-color: var(--secondary); color: white; }
.btn-success:hover:not(:disabled) { background-color: var(--secondary-hover); transform: translateY(-1px); }
.btn-danger { background-color: #ef4444; color: white; }
.btn-danger:hover:not(:disabled) { background-color: #dc2626; transform: translateY(-1px); }
.btn-ghost { background-color: transparent; border: 1px solid var(--border); }
.btn-ghost:hover { background-color: #f1f5f9; }
.btn-sm { padding: 0.4rem 0.8rem; font-size: 0.85rem; }

/* Tabela e Badges */
.table-header { display: flex; justify-content: space-between; align-items: center; }
.table-container { border: 1px solid var(--border); border-radius: 0.75rem; overflow: hidden; background: white; }
.modern-table { width: 100%; border-collapse: collapse; text-align: left; }
.modern-table th { background-color: #f8fafc; padding: 1rem 1.5rem; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); border-bottom: 1px solid var(--border); }
.modern-table td { padding: 1rem 1.5rem; border-bottom: 1px solid var(--border); color: var(--text-main); vertical-align: middle; }
.table-row:hover { background-color: #f8fafc; }
.actions-cell { display: flex; justify-content: flex-end; }
.badge-success { background: #ecfdf5; color: #065f46; padding: 0.25rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; }
.badge-danger { background: #fef2f2; color: #991b1b; padding: 0.25rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; }
.badge-master-sm { background: #fef08a; color: #854d0e; font-size: 0.6rem; padding: 2px 4px; border-radius: 4px; font-weight: bold; margin-left: 5px; vertical-align: super; }

/* Utilidades */
.spinner { width: 1.25rem; height: 1.25rem; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: currentColor; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.scale-in { animation: scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) backwards; }
@keyframes scaleIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.feedback-toast { display: flex; align-items: center; justify-content: center; padding: 0.75rem; border-radius: 0.5rem; font-weight: 500; font-size: 0.95rem; }
.toast-success { background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.toast-error { background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } .tabs-nav { flex-direction: column; } }
</style>