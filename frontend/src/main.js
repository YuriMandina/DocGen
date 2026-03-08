// frontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Importamos o router que acabámos de criar

const app = createApp(App)

app.use(router) // Dizemos ao Vue para usar as rotas
app.mount('#app')