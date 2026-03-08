<template>
  <div class="view-container">
    
    <header class="page-header scale-in">
      <div>
        <h1 class="page-title">Gestão de Funcionários</h1>
        <p class="text-muted">Cadastre a equipe e mantenha os dados atualizados para a geração de contratos.</p>
      </div>
    </header>

    <section class="card scale-in" style="animation-delay: 0.05s;">
      <h2 class="section-title">Cadastrar Novo Funcionário</h2>
      <form @submit.prevent="criarFuncionario" class="form-grid">
        
        <div class="input-group">
          <label class="input-label">Nome Completo</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            <input v-model="novoFuncionario.full_name" type="text" placeholder="Nome do colaborador" required class="modern-input with-icon" :disabled="isSubmitting" />
          </div>
        </div>

        <div class="input-group">
          <label class="input-label">Data de Admissão</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
            <input v-model="novoFuncionario.admission_date" type="date" required class="modern-input with-icon" :disabled="isSubmitting" />
          </div>
        </div>

        <div class="input-group">
          <label class="input-label">Cargo</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
            <select v-model="novoFuncionario.role_id" required class="modern-input with-icon" :disabled="isSubmitting || cargos.length === 0">
              <option value="" disabled>{{ cargos.length === 0 ? 'Cadastre um cargo primeiro' : 'Selecione um cargo' }}</option>
              <option v-for="cargo in cargos" :key="cargo.id" :value="cargo.id">{{ cargo.name }}</option>
            </select>
          </div>
        </div>

        <div class="input-group">
          <label class="input-label">Carteira Profissional</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" /></svg>
            <input 
              v-model="novoFuncionario.professional_card" 
              @input="novoFuncionario.professional_card = aplicarMascaraCarteira($event.target.value)"
              type="text" 
              placeholder="00123456/00123-UF"
              pattern="\d{8}/\d{5}-[A-Z]{2}"
              title="Formato exigido: 00123456/00123-UF"
              required 
              class="modern-input with-icon" 
              :disabled="isSubmitting"
            />
          </div>
        </div>

        <div class="btn-full mt-2">
          <button type="submit" class="btn-primary w-full" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner"></span>
            <svg v-else class="btn-icon-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>
            {{ isSubmitting ? 'Salvando...' : 'Adicionar Funcionário' }}
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
        <div>
          <h2 class="section-title m-0">Equipe Cadastrada</h2>
          <span class="badge mt-2">{{ funcionariosFiltrados.length }} registro(s)</span>
        </div>
        
        <div class="search-wrapper">
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          <input v-model="termoBusca" type="text" placeholder="Buscar por nome ou carteira..." class="modern-input search-input" />
        </div>
      </div>
      
      <div class="table-container mt-3">
        <div v-if="isLoadingData" class="loading-state">
          <span class="spinner-large"></span>
          <p class="text-muted">Carregando dados da equipe...</p>
        </div>

        <table v-else class="modern-table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Cargo</th>
              <th>Admissão</th>
              <th>Carteira Profissional</th>
              <th class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="funcionariosFiltrados.length === 0">
              <td colspan="5">
                <div class="empty-state">
                  <div class="empty-icon-wrapper">
                    <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                  </div>
                  <h3>{{ termoBusca ? 'Nenhum resultado encontrado' : 'Equipe vazia' }}</h3>
                  <p class="text-muted">
                    {{ termoBusca ? `Não encontramos ninguém com o termo "${termoBusca}".` : 'Comece cadastrando um funcionário no formulário acima.' }}
                  </p>
                </div>
              </td>
            </tr>
            <tr v-for="func in funcionariosFiltrados" :key="func.id" class="table-row">
              <td class="font-medium">{{ func.full_name }}</td>
              <td class="text-muted">{{ getNomeCargo(func.role_id) }}</td>
              <td>{{ formatarDataPt(func.admission_date) }}</td>
              <td class="font-mono">{{ func.professional_card }}</td>
              <td class="actions-cell">
                <button @click="abrirModalEdicao(func)" class="btn-action edit" aria-label="Editar" title="Editar">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                </button>
                <button @click="confirmarExclusao(func)" class="btn-action delete" aria-label="Excluir" title="Excluir">
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
        <div class="modal-content" style="max-width: 600px;">
          <div class="modal-header">
            <h3>Editar Funcionário</h3>
            <button @click="fecharModalEdicao" class="btn-close" aria-label="Fechar">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
          
          <form @submit.prevent="salvarEdicao" class="form-grid mt-3">
            <div class="input-group btn-full">
              <label class="input-label">Nome Completo</label>
              <input v-model="funcEmEdicao.full_name" type="text" required class="modern-input" :disabled="isSubmitting" />
            </div>
            <div class="input-group">
              <label class="input-label">Data de Admissão</label>
              <input v-model="funcEmEdicao.admission_date" type="date" required class="modern-input" :disabled="isSubmitting" />
            </div>
            <div class="input-group">
              <label class="input-label">Cargo</label>
              <select v-model="funcEmEdicao.role_id" required class="modern-input" :disabled="isSubmitting">
                <option v-for="cargo in cargos" :key="cargo.id" :value="cargo.id">{{ cargo.name }}</option>
              </select>
            </div>
            <div class="input-group btn-full">
              <label class="input-label">Carteira Profissional</label>
              <input 
                v-model="funcEmEdicao.professional_card" 
                @input="funcEmEdicao.professional_card = aplicarMascaraCarteira($event.target.value)"
                type="text" 
                placeholder="00123456/00123-UF"
                pattern="\d{8}/\d{5}-[A-Z]{2}"
                title="Formato exigido: 00123456/00123-UF"
                required 
                class="modern-input" 
                :disabled="isSubmitting"
              />
            </div>
            
            <div class="btn-full">
              <p v-if="erroModal" class="feedback-text error mt-2">{{ erroModal }}</p>
            </div>

            <div class="modal-actions btn-full mt-3">
              <button type="button" @click="fecharModalEdicao" class="btn-ghost" :disabled="isSubmitting">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="isSubmitting">
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
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7a4 4 0 11-8 0 4 4 0 018 0zM9 14a6 6 0 00-6 6v1h12v-1a6 6 0 00-6-6zM21 12h-6" /></svg>
          </div>
          <h3>Remover da Equipe?</h3>
          <p class="text-muted text-center mt-2">
            Tem certeza que deseja excluir <strong>{{ funcParaExcluir?.full_name }}</strong> do sistema?<br>
            Esta ação não poderá ser desfeita.
          </p>
          
          <p v-if="erroExclusao" class="feedback-text error mt-2 text-center">{{ erroExclusao }}</p>
          
          <div class="modal-actions justify-center mt-4">
            <button @click="modalExclusaoAberto = false" class="btn-ghost" :disabled="isSubmitting">Cancelar</button>
            <button @click="executarExclusao" class="btn-danger" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner"></span>
              {{ isSubmitting ? 'Excluindo...' : 'Sim, remover' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../services/api';

// --- ESTADOS GLOBAIS ---
const cargos = ref([]);
const funcionarios = ref([]);
const termoBusca = ref('');
const isLoadingData = ref(true);
const isSubmitting = ref(false);

const novoFuncionario = ref({ full_name: '', admission_date: '', role_id: '', professional_card: '' });
const mensagem = ref('');
const erro = ref(false);

// Estados Edição
const modalAberto = ref(false);
const funcEmEdicao = ref({});
const erroModal = ref('');

// Estados Exclusão
const modalExclusaoAberto = ref(false);
const funcParaExcluir = ref(null);
const erroExclusao = ref('');

// --- LIFECYCLE ---
onMounted(async () => {
  isLoadingData.value = true;
  await Promise.all([buscarCargos(), buscarFuncionarios()]);
  isLoadingData.value = false;
});

// --- FUNÇÃO DA MÁSCARA INTELIGENTE ---
const aplicarMascaraCarteira = (valor) => {
  if (!valor) return '';
  
  // 1. Remove qualquer coisa que não seja Letra ou Número e já converte para Maiúsculo
  let v = valor.toUpperCase().replace(/[^A-Z0-9]/g, '');
  
  // 2. Separa a string para garantir a integridade dos blocos
  let numeros = v.replace(/[^0-9]/g, ''); // Garante que a primeira parte seja só números
  let p1 = numeros.substring(0, 8);
  let p2 = numeros.substring(8, 13);
  
  // Extrai as letras (a UF do estado), permitindo que só sejam digitadas letras
  let letras = v.substring(numeros.length).replace(/[^A-Z]/g, '').substring(0, 2);

  // 3. Reconstrói a string final inserindo os símbolos
  let formatado = p1;
  
  // Se passou de 8 números, coloca a barra
  if (numeros.length > 8) {
    formatado += '/' + p2;
  }
  
  // Se já preencheu os 13 números e começou a digitar letras, coloca o traço
  if (numeros.length >= 13 && letras.length > 0) {
    formatado += '-' + letras;
  }
  
  return formatado;
};

// --- HELPERS ---
const mostrarFeedback = (msg, isErro = false) => {
  mensagem.value = msg;
  erro.value = isErro;
  setTimeout(() => { mensagem.value = ''; }, 4000);
};

// --- MÉTODOS DE API ---
const buscarCargos = async () => {
  try {
    const res = await api.get('/roles/');
    cargos.value = res.data;
  } catch (err) {
    console.error('Erro ao buscar cargos:', err);
  }
};

const buscarFuncionarios = async () => {
  try {
    const res = await api.get('/employees/');
    funcionarios.value = res.data;
  } catch (err) {
    console.error('Erro ao buscar funcionários:', err);
  }
};

// --- COMPUTADAS E FORMATADORES ---
const funcionariosFiltrados = computed(() => {
  if (!termoBusca.value) return funcionarios.value;
  const termo = termoBusca.value.toLowerCase();
  return funcionarios.value.filter(f => 
    f.full_name.toLowerCase().includes(termo) || 
    f.professional_card.toLowerCase().includes(termo)
  );
});

const getNomeCargo = (role_id) => {
  const cargo = cargos.value.find(c => c.id === role_id);
  return cargo ? cargo.name : 'Cargo não encontrado';
};

const formatarDataPt = (dataString) => {
  if (!dataString) return '--/--/----';
  const [ano, mes, dia] = dataString.split('-');
  return `${dia}/${mes}/${ano}`;
};

// --- FLUXO DE CADASTRO ---
const criarFuncionario = async () => {
  isSubmitting.value = true;
  mensagem.value = '';
  
  try {
    await api.post('/employees/', novoFuncionario.value);
    novoFuncionario.value = { full_name: '', admission_date: '', role_id: '', professional_card: '' };
    mostrarFeedback('Funcionário cadastrado com sucesso!');
    await buscarFuncionarios();
  } catch (err) {
    mostrarFeedback(err.response?.data?.detail || 'Erro ao cadastrar funcionário.', true);
  } finally {
    isSubmitting.value = false;
  }
};

// --- FLUXO DE EDIÇÃO ---
const abrirModalEdicao = (func) => {
  funcEmEdicao.value = { ...func };
  erroModal.value = '';
  modalAberto.value = true;
};

const fecharModalEdicao = () => {
  modalAberto.value = false;
  erroModal.value = '';
};

const salvarEdicao = async () => {
  isSubmitting.value = true;
  erroModal.value = '';
  
  try {
    await api.put(`/employees/${funcEmEdicao.value.id}`, funcEmEdicao.value);
    fecharModalEdicao();
    mostrarFeedback('Dados atualizados com sucesso!');
    await buscarFuncionarios();
  } catch (err) {
    erroModal.value = err.response?.data?.detail || 'Erro ao editar dados do funcionário.';
  } finally {
    isSubmitting.value = false;
  }
};

// --- FLUXO DE EXCLUSÃO ---
const confirmarExclusao = (func) => {
  funcParaExcluir.value = func;
  erroExclusao.value = '';
  modalExclusaoAberto.value = true;
};

const executarExclusao = async () => {
  isSubmitting.value = true;
  erroExclusao.value = '';
  
  try {
    await api.delete(`/employees/${funcParaExcluir.value.id}`);
    modalExclusaoAberto.value = false;
    mostrarFeedback('Funcionário removido com sucesso!');
    await buscarFuncionarios();
  } catch (err) {
    erroExclusao.value = err.response?.data?.detail || 'Não foi possível remover este funcionário.';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* --- VARIÁVEIS E BASE (Igual ao RolesView para manter o padrão) --- */
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
.font-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.9em; letter-spacing: 0.05em; color: var(--text-muted); }
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

/* Formulários Avançados (Grid) */
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

/* Tabela, Header e Busca */
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 1rem; }
.search-wrapper { position: relative; width: 100%; max-width: 320px; }
.search-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); width: 1.25rem; height: 1.25rem; color: var(--text-muted); }
.search-input { padding-left: 2.75rem; border-radius: 999px; }
.badge { background: #e0e7ff; color: var(--primary-hover); padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; display: inline-block; }

.table-container { border: 1px solid var(--border); border-radius: 0.75rem; overflow-x: auto; background: white; }
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
.modal-content { background: white; width: 100%; border-radius: 1rem; padding: 2rem; box-shadow: var(--shadow-lg); position: relative; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.modal-header h3 { margin: 0; font-size: 1.25rem; font-weight: 600; color: var(--text-main); }
.btn-close { background: transparent; padding: 0.25rem; border-radius: 0.25rem; color: var(--text-muted); position: absolute; top: 1.5rem; right: 1.5rem; }
.btn-close svg { width: 1.5rem; height: 1.5rem; }
.btn-close:hover { background: #f1f5f9; color: var(--text-main); }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1rem; }
.justify-center { justify-content: center; }

/* Modal de Exclusão Específico */
.danger-modal { text-align: center; max-width: 28rem; }
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
  .table-header { flex-direction: column; align-items: flex-start; }
  .search-wrapper { max-width: 100%; }
}
</style>