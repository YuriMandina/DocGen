<template>
  <div class="auth-container scale-in">
    <div class="card auth-card">
      <div class="text-center mb-4">
        <h1 class="page-title">Criar Conta DocGen</h1>
        <p class="text-muted">Cadastre-se e gerencie os contratos da sua empresa.</p>
      </div>

      <form @submit.prevent="registrar" class="form-grid">
        <div class="section-divider btn-full"><span>Seus Dados Pessoais</span></div>
        
        <div class="input-group btn-full">
          <label class="input-label">Nome Completo</label>
          <input v-model="form.full_name" type="text" required class="modern-input" :disabled="isLoading" placeholder="Como devemos chamar você?" />
        </div>

        <div class="input-group">
          <label class="input-label">CPF</label>
          <input v-model="form.cpf" @input="form.cpf = mascaraCPF($event.target.value)" type="text" required class="modern-input" :disabled="isLoading" placeholder="000.000.000-00" maxlength="14" />
        </div>

        <div class="input-group">
          <label class="input-label">E-mail Corporativo</label>
          <input v-model="form.username" type="email" required class="modern-input" :disabled="isLoading" placeholder="voce@empresa.com.br" />
        </div>

        <div class="input-group btn-full">
          <label class="input-label">Senha Segura</label>
          <input v-model="form.password" type="password" required class="modern-input" :disabled="isLoading" minlength="8" placeholder="Mínimo de 8 caracteres" />
        </div>

        <div class="input-group btn-full">
          <label class="input-label">Confirmar Senha</label>
          <input v-model="form.password_confirm" type="password" required class="modern-input" :disabled="isLoading" minlength="8" placeholder="Digite a senha novamente" />
        </div>

        <div class="section-divider btn-full mt-3"><span>Dados da sua Empresa</span></div>
        <p class="text-muted btn-full" style="font-size: 0.8rem; margin-top: -10px;">
          Se for o primeiro cadastro deste CNPJ, você será automaticamente o <strong>Administrador (Master)</strong>.
        </p>

        <div class="input-group btn-full">
          <label class="input-label">Razão Social / Nome Fantasia</label>
          <input v-model="form.company_name" type="text" required class="modern-input" :disabled="isLoading" placeholder="Nome da sua empresa" />
        </div>

        <div class="input-group btn-full">
          <label class="input-label">CNPJ</label>
          <input v-model="form.cnpj" @input="form.cnpj = mascaraCNPJ($event.target.value)" type="text" required class="modern-input" :disabled="isLoading" placeholder="00.000.000/0000-00" maxlength="18" />
        </div>

        <div v-if="erro" class="btn-full feedback-toast toast-error mt-2">
          {{ erro }}
        </div>

        <div class="btn-full mt-4">
          <button type="submit" class="btn-primary w-full" :disabled="isLoading">
            <span v-if="isLoading" class="spinner"></span>
            {{ isLoading ? 'Criando conta...' : 'Registrar Conta' }}
          </button>
        </div>
      </form>

      <div class="text-center mt-4">
        <p class="text-muted">Já possui conta? <router-link to="/login" class="link-primary">Faça login aqui</router-link>.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const isLoading = ref(false);
const erro = ref('');

const form = ref({
  full_name: '', cpf: '', username: '', password: '', password_confirm: '', company_name: '', cnpj: ''
});

// Máscaras de Input
const mascaraCPF = (v) => {
  v = v.replace(/\D/g, "");
  if (v.length <= 11) {
    v = v.replace(/(\d{3})(\d)/, "$1.$2");
    v = v.replace(/(\d{3})(\d)/, "$1.$2");
    v = v.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
  }
  return v;
};

const mascaraCNPJ = (v) => {
  v = v.replace(/\D/g, "");
  if (v.length <= 14) {
    v = v.replace(/^(\d{2})(\d)/, "$1.$2");
    v = v.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
    v = v.replace(/\.(\d{3})(\d)/, ".$1/$2");
    v = v.replace(/(\d{4})(\d)/, "$1-$2");
  }
  return v;
};

const registrar = async () => {
  if (form.value.password !== form.value.password_confirm) {
    erro.value = 'As senhas digitadas não coincidem. Verifique e tente novamente.';
    return;
  }

  isLoading.value = true;
  erro.value = '';
  
  try {
    await api.post('/auth/register', form.value);
    alert('Conta criada com sucesso! Faça o login.');
    router.push('/login');
  } catch (err) {
    // Tratamento para exibir o erro do model_validator do Pydantic de forma amigável
    if (err.response?.data?.detail && Array.isArray(err.response.data.detail)) {
        erro.value = err.response.data.detail[0].msg.replace("Value error, ", "");
    } else {
        erro.value = err.response?.data?.detail || 'Erro ao processar o registro. Verifique os dados.';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; padding: 2rem 1rem; }
.card { background: var(--surface, #ffffff); padding: 2.5rem; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); border: 1px solid var(--border, #e2e8f0); }
.auth-card { max-width: 550px; width: 100%; }

.mb-4 { margin-bottom: 1.5rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 1rem; }
.mt-4 { margin-top: 1.5rem; }
.text-center { text-align: center; }
.page-title { font-size: 1.8rem; font-weight: 700; color: var(--text-main, #0f172a); margin: 0 0 0.5rem 0; letter-spacing: -0.025em; }
.text-muted { color: var(--text-muted, #64748b); font-size: 0.95rem; line-height: 1.5; margin: 0; }

.section-divider { display: flex; align-items: center; text-align: center; color: var(--text-muted); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin: 1.5rem 0 0.5rem 0; }
.section-divider::before, .section-divider::after { content: ''; flex: 1; border-bottom: 1px solid var(--border, #e2e8f0); }
.section-divider::before { margin-right: 1em; }
.section-divider::after { margin-left: 1em; }

/* Formulários */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
.input-group { display: flex; flex-direction: column; gap: 0.5rem; }
.btn-full { grid-column: 1 / -1; }
.input-label { font-size: 0.875rem; font-weight: 600; color: var(--text-main, #0f172a); text-align: left; }
.input-wrapper { position: relative; display: flex; align-items: center; }

.modern-input { width: 100%; padding: 0.75rem 1rem; font-size: 0.95rem; line-height: 1.5; color: var(--text-main); background-color: var(--bg-color, #f8fafc); border: 1px solid var(--border, #e2e8f0); border-radius: 0.5rem; transition: all 0.2s ease; outline: none; box-sizing: border-box; }
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

/* Spinner e Animações */
.spinner { width: 1.25rem; height: 1.25rem; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: white; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.scale-in { animation: scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) backwards; }
@keyframes scaleIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }

/* Feedbacks */
.feedback-toast { padding: 0.75rem 1rem; border-radius: 0.5rem; font-size: 0.9rem; font-weight: 500; text-align: center; }
.toast-error { background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

/* Responsivo para telas menores */
@media (max-width: 600px) {
  .form-grid { grid-template-columns: 1fr; }
}
</style>