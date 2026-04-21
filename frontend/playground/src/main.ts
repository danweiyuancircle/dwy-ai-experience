import './app.css'
import 'vue-sonner/style.css'
import { createApp } from 'vue'
import EUI from '@dwydev/eui'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(EUI)
app.use(router)
app.mount('#app')
