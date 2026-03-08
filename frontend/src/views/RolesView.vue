<template>
  <div class="view-container">
    
    <header class="page-header scale-in">
      <div>
        <h1 class="page-title">Gestão de Cargos</h1>
        <p class="text-muted">Gerencie os cargos e permissões da sua organização.</p>
      </div>
    </header>

    <section class="card scale-in" style="animation-delay: 0.05s;">
      <h2 class="section-title">Cadastrar Novo Cargo</h2>
      <form @submit.prevent="criarCargo" class="form-row">
        <div class="input-group">
          <label for="roleName" class="sr-only">Nome do Cargo</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <input 
              id="roleName"
              v-model="novoCargo.name" 
              type="text" 
              placeholder="Ex: Desenvolvedor Full Stack" 
              required 
              class="modern-input with-icon" 
              :disabled="isSubmitting"
            />
          </div>
        </div>
        <button type="submit" class="btn-primary" :disabled="isSubmitting || !novoCargo.name.trim()">
          <span v-if="isSubmitting" class="spinner"></span>
          <svg v-else class="btn-icon-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          {{ isSubmitting ? 'Salvando...' : 'Adicionar Cargo' }}
        </button>
      </form>
      
      <transition name="fade">
        <div v-if="mensagem" class="feedback-toast" :class="erro ? 'toast-error' : 'toast-success'">
          <svg v-if="!erro" class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
          <svg v-else class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          {{ mensagem }}
        </div>
      </transition>
    </section>

    <section class="card scale-in" style="animation-delay: 0.1s;">
      <div class="table-header">
        <h2 class="section-title m-0">Cargos Cadastrados</h2>
        <span class="badge">{{ cargos.length }} registro(s)</span>
      </div>
      
      <div class="table-container">
        <div v-if="isLoadingData" class="loading-state">
          <span class="spinner-large"></span>
          <p class="text-muted">Carregando dados...</p>
        </div>

        <table v-else class="modern-table">
          <thead>
            <tr>
              <th width="10%">ID</th>
              <th width="70%">Nome do Cargo</th>
              <th width="20%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="cargos.length === 0">
              <td colspan="3">
                <div class="empty-state">
                  <div class="empty-icon-wrapper">
                    <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                  </div>
                  <h3>Nenhum cargo encontrado</h3>
                  <p class="text-muted">Comece adicionando um novo cargo no formulário acima.</p>
                </div>
              </td>
            </tr>
            <tr v-for="cargo in cargos" :key="cargo.id" class="table-row">
              <td class="text-muted">#{{ cargo.id }}</td>
              <td class="font-medium">{{ cargo.name }}</td>
              <td class="actions-cell">
                <button @click="abrirModalEdicao(cargo)" class="btn-action edit" aria-label="Editar cargo" title="Editar">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                </button>
                <button @click="confirmarExclusao(cargo)" class="btn-action delete" aria-label="Excluir cargo" title="Excluir">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <transition name="modal-fade">
      <div v-if="modalAberto" class="modal-overlay" @click.self="fecharModalEdicao">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Editar Cargo</h3>
            <button @click="fecharModalEdicao" class="btn-close" aria-label="Fechar modal">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
          
          <form @submit.prevent="salvarEdicao">
            <div class="input-group">
              <label class="input-label">Nome do Cargo</label>
              <input 
                ref="inputEdicao"
                v-model="cargoEmEdicao.name" 
                type="text" 
                required 
                class="modern-input" 
                :disabled="isSubmitting"
              />
            </div>
            
            <p v-if="erroModal" class="feedback-text error mt-2">{{ erroModal }}</p>
            
            <div class="modal-actions">
              <button type="button" @click="fecharModalEdicao" class="btn-ghost" :disabled="isSubmitting">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="isSubmitting || cargoEmEdicao.name === cargoOriginalNome">
                <span v-if="isSubmitting" class="spinner"></span>
                {{ isSubmitting ? 'Salvando...' : 'Salvar Alterações' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>

    <transition name="modal-fade">
      <div v-if="modalExclusaoAberto" class="modal-overlay" @click.self="modalExclusaoAberto = false">
        <div class="modal-content danger-modal">
          <div class="danger-icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          </div>
          <h3>Excluir Cargo?</h3>
          <p class="text-muted text-center mt-2">
            Tem certeza que deseja excluir o cargo <strong>{{ cargoParaExcluir?.name }}</strong>?<br>
            Esta ação não poderá ser desfeita.
          </p>
          
          <p v-if="erroExclusao" class="feedback-text error mt-2 text-center">{{ erroExclusao }}</p>
          
          <div class="modal-actions justify-center mt-4">
            <button @click="modalExclusaoAberto = false" class="btn-ghost" :disabled="isSubmitting">Cancelar</button>
            <button @click="executarExclusao" class="btn-danger" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner"></span>
              {{ isSubmitting ? 'Excluindo...' : 'Sim, excluir cargo' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import api from '../services/api';

// --- ESTADOS GLOBAIS ---
const cargos = ref([]);
const novoCargo = ref({ name: '' });
const isLoadingData = ref(true);
const isSubmitting = ref(false);

// Feedbacks Gerais
const mensagem = ref('');
const erro = ref(false);

// Estados Edição
const modalAberto = ref(false);
const cargoEmEdicao = ref({ id: null, name: '' });
const cargoOriginalNome = ref('');
const erroModal = ref('');
const inputEdicao = ref(null);

// Estados Exclusão
const modalExclusaoAberto = ref(false);
const cargoParaExcluir = ref(null);
const erroExclusao = ref('');

// --- LIFECYCLE ---
onMounted(async () => {
  await buscarCargos();
});

// --- HELPERS ---
const mostrarFeedback = (msg, isErro = false) => {
  mensagem.value = msg;
  erro.value = isErro;
  setTimeout(() => { mensagem.value = ''; }, 4000);
};

// --- MÉTODOS DE API ---
const buscarCargos = async () => {
  isLoadingData.value = true;
  try {
    const response = await api.get('/roles/');
    cargos.value = response.data;
  } catch {
    mostrarFeedback("Erro ao conectar com o servidor.", true);
  } finally {
    isLoadingData.value = false;
  }
};

const criarCargo = async () => {
  isSubmitting.value = true;
  mensagem.value = '';
  
  try {
    await api.post('/roles/', novoCargo.value);
    novoCargo.value.name = ''; 
    mostrarFeedback('Cargo cadastrado com sucesso!');
    await buscarCargos();
  } catch (err) {
    mostrarFeedback(err.response?.data?.detail || 'Erro ao criar cargo.', true);
  } finally {
    isSubmitting.value = false;
  }
};

// --- FLUXO DE EDIÇÃO ---
const abrirModalEdicao = (cargo) => {
  cargoEmEdicao.value = { ...cargo };
  cargoOriginalNome.value = cargo.name;
  erroModal.value = '';
  modalAberto.value = true;
  
  // Foca no input automaticamente após o modal abrir
  nextTick(() => {
    if (inputEdicao.value) inputEdicao.value.focus();
  });
};

const fecharModalEdicao = () => {
  modalAberto.value = false;
  erroModal.value = '';
};

const salvarEdicao = async () => {
  isSubmitting.value = true;
  erroModal.value = '';
  
  try {
    await api.put(`/roles/${cargoEmEdicao.value.id}`, { name: cargoEmEdicao.value.name });
    fecharModalEdicao();
    mostrarFeedback('Cargo atualizado com sucesso!');
    await buscarCargos();
  } catch (err) {
    erroModal.value = err.response?.data?.detail || 'Erro ao editar cargo.';
  } finally {
    isSubmitting.value = false;
  }
};

// --- FLUXO DE EXCLUSÃO ---
const confirmarExclusao = (cargo) => {
  cargoParaExcluir.value = cargo;
  erroExclusao.value = '';
  modalExclusaoAberto.value = true;
};

const executarExclusao = async () => {
  isSubmitting.value = true;
  erroExclusao.value = '';
  
  try {
    await api.delete(`/roles/${cargoParaExcluir.value.id}`);
    modalExclusaoAberto.value = false;
    mostrarFeedback('Cargo excluído com sucesso!');
    await buscarCargos();
  } catch (err) {
    erroExclusao.value = err.response?.data?.detail || 'Não foi possível excluir este cargo.';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* --- VARIÁVEIS LOCAIS (Elevando o Design) --- */
:root {
  --transition-fast: 0.2s ease;
  --transition-smooth: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.view-container { display: flex; flex-direction: column; gap: 2rem; padding-bottom: 2rem; }

/* Tipografia e Headers */
.page-header { margin-bottom: 0.5rem; }
.page-title { font-size: 1.8rem; font-weight: 700; color: var(--text-main); margin: 0 0 0.5rem 0; letter-spacing: -0.025em; }
.section-title { font-size: 1.25rem; font-weight: 600; color: var(--text-main); margin: 0 0 1.5rem 0; }
.text-muted { color: var(--text-muted); font-size: 0.95rem; line-height: 1.5; margin: 0; }
.font-medium { font-weight: 500; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.m-0 { margin: 0; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 1rem; }
.mt-4 { margin-top: 1.5rem; }

/* Cards */
.card {
  background: var(--surface);
  padding: 1.5rem 2rem;
  border-radius: 1rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  transition: box-shadow var(--transition-smooth);
}
.card:hover { box-shadow: var(--shadow-md); }

/* Formulários Avançados */
.form-row { display: flex; gap: 1rem; align-items: flex-start; }
.input-group { flex: 1; display: flex; flex-direction: column; gap: 0.5rem; }
.input-label { font-size: 0.875rem; font-weight: 500; color: var(--text-main); }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border-width: 0; }
.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 1rem; width: 1.25rem; height: 1.25rem; color: var(--text-muted); pointer-events: none; }

.modern-input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--text-main);
  background-color: var(--bg-color);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  transition: all var(--transition-fast);
  outline: none;
}
.modern-input.with-icon { padding-left: 2.75rem; }
.modern-input:focus { background-color: #fff; border-color: var(--primary); box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1); }
.modern-input:disabled { background-color: #f1f5f9; cursor: not-allowed; opacity: 0.7; }

/* Botões Modernos */
button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
  font-size: 0.95rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}
button:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
button:disabled { opacity: 0.6; cursor: not-allowed; transform: none !important; }

.btn-primary { background-color: var(--primary); color: white; box-shadow: var(--shadow-sm); }
.btn-primary:hover:not(:disabled) { background-color: var(--primary-hover); transform: translateY(-1px); box-shadow: var(--shadow-md); }
.btn-ghost { background-color: transparent; color: var(--text-main); border: 1px solid var(--border); }
.btn-ghost:hover:not(:disabled) { background-color: var(--bg-color); }
.btn-danger { background-color: #ef4444; color: white; }
.btn-danger:hover:not(:disabled) { background-color: #dc2626; transform: translateY(-1px); }
.btn-icon-svg { width: 1.25rem; height: 1.25rem; }

/* Feedbacks (Toast inline) */
.feedback-toast {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  animation: slideUp 0.3s ease-out;
}
.toast-icon { width: 1.25rem; height: 1.25rem; flex-shrink: 0; }
.toast-success { background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.toast-error { background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.feedback-text.error { color: #dc2626; font-size: 0.875rem; font-weight: 500; }

/* Tabela e Cabeçalho */
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.badge { background: #e0e7ff; color: var(--primary-hover); padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; }
.table-container { border: 1px solid var(--border); border-radius: 0.75rem; overflow: hidden; background: white; }
.modern-table { width: 100%; border-collapse: collapse; text-align: left; }
.modern-table th { background-color: #f8fafc; padding: 1rem 1.5rem; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); border-bottom: 1px solid var(--border); }
.modern-table td { padding: 1rem 1.5rem; border-bottom: 1px solid var(--border); color: var(--text-main); vertical-align: middle; }
.modern-table tr:last-child td { border-bottom: none; }
.table-row { transition: background-color var(--transition-fast); }
.table-row:hover { background-color: #f8fafc; }

/* Botões de Ação da Tabela */
.actions-cell { display: flex; justify-content: flex-end; gap: 0.5rem; }
.btn-action { padding: 0.5rem; border-radius: 0.375rem; background: transparent; color: var(--text-muted); border: 1px solid transparent; }
.btn-action svg { width: 1.25rem; height: 1.25rem; }
.btn-action.edit:hover { color: var(--primary); background: #e0e7ff; border-color: #c7d2fe; }
.btn-action.delete:hover { color: #dc2626; background: #fef2f2; border-color: #fecaca; }

/* Empty State e Loading */
.empty-state, .loading-state { padding: 4rem 2rem; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.empty-icon-wrapper { background: #f1f5f9; padding: 1rem; border-radius: 50%; margin-bottom: 1rem; color: var(--text-muted); }
.empty-icon { width: 2rem; height: 2rem; }
.empty-state h3 { margin: 0 0 0.5rem 0; color: var(--text-main); font-size: 1.1rem; }

/* Modais Refinados */
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 1000; padding: 1rem; }
.modal-content { background: white; width: 100%; max-width: 28rem; border-radius: 1rem; padding: 2rem; box-shadow: var(--shadow-lg); position: relative; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.modal-header h3 { margin: 0; font-size: 1.25rem; font-weight: 600; color: var(--text-main); }
.btn-close { background: transparent; padding: 0.25rem; border-radius: 0.25rem; color: var(--text-muted); position: absolute; top: 1.5rem; right: 1.5rem; }
.btn-close svg { width: 1.5rem; height: 1.5rem; }
.btn-close:hover { background: #f1f5f9; color: var(--text-main); }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 2rem; }
.justify-center { justify-content: center; }

/* Modal de Exclusão Específico */
.danger-modal { text-align: center; }
.danger-icon-wrapper { background: #fef2f2; color: #dc2626; width: 3rem; height: 3rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; }
.danger-icon-wrapper svg { width: 1.5rem; height: 1.5rem; }
.danger-modal h3 { font-size: 1.25rem; font-weight: 600; color: var(--text-main); margin: 0; }

/* Animações Keyframes */
.spinner { width: 1.25rem; height: 1.25rem; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: currentColor; animation: spin 0.8s linear infinite; }
.spinner-large { width: 2.5rem; height: 2.5rem; border: 3px solid #e2e8f0; border-radius: 50%; border-top-color: var(--primary); animation: spin 0.8s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }
.scale-in { animation: scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) backwards; }
@keyframes scaleIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Transições do Vue */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.modal-fade-enter-active, .modal-fade-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .modal-content, .modal-fade-leave-to .modal-content { transform: scale(0.95) translateY(10px); }
</style>