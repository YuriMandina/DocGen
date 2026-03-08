<template>
  <div class="view-container">
    
    <header class="page-header scale-in">
      <div>
        <h1 class="page-title">Gerador de Contratos</h1>
        <p class="text-muted">Selecione o colaborador e os modelos desejados. O sistema irá gerar todos os documentos selecionados de uma só vez.</p>
      </div>
    </header>

    <div v-if="isLoadingData" class="loading-state card scale-in">
      <span class="spinner-large"></span>
      <p class="text-muted">Carregando dados do sistema...</p>
    </div>

    <section v-else class="card scale-in" style="animation-delay: 0.05s;">
      
      <form @submit.prevent="gerarContratosEmLote" class="form-grid">
        
        <div class="input-group">
          <label class="input-label">1. Selecionar Funcionário</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            <select v-model="formGerar.employee_id" required class="modern-input with-icon" :disabled="estaGerando || funcionarios.length === 0">
              <option value="" disabled>{{ funcionarios.length === 0 ? 'Nenhum funcionário cadastrado' : 'Escolha um funcionário na lista' }}</option>
              <option v-for="func in funcionarios" :key="func.id" :value="func.id">
                {{ func.full_name }} ({{ func.professional_card }})
              </option>
            </select>
          </div>
        </div>

        <div class="input-group btn-full">
          <div class="flex-between">
            <label class="input-label">2. Selecionar Modelos de Contrato</label>
            <button v-if="contratosDisponiveis.length > 0" type="button" class="btn-text-only" @click="selecionarTodos" :disabled="estaGerando">
              {{ todosSelecionados ? 'Desmarcar Todos' : 'Selecionar Todos' }}
            </button>
          </div>
          
          <div v-if="!formGerar.employee_id" class="empty-selection-box">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" /></svg>
            <p>Selecione um funcionário no passo 1 para ver os modelos disponíveis.</p>
          </div>
          
          <div v-else-if="contratosDisponiveis.length === 0" class="empty-selection-box">
            <p>Nenhum modelo de contrato compatível com o cargo deste funcionário.</p>
          </div>

          <div v-else class="checkbox-grid">
            <label 
              v-for="contrato in contratosDisponiveis" 
              :key="contrato.id" 
              class="checkbox-card" 
              :class="{ 'selected': formGerar.contract_ids.includes(contrato.id), 'disabled': estaGerando }"
            >
              <input 
                type="checkbox" 
                :value="contrato.id" 
                v-model="formGerar.contract_ids" 
                class="sr-only" 
                :disabled="estaGerando"
              />
              <div class="check-box-ui">
                <svg v-if="formGerar.contract_ids.includes(contrato.id)" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
              </div>
              <div class="contract-info">
                <span class="contract-name">{{ contrato.contract_name }}</span>
                <span class="contract-type">{{ contrato.type === 'UNIVERSAL' ? 'Universal' : 'Específico' }}</span>
              </div>
            </label>
          </div>
        </div>

        <div class="input-group btn-full mt-2">
          <label class="input-label">
            3. Data Impressa nos Contratos
          </label>
          <p class="date-hint">Deixe em branco para utilizar automaticamente a <strong>Data de Admissão</strong> do colaborador, ou selecione uma data personalizada abaixo:</p>
          <div class="input-wrapper" style="max-width: 300px;">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
            <input v-model="formGerar.custom_date" type="date" class="modern-input with-icon" :disabled="estaGerando" />
          </div>
        </div>

        <div class="btn-full mt-4">
          <button type="submit" class="btn-success w-full generate-btn" :disabled="estaGerando || !formGerar.employee_id || formGerar.contract_ids.length === 0">
            <span v-if="estaGerando" class="spinner"></span>
            <svg v-else class="btn-icon-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            {{ estaGerando ? `Processando ${formGerar.contract_ids.length} documento(s)...` : `Gerar e Baixar ${formGerar.contract_ids.length > 0 ? formGerar.contract_ids.length : ''} Contrato(s)` }}
          </button>
        </div>
      </form>

      <transition name="fade">
        <div v-if="mensagemErro" class="feedback-toast toast-error mt-4">
          <svg class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          {{ mensagemErro }}
        </div>
      </transition>
    </section>

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
          <h3 class="modal-title">Lote Concluído!</h3>
          <p class="text-muted mt-2">
            <strong>{{ qtdGerada }} documento(s)</strong> gerados e baixados com sucesso para <strong>{{ nomeFuncionarioGerado }}</strong>.
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
import { ref, computed, onMounted, watch } from 'vue';
import api from '../services/api';

// --- ESTADOS GLOBAIS ---
const funcionarios = ref([]);
const contratos = ref([]);
// Repare que contract_id virou contract_ids (array)
const formGerar = ref({ employee_id: '', contract_ids: [], custom_date: '' });

const isLoadingData = ref(true);
const estaGerando = ref(false);
const mensagemErro = ref('');

const mostrarModal = ref(false);
const nomeFuncionarioGerado = ref('');
const qtdGerada = ref(0);

// --- LIFECYCLE ---
onMounted(async () => {
  isLoadingData.value = true;
  try {
    const [resFuncs, resContratos] = await Promise.all([
      api.get('/employees/'),
      api.get('/contracts/')
    ]);
    funcionarios.value = resFuncs.data;
    contratos.value = resContratos.data;
  } catch {
    mensagemErro.value = "Não foi possível carregar os dados. Verifique sua conexão.";
  } finally {
    isLoadingData.value = false;
  }
});

// --- LÓGICA DE SELEÇÃO E FILTROS ---
const contratosDisponiveis = computed(() => {
  if (!formGerar.value.employee_id) return [];
  
  const funcSelecionado = funcionarios.value.find(f => f.id === formGerar.value.employee_id);
  if (!funcSelecionado) return [];

  return contratos.value.filter(c => 
    c.type === 'UNIVERSAL' || c.role_id === funcSelecionado.role_id
  );
});

// Reseta a seleção de contratos caso o usuário mude o funcionário
watch(() => formGerar.value.employee_id, () => {
  formGerar.value.contract_ids = [];
});

const todosSelecionados = computed(() => {
  return contratosDisponiveis.value.length > 0 && 
         formGerar.value.contract_ids.length === contratosDisponiveis.value.length;
});

const selecionarTodos = () => {
  if (todosSelecionados.value) {
    formGerar.value.contract_ids = [];
  } else {
    formGerar.value.contract_ids = contratosDisponiveis.value.map(c => c.id);
  }
};

// --- FLUXO DE GERAÇÃO EM LOTE ---
const gerarContratosEmLote = async () => {
  estaGerando.value = true;
  mensagemErro.value = '';

  const funcSelecionado = funcionarios.value.find(f => f.id === formGerar.value.employee_id);
  nomeFuncionarioGerado.value = funcSelecionado ? funcSelecionado.full_name : 'Colaborador';
  const nomeLimpoFunc = nomeFuncionarioGerado.value.replace(/ /g, "_");

  const payload = {
    employee_id: formGerar.value.employee_id,
    contract_ids: formGerar.value.contract_ids,
    custom_date: formGerar.value.custom_date || null,
  };

  try {
    const response = await api.post('/contracts/generate-batch/', payload, { responseType: 'blob' });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Contratos_${nomeLimpoFunc}.zip`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    
    qtdGerada.value = formGerar.value.contract_ids.length;
    mostrarModal.value = true;
    formGerar.value = { employee_id: '', contract_ids: [], custom_date: '' }; // Limpa o formulário

  } catch (error) {
    if (error.response && error.response.data instanceof Blob) {
      const errorText = await error.response.data.text();
      try {
        mensagemErro.value = JSON.parse(errorText).detail;
      } catch {
        mensagemErro.value = "Ocorreu um erro desconhecido ao gerar o arquivo ZIP.";
      }
    } else {
      mensagemErro.value = error.response?.data?.detail || "Não foi possível gerar o arquivo ZIP. Verifique a conexão.";
    }
  } finally {
    estaGerando.value = false;
  }
};
</script>

<style scoped>
/* --- VARIÁVEIS E BASE --- */
:root {
  --transition-fast: 0.2s ease;
  --transition-smooth: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.view-container { display: flex; flex-direction: column; gap: 2rem; padding-bottom: 2rem; max-width: 800px; margin: 0 auto; }

/* Tipografia e Headers */
.page-header { margin-bottom: 0.5rem; }
.page-title { font-size: 1.8rem; font-weight: 700; color: var(--text-main); margin: 0 0 0.5rem 0; letter-spacing: -0.025em; }
.text-muted { color: var(--text-muted); font-size: 0.95rem; line-height: 1.5; margin: 0; }
.text-center { text-align: center; }
.mt-2 { margin-top: 0.75rem; }
.mt-4 { margin-top: 1.5rem; }
.w-full { width: 100%; }
.flex-between { display: flex; justify-content: space-between; align-items: flex-end; }

/* Cards */
.card { background: var(--surface); padding: 2.5rem; border-radius: 1rem; box-shadow: var(--shadow-sm); border: 1px solid var(--border); transition: box-shadow var(--transition-smooth); }
.card:hover { box-shadow: var(--shadow-md); }

/* Formulários Avançados (Grid) */
.form-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
.input-group { display: flex; flex-direction: column; gap: 0.5rem; }
.btn-full { grid-column: 1 / -1; }
.input-label { font-size: 1rem; font-weight: 600; color: var(--text-main); }
.date-hint { font-size: 0.85rem; color: var(--text-muted); margin-top: -0.25rem; margin-bottom: 0.5rem; }
.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 1rem; width: 1.25rem; height: 1.25rem; color: var(--text-muted); pointer-events: none; }

.modern-input { width: 100%; padding: 0.75rem 1rem; font-size: 0.95rem; line-height: 1.5; color: var(--text-main); background-color: var(--bg-color); border: 1px solid var(--border); border-radius: 0.5rem; transition: all var(--transition-fast); outline: none; }
.modern-input.with-icon { padding-left: 2.75rem; }
.modern-input:focus { background-color: #fff; border-color: var(--primary); box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1); }
.modern-input:disabled { background-color: #f1f5f9; cursor: not-allowed; opacity: 0.7; }

/* CHECKBOX UI (CARDS CLICÁVEIS) */
.empty-selection-box { border: 2px dashed var(--border); border-radius: 0.75rem; padding: 2rem; text-align: center; color: var(--text-muted); background: #f8fafc; font-size: 0.9rem; display: flex; flex-direction: column; align-items: center; gap: 0.5rem; }
.empty-selection-box svg { width: 2rem; height: 2rem; color: #94a3b8; }

.checkbox-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin-top: 0.5rem; }
.checkbox-card { display: flex; align-items: flex-start; gap: 0.75rem; padding: 1rem; border: 2px solid var(--border); border-radius: 0.75rem; cursor: pointer; transition: all var(--transition-fast); background-color: var(--surface); user-select: none; }
.checkbox-card:hover:not(.disabled) { border-color: #cbd5e1; background-color: #f8fafc; }
.checkbox-card.selected { border-color: var(--primary); background-color: #eef2ff; }
.checkbox-card.disabled { opacity: 0.6; cursor: not-allowed; }

.check-box-ui { width: 1.25rem; height: 1.25rem; flex-shrink: 0; border: 2px solid #cbd5e1; border-radius: 0.25rem; display: flex; align-items: center; justify-content: center; transition: all var(--transition-fast); margin-top: 0.1rem; }
.checkbox-card.selected .check-box-ui { background-color: var(--primary); border-color: var(--primary); color: white; }
.contract-info { display: flex; flex-direction: column; }
.contract-name { font-weight: 600; font-size: 0.95rem; color: var(--text-main); line-height: 1.2; }
.contract-type { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; }

.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border-width: 0; }
.btn-text-only { background: none; border: none; color: var(--primary); font-size: 0.85rem; font-weight: 600; cursor: pointer; padding: 0; transition: color var(--transition-fast); }
.btn-text-only:hover { color: var(--primary-hover); text-decoration: underline; }

/* Botões Modernos */
button { display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; font-weight: 500; font-size: 1.05rem; padding: 1rem 1.5rem; border-radius: 0.5rem; border: none; cursor: pointer; transition: all var(--transition-fast); }
button:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
button:disabled { opacity: 0.6; cursor: not-allowed; transform: none !important; box-shadow: none !important; }

.btn-primary { background-color: var(--primary); color: white; box-shadow: var(--shadow-sm); }
.btn-primary:hover:not(:disabled) { background-color: var(--primary-hover); transform: translateY(-1px); box-shadow: var(--shadow-md); }
.btn-success { background-color: var(--secondary); color: white; box-shadow: var(--shadow-sm); }
.btn-success:hover:not(:disabled) { background-color: var(--secondary-hover); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
.btn-icon-svg { width: 1.25rem; height: 1.25rem; }
.generate-btn { font-weight: 600; letter-spacing: 0.025em; }

/* Feedbacks (Toast) */
.feedback-toast { display: flex; align-items: center; gap: 0.5rem; margin-top: 1rem; padding: 0.75rem 1rem; border-radius: 0.5rem; font-size: 0.95rem; font-weight: 500; animation: slideUp 0.3s ease-out; justify-content: center; }
.toast-icon { width: 1.25rem; height: 1.25rem; flex-shrink: 0; }
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

/* Ícone de Sucesso */
.success-icon-wrapper { background: #ecfdf5; color: #10b981; width: 4rem; height: 4rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem auto; animation: bounce 1s ease infinite alternate; }
.success-icon-wrapper svg { width: 2rem; height: 2rem; }

/* Animações */
.spinner { width: 1.25rem; height: 1.25rem; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: currentColor; animation: spin 0.8s linear infinite; }
.spinner-large { width: 2.5rem; height: 2.5rem; border: 3px solid #e2e8f0; border-radius: 50%; border-top-color: var(--primary); animation: spin 0.8s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }
.scale-in { animation: scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) backwards; }
@keyframes scaleIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes bounce { from { transform: translateY(0); } to { transform: translateY(-10px); } }
.modal-fade-enter-active, .modal-fade-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; transform: scale(0.95) translateY(10px); }
</style>