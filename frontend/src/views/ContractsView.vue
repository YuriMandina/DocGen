<template>
  <div class="view-container">
    
    <header class="page-header scale-in">
      <div>
        <h1 class="page-title">Gestão e Geração de Contratos</h1>
        <p class="text-muted">Faça upload de modelos Word (.docx) e gere contratos preenchidos automaticamente.</p>
      </div>
    </header>

    <div v-if="isLoadingData" class="loading-state card scale-in">
      <span class="spinner-large"></span>
      <p class="text-muted">Carregando dados do sistema...</p>
    </div>

    <div v-else class="content-wrapper">
      <section class="card scale-in" style="animation-delay: 0.05s;">
        <h2 class="section-title">1. Adicionar Modelo de Contrato</h2>
        <form @submit.prevent="fazerUpload" class="form-grid">
          
          <div class="input-group">
            <label class="input-label">Nome do Contrato</label>
            <div class="input-wrapper">
              <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
              <input v-model="formUpload.name" type="text" placeholder="Ex: Contrato de Experiência" required class="modern-input with-icon" :disabled="isUploading" />
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
              <select v-model="formUpload.role_id" required class="modern-input with-icon" :disabled="isUploading">
                <option v-for="cargo in cargos" :key="cargo.id" :value="cargo.id">{{ cargo.name }}</option>
              </select>
            </div>
          </div>

          <div class="input-group" :class="{'btn-full': formUpload.type !== 'ESPECIFICO'}">
            <label class="input-label">Arquivo Word (.docx)</label>
            <div class="input-wrapper">
              <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" /></svg>
              <input type="file" accept=".docx" @change="selecionarFicheiro" required class="modern-input with-icon file-input" :disabled="isUploading" />
            </div>
          </div>

          <div class="btn-full mt-2">
            <button type="submit" class="btn-primary w-full" :disabled="isUploading || !formUpload.file">
              <span v-if="isUploading" class="spinner"></span>
              <svg v-else class="btn-icon-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
              {{ isUploading ? 'Enviando Documento...' : 'Fazer Upload de Modelo' }}
            </button>
          </div>
        </form>

        <transition name="fade">
          <div v-if="mensagemUpload" class="feedback-toast" :class="erroUpload ? 'toast-error' : 'toast-success'">
            <svg v-if="!erroUpload" class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
            <svg v-else class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            {{ mensagemUpload }}
          </div>
        </transition>
      </section>

      <section class="card scale-in" style="animation-delay: 0.1s;">
        <h2 class="section-title">2. Gerar Contrato Preenchido</h2>
        <form @submit.prevent="gerarContrato" class="form-grid">
          
          <div class="input-group">
            <label class="input-label">Selecionar Funcionário</label>
            <div class="input-wrapper">
              <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
              <select v-model="formGerar.employee_id" required class="modern-input with-icon" :disabled="isGenerating || funcionarios.length === 0">
                <option value="" disabled>{{ funcionarios.length === 0 ? 'Nenhum funcionário cadastrado' : 'Escolha um colaborador' }}</option>
                <option v-for="func in funcionarios" :key="func.id" :value="func.id">{{ func.full_name }} ({{ func.professional_card }})</option>
              </select>
            </div>
          </div>

          <div class="input-group">
            <label class="input-label">Selecionar Modelo de Contrato</label>
            <div class="input-wrapper">
              <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              <select v-model="formGerar.contract_id" required class="modern-input with-icon" :disabled="isGenerating || contratos.length === 0">
                <option value="" disabled>{{ contratos.length === 0 ? 'Faça upload de um modelo primeiro' : 'Escolha o contrato' }}</option>
                <option v-for="contrato in contratos" :key="contrato.id" :value="contrato.id">{{ contrato.contract_name }}</option>
              </select>
            </div>
          </div>

          <div class="input-group btn-full">
            <label class="input-label">Data Personalizada <span class="text-muted font-normal">(Opcional - Em branco usa admissão)</span></label>
            <div class="input-wrapper">
              <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
              <input v-model="formGerar.custom_date" type="date" class="modern-input with-icon" :disabled="isGenerating" />
            </div>
          </div>

          <div class="btn-full mt-2">
            <button type="submit" class="btn-success w-full" :disabled="isGenerating || !formGerar.employee_id || !formGerar.contract_id">
              <span v-if="isGenerating" class="spinner"></span>
              <svg v-else class="btn-icon-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              {{ isGenerating ? 'Processando Documento...' : 'Gerar e Baixar Contrato' }}
            </button>
          </div>
        </form>

        <transition name="fade">
          <div v-if="mensagemGerar && erroGerar" class="feedback-toast toast-error mt-3">
            <svg class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            {{ mensagemGerar }}
          </div>
        </transition>
      </section>
    </div>

    <transition name="modal-fade">
      <div v-if="mostrarModal" class="modal-overlay" @click.self="mostrarModal = false">
        <div class="modal-content text-center">
          <div class="modal-header justify-end">
            <button @click="mostrarModal = false" class="btn-close" aria-label="Fechar">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
          
          <div class="success-icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <h3 class="modal-title">Contrato Gerado!</h3>
          <p class="text-muted mt-2">
            O download do documento <strong>{{ nomeArquivoGerado }}</strong> foi iniciado automaticamente no seu navegador.
          </p>
          
          <div class="modal-actions justify-center mt-4">
            <button @click="mostrarModal = false" class="btn-primary w-full">Entendido</button>
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
const funcionarios = ref([]);
const contratos = ref([]);

const isLoadingData = ref(true);
const isUploading = ref(false);
const isGenerating = ref(false);

const formUpload = ref({ name: '', type: 'UNIVERSAL', role_id: '', file: null });
const formGerar = ref({ employee_id: '', contract_id: '', custom_date: '' });

// Estados de Feedback
const mensagemUpload = ref('');
const erroUpload = ref(false);
const mensagemGerar = ref('');
const erroGerar = ref(false);

// Estados do Modal
const mostrarModal = ref(false);
const nomeArquivoGerado = ref('');

// --- LIFECYCLE ---
onMounted(async () => {
  await buscarDados();
});

// --- MÉTODOS DE API ---
const buscarDados = async () => {
  isLoadingData.value = true;
  try {
    // Promise.all executa as requisições em paralelo (muito mais rápido)
    const [resCargos, resFuncs, resContratos] = await Promise.all([
      api.get('/roles/'),
      api.get('/employees/'),
      api.get('/contracts/')
    ]);
    
    cargos.value = resCargos.data;
    funcionarios.value = resFuncs.data;
    contratos.value = resContratos.data;
  } catch (error) {
    console.error("Erro ao carregar dados", error);
  } finally {
    isLoadingData.value = false;
  }
};

// --- FLUXO DE UPLOAD ---
const selecionarFicheiro = (event) => {
  formUpload.value.file = event.target.files[0];
};

const mostrarFeedbackUpload = (msg, isErro = false) => {
  mensagemUpload.value = msg;
  erroUpload.value = isErro;
  setTimeout(() => { mensagemUpload.value = ''; }, 5000);
};

const fazerUpload = async () => {
  isUploading.value = true;
  mensagemUpload.value = '';
  
  const formData = new FormData();
  formData.append('contract_name', formUpload.value.name);
  formData.append('type', formUpload.value.type);
  if (formUpload.value.type === 'ESPECIFICO') {
    formData.append('role_id', formUpload.value.role_id);
  }
  formData.append('file', formUpload.value.file);

  try {
    await api.post('/contracts/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    mostrarFeedbackUpload("Contrato validado e guardado com sucesso!");
    // Reseta o formulário
    formUpload.value = { name: '', type: 'UNIVERSAL', role_id: '', file: null };
    // Atualiza a lista de contratos disponíveis
    await buscarDados();
  } catch (error) {
    mostrarFeedbackUpload(error.response?.data?.detail || "Erro ao fazer upload do modelo.", true);
  } finally {
    isUploading.value = false;
  }
};

// --- FLUXO DE GERAÇÃO E DOWNLOAD ---
const gerarContrato = async () => {
  isGenerating.value = true;
  mensagemGerar.value = '';
  erroGerar.value = false;

  const payload = { ...formGerar.value };
  if (!payload.custom_date) payload.custom_date = null;

  try {
    // responseType: 'blob' para baixar o arquivo físico
    const response = await api.post('/contracts/generate/', payload, {
      responseType: 'blob'
    });

    // Pega o nome do funcionário para nomear o arquivo de forma inteligente
    const funcSelecionado = funcionarios.value.find(f => f.id === formGerar.value.employee_id);
    const nomeLimpo = funcSelecionado ? funcSelecionado.full_name.replace(/ /g, "_") : "Preenchido";
    nomeArquivoGerado.value = `Contrato_${nomeLimpo}.docx`;

    // Rotina de Download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', nomeArquivoGerado.value);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);

    // Feedback Visual
    mostrarModal.value = true;
    
    // Reseta o formulário parcialmente
    formGerar.value.custom_date = '';

  } catch (error) {
    erroGerar.value = true;
    if (error.response && error.response.data instanceof Blob) {
      const errorText = await error.response.data.text();
      try {
        mensagemGerar.value = JSON.parse(errorText).detail;
      } catch {
        mensagemGerar.value = "Erro desconhecido ao gerar o contrato.";
      }
    } else {
      mensagemGerar.value = "Erro de conexão com o servidor.";
    }
  } finally {
    isGenerating.value = false;
  }
};
</script>

<style scoped>
/* --- VARIÁVEIS E BASE (Padrão Sênior) --- */
:root {
  --transition-fast: 0.2s ease;
  --transition-smooth: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.view-container { display: flex; flex-direction: column; gap: 2rem; padding-bottom: 2rem; max-width: 900px; margin: 0 auto; }
.content-wrapper { display: flex; flex-direction: column; gap: 2rem; }

/* Tipografia e Headers */
.page-header { margin-bottom: 0.5rem; }
.page-title { font-size: 1.8rem; font-weight: 700; color: var(--text-main); margin: 0 0 0.5rem 0; letter-spacing: -0.025em; }
.section-title { font-size: 1.25rem; font-weight: 600; color: var(--text-main); margin: 0 0 1.5rem 0; border-bottom: 2px solid var(--bg-color); padding-bottom: 0.75rem; }
.text-muted { color: var(--text-muted); font-size: 0.95rem; line-height: 1.5; margin: 0; }
.font-normal { font-weight: 400; }
.text-center { text-align: center; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 1rem; }
.mt-4 { margin-top: 1.5rem; }
.w-full { width: 100%; }

/* Cards */
.card { background: var(--surface); padding: 2rem; border-radius: 1rem; box-shadow: var(--shadow-sm); border: 1px solid var(--border); transition: box-shadow var(--transition-smooth); }
.card:hover { box-shadow: var(--shadow-md); }

/* Formulários Avançados (Grid) */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.input-group { display: flex; flex-direction: column; gap: 0.5rem; }
.btn-full { grid-column: 1 / -1; }
.input-label { font-size: 0.875rem; font-weight: 600; color: var(--text-main); }
.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 1rem; width: 1.25rem; height: 1.25rem; color: var(--text-muted); pointer-events: none; }

.modern-input { width: 100%; padding: 0.75rem 1rem; font-size: 0.95rem; line-height: 1.5; color: var(--text-main); background-color: var(--bg-color); border: 1px solid var(--border); border-radius: 0.5rem; transition: all var(--transition-fast); outline: none; }
.modern-input.with-icon { padding-left: 2.75rem; }
.modern-input:focus { background-color: #fff; border-color: var(--primary); box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1); }
.modern-input:disabled { background-color: #f1f5f9; cursor: not-allowed; opacity: 0.7; }

/* Customizando o Input de Arquivo (.docx) */
.file-input { padding: 0.55rem 1rem 0.55rem 2.75rem; cursor: pointer; color: var(--text-muted); }
.file-input::file-selector-button { background-color: #e2e8f0; border: none; padding: 0.35rem 0.75rem; border-radius: 0.25rem; color: var(--text-main); font-weight: 500; cursor: pointer; transition: background 0.2s; margin-right: 1rem; }
.file-input::file-selector-button:hover { background-color: #cbd5e1; }

/* Botões Modernos */
button { display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; font-weight: 500; font-size: 1rem; padding: 0.85rem 1.5rem; border-radius: 0.5rem; border: none; cursor: pointer; transition: all var(--transition-fast); }
button:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
button:disabled { opacity: 0.6; cursor: not-allowed; transform: none !important; box-shadow: none !important; }

.btn-primary { background-color: var(--primary); color: white; box-shadow: var(--shadow-sm); }
.btn-primary:hover:not(:disabled) { background-color: var(--primary-hover); transform: translateY(-1px); box-shadow: var(--shadow-md); }
.btn-success { background-color: var(--secondary); color: white; box-shadow: var(--shadow-sm); }
.btn-success:hover:not(:disabled) { background-color: var(--secondary-hover); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
.btn-icon-svg { width: 1.25rem; height: 1.25rem; }

/* Feedbacks (Toast inline) */
.feedback-toast { display: flex; align-items: center; gap: 0.5rem; margin-top: 1rem; padding: 0.75rem 1rem; border-radius: 0.5rem; font-size: 0.95rem; font-weight: 500; animation: slideUp 0.3s ease-out; }
.toast-icon { width: 1.25rem; height: 1.25rem; flex-shrink: 0; }
.toast-success { background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.toast-error { background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

/* Loading State Inicial */
.loading-state { padding: 4rem 2rem; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }

/* Modais Refinados */
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 1000; padding: 1rem; }
.modal-content { background: white; width: 100%; max-width: 26rem; border-radius: 1rem; padding: 2rem; box-shadow: var(--shadow-lg); position: relative; }
.modal-header { display: flex; justify-content: flex-end; align-items: center; margin-bottom: 0.5rem; }
.modal-title { font-size: 1.5rem; font-weight: 700; color: var(--text-main); margin: 0; }
.btn-close { background: transparent; padding: 0.25rem; border-radius: 0.25rem; color: var(--text-muted); border: none; cursor: pointer; position: absolute; top: 1rem; right: 1rem; }
.btn-close svg { width: 1.5rem; height: 1.5rem; }
.btn-close:hover { background: #f1f5f9; color: var(--text-main); }
.modal-actions { display: flex; gap: 0.75rem; }
.justify-center { justify-content: center; }
.justify-end { justify-content: flex-end; }

/* Ícone de Sucesso no Modal */
.success-icon-wrapper { background: #ecfdf5; color: #10b981; width: 4rem; height: 4rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem auto; animation: bounce 1s ease infinite alternate; }
.success-icon-wrapper svg { width: 2rem; height: 2rem; }

/* Animações Keyframes */
.spinner { width: 1.25rem; height: 1.25rem; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: currentColor; animation: spin 0.8s linear infinite; }
.spinner-large { width: 2.5rem; height: 2.5rem; border: 3px solid #e2e8f0; border-radius: 50%; border-top-color: var(--primary); animation: spin 0.8s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }
.scale-in { animation: scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) backwards; }
@keyframes scaleIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes bounce { from { transform: translateY(0); } to { transform: translateY(-10px); } }

/* Transições do Vue */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.modal-fade-enter-active, .modal-fade-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .modal-content, .modal-fade-leave-to .modal-content { transform: scale(0.95) translateY(10px); }

/* Responsividade Básica */
@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; gap: 1rem; }
}
</style>