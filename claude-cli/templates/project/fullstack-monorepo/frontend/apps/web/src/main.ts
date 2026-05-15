import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { EUI } from '@dwydev/eui'

import App from './App.vue'
import router from './router'

import '@dwydev/eui/theme/tokens.css'
import './index.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(EUI)

app.mount('#app')
