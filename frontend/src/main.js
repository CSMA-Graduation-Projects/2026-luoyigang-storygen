import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
import router from './router'

const app = createApp(App).use(router)

app.config.errorHandler = (err) => {
    console.error("全局错误:", err)
}

app.mount('#app')