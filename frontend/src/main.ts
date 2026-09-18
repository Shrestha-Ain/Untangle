import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Import Tailwind CSS (processes through PostCSS → Vite)
import './style.css'

/**
 * App bootstrap order:
 * 1. createApp(App) — creates the Vue application instance
 * 2. use(createPinia()) — registers Pinia for global state management
 * 3. use(router) — registers Vue Router for navigation
 * 4. mount('#app') — attaches to the <div id="app"> in index.html
 *
 * Pinia MUST be registered before the router because route guards
 * (and lazy-loaded components) may access stores on first navigation.
 */
const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
