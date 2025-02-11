import { createPinia } from 'pinia' // 引入 Pinia
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from 'vue-router/auto-routes'
import App from './App.vue'

import '@unocss/reset/tailwind.css'
import './styles/main.css'
import 'uno.css'

const app = createApp(App)
const router = createRouter({
  routes,
  // history: createWebHistory(import.meta.env.BASE_URL),
  history: createWebHistory(),
})
app.use(router)
app.use(createPinia()) // 将 Pinia 插件安装到应用中
app.mount('#app')
