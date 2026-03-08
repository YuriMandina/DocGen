<template>
  <div class="view-container">
    
    <header class="page-header scale-in">
      <div>
        <h1 class="page-title">Modelos de Contrato</h1>
        <p class="text-muted">Faça o upload e gerencie os modelos base em Word (.docx) que serão usados para gerar os contratos preenchidos.</p>
      </div>
    </header>

    <section class="card scale-in" style="animation-delay: 0.05s;">
      <h2 class="section-title">Adicionar Novo Modelo (.docx)</h2>
      <form @submit.prevent="fazerUpload" class="form-grid">
        
        <div class="input-group">
          <label class="input-label">Nome do Contrato</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
            <input v-model="formUpload.name" type="text" placeholder="Ex: Contrato de Trabalho CLT" required class="modern-input with-icon" :disabled="isUploading" />
          </div>
        </div>

        <div class="input-group">
          <label class="input-label">Tipo de Contrato</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" /></svg>
            <select v-model="formUpload.type" required class="modern-input with-icon" :disabled="isUploading">
              <option value="UNIVERSAL">Universal (Aplica-se a todos)</option>
              <option value="ESPECIFICO">Específico (Por Cargo)</option>
            </select>
          </div>
        </div>

        <div v-if="formUpload.type === 'ESPECIFICO'" class="input-group">
          <label class="input-label">Vincular ao Cargo</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
            <select v-model="formUpload.role_id" required class="modern-input with-icon" :disabled="isUploading || cargos.length === 0">
              <option value="" disabled>{{ cargos.length === 0 ? 'Cadastre um cargo primeiro' : 'Selecione um cargo' }}</option>
              <option v-for="cargo in cargos" :key="cargo.id" :value="cargo.id">{{ cargo.name }}</option>
            </select>
          </div>
        </div>

        <div class="input-group" :class="{'btn-full': formUpload.type !== 'ESPECIFICO'}">
          <label class="input-label">Arquivo Word (.docx)</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" /></svg>
            <input type="file" ref="fileInput" accept=".docx" @change="selecionarFicheiro" required class="modern-input with-icon file-input" :disabled="isUploading" />
          </div>
        </div>

        <div class="btn-full mt-2">
          <button type="submit" class="btn-primary w-full" :disabled="isUploading || !formUpload.file">
            <span v-if="isUploading" class="spinner"></span>
            <svg v-else class="btn-icon-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
            {{ isUploading ? 'Validando e Enviando...' : 'Fazer Upload do Modelo' }}
          </button>
        </div>
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
        <h2 class="section-title m-0">Modelos no Sistema</h2>
        <span class="badge">{{ contratos.length }} modelo(s)</span>
      </div>
      
      <div class="table-container mt-3">
        <div v-if="isLoadingData" class="loading-state">
          <span class="spinner-large"></span>
          <p class="text-muted">Carregando modelos disponíveis...</p>
        </div>

        <table v-else class="modern-table">
          <thead>
            <tr>
              <th width="40%">Nome do Modelo</th>
              <th width="20%">Tipo</th>
              <th width="30%">Cargo Vinculado</th>
              <th width="10%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="contratos.length === 0">
              <td colspan="4">
                <div class="empty-state">
                  <div class="empty-icon-wrapper">
                    <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                  </div>
                  <h3>Nenhum modelo cadastrado</h3>
                  <p class="text-muted">Faça o upload do seu primeiro arquivo Word utilizando o formulário acima.</p>
                </div>
              </td>
            </tr>
            <tr v-for="contrato in contratos" :key="contrato.id" class="table-row">
              <td class="font-medium">{{ contrato.contract_name }}</td>
              <td>
                <span :class="contrato.type === 'UNIVERSAL' ? 'badge-uni' : 'badge-esp'">
                  {{ contrato.type }}
                </span>
              </td>
              <td class="text-muted">{{ contrato.type === 'ESPECIFICO' ? getNomeCargo(contrato.role_id) : 'Todos os cargos' }}</td>
              <td class="actions-cell">
                <button @click="confirmarExclusao(contrato)" class="btn-action delete" aria-label="Excluir Modelo" title="Excluir">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <transition name="modal-fade">
      <div v-if="modalExclusaoAberto" class="modal-overlay" @click.self="modalExclusaoAberto = false">
        <div class="modal-content danger-modal">
          <div class="danger-icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
          </div>
          <h3>Excluir Modelo?</h3>
          <p class="text-muted text-center mt-2">
            Tem certeza que deseja apagar o modelo <strong>{{ contratoParaExcluir?.contract_name }}</strong> do servidor?<br>
            Esta ação removerá o arquivo físico permanentemente.
          </p>
          
          <p v-if="erroExclusao" class="feedback-text error mt-2 text-center">{{ erroExclusao }}</p>
          
          <div class="modal-actions justify-center mt-4">
            <button @click="modalExclusaoAberto = false" class="btn-ghost" :disabled="isDeleting">Cancelar</button>
            <button @click="executarExclusao" class="btn-danger" :disabled="isDeleting">
              <span v-if="isDeleting" class="spinner"></span>
              {{ isDeleting ? 'Excluindo...' : 'Sim, excluir modelo' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

// --- ESTADOS GLOBAIS ---
const cargos = ref([]);
const contratos = ref([]);
const isLoadingData = ref(true);
const isUploading = ref(false);

const formUpload = ref({ name: '', type: 'UNIVERSAL', role_id: '', file: null });
const fileInput = ref(null); // Referência para limpar o input HTML do arquivo
const mensagem = ref('');
const erro = ref(false);

// Estados Exclusão
const modalExclusaoAberto = ref(false);
const contratoParaExcluir = ref(null);
const isDeleting = ref(false);
const erroExclusao = ref('');

// --- LIFECYCLE ---
onMounted(async () => {
  isLoadingData.value = true;
  try {
    const [resCargos, resContratos] = await Promise.all([
      api.get('/roles/'),
      api.get('/contracts/')
    ]);
    cargos.value = resCargos.data;
    contratos.value = resContratos.data;
  } catch {
    mostrarFeedback("Erro ao carregar dados do servidor.", true);
  } finally {
    isLoadingData.value = false;
  }
});

// --- HELPERS ---
const mostrarFeedback = (msg, isErro = false) => {
  mensagem.value = msg;
  erro.value = isErro;
  setTimeout(() => { mensagem.value = ''; }, 4000);
};

const getNomeCargo = (role_id) => {
  const cargo = cargos.value.find(c => c.id === role_id);
  return cargo ? cargo.name : 'Cargo Removido';
};

// --- FLUXO DE UPLOAD ---
const selecionarFicheiro = (event) => {
  formUpload.value.file = event.target.files[0];
};

const fazerUpload = async () => {
  isUploading.value = true;
  mensagem.value = '';
  erro.value = false;
  
  const formData = new FormData();
  formData.append('contract_name', formUpload.value.name);
  formData.append('type', formUpload.value.type);
  if (formUpload.value.type === 'ESPECIFICO') {
    formData.append('role_id', formUpload.value.role_id);
  }
  formData.append('file', formUpload.value.file);

  try {
    await api.post('/contracts/upload/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
    
    mostrarFeedback("Modelo validado e salvo com sucesso!");
    
    // Reseta o formulário
    formUpload.value = { name: '', type: 'UNIVERSAL', role_id: '', file: null };
    if (fileInput.value) fileInput.value.value = ''; // Limpa o input de arquivo visualmente
    
    // Atualiza a tabela
    const resContratos = await api.get('/contracts/');
    contratos.value = resContratos.data;
  } catch (err) {
    mostrarFeedback(err.response?.data?.detail || "Erro ao fazer upload do documento.", true);
  } finally {
    isUploading.value = false;
  }
};

// --- FLUXO DE EXCLUSÃO ---
const confirmarExclusao = (contrato) => {
  contratoParaExcluir.value = contrato;
  erroExclusao.value = '';
  modalExclusaoAberto.value = true;
};

const executarExclusao = async () => {
  isDeleting.value = true;
  erroExclusao.value = '';
  
  try {
    await api.delete(`/contracts/${contratoParaExcluir.value.id}`);
    modalExclusaoAberto.value = false;
    mostrarFeedback('Modelo de contrato excluído permanentemente.');
    
    // Atualiza a tabela
    const resContratos = await api.get('/contracts/');
    contratos.value = resContratos.data;
  } catch (err) {
    erroExclusao.value = err.response?.data?.detail || 'Não foi possível excluir este modelo.';
  } finally {
    isDeleting.value = false;
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
.w-full { width: 100%; }

/* Cards */
.card { background: var(--surface); padding: 1.5rem 2rem; border-radius: 1rem; box-shadow: var(--shadow-sm); border: 1px solid var(--border); transition: box-shadow var(--transition-smooth); }
.card:hover { box-shadow: var(--shadow-md); }

/* Formulários Avançados */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
.input-group { display: flex; flex-direction: column; gap: 0.5rem; }
.btn-full { grid-column: 1 / -1; }
.input-label { font-size: 0.875rem; font-weight: 500; color: var(--text-main); }
.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 1rem; width: 1.25rem; height: 1.25rem; color: var(--text-muted); pointer-events: none; }

.modern-input { width: 100%; padding: 0.75rem 1rem; font-size: 0.95rem; line-height: 1.5; color: var(--text-main); background-color: var(--bg-color); border: 1px solid var(--border); border-radius: 0.5rem; transition: all var(--transition-fast); outline: none; }
.modern-input.with-icon { padding-left: 2.75rem; }
.modern-input:focus { background-color: #fff; border-color: var(--primary); box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1); }
.modern-input:disabled { background-color: #f1f5f9; cursor: not-allowed; opacity: 0.7; }

/* Input de Arquivo Customizado */
.file-input { padding: 0.55rem 1rem 0.55rem 2.75rem; cursor: pointer; color: var(--text-muted); }
.file-input::file-selector-button { background-color: #e2e8f0; border: none; padding: 0.35rem 0.75rem; border-radius: 0.25rem; color: var(--text-main); font-weight: 500; cursor: pointer; transition: background 0.2s; margin-right: 1rem; }
.file-input::file-selector-button:hover { background-color: #cbd5e1; }

/* Botões Modernos */
button { display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; font-weight: 500; font-size: 0.95rem; padding: 0.75rem 1.5rem; border-radius: 0.5rem; border: none; cursor: pointer; transition: all var(--transition-fast); white-space: nowrap; }
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
.feedback-toast { display: flex; align-items: center; gap: 0.5rem; margin-top: 1rem; padding: 0.75rem 1rem; border-radius: 0.5rem; font-size: 0.9rem; font-weight: 500; animation: slideUp 0.3s ease-out; }
.toast-icon { width: 1.25rem; height: 1.25rem; flex-shrink: 0; }
.toast-success { background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.toast-error { background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.feedback-text.error { color: #dc2626; font-size: 0.875rem; font-weight: 500; }

/* Tabela e Cabeçalho */
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.badge { background: #e0e7ff; color: var(--primary-hover); padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; }
.badge-uni { background-color: #e0e7ff; color: #4338ca; padding: 0.25rem 0.6rem; border-radius: 0.375rem; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; }
.badge-esp { background-color: #fce7f3; color: #be185d; padding: 0.25rem 0.6rem; border-radius: 0.375rem; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; }

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
.btn-action.delete:hover { color: #dc2626; background: #fef2f2; border-color: #fecaca; }

/* Empty State e Loading */
.empty-state, .loading-state { padding: 4rem 2rem; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.empty-icon-wrapper { background: #f1f5f9; padding: 1rem; border-radius: 50%; margin-bottom: 1rem; color: var(--text-muted); }
.empty-icon { width: 2rem; height: 2rem; }
.empty-state h3 { margin: 0 0 0.5rem 0; color: var(--text-main); font-size: 1.1rem; }

/* Modais Refinados */
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 1000; padding: 1rem; }
.modal-content { background: white; width: 100%; max-width: 28rem; border-radius: 1rem; padding: 2rem; box-shadow: var(--shadow-lg); position: relative; }
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

/* Responsividade Básica */
@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
}
</style>