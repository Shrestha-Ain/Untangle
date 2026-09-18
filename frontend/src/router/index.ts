import { createRouter, createWebHistory } from 'vue-router'

/**
 * Application router — three pages:
 *  /login        → LoginView    (public)
 *  /             → HomeView     (protected — the "Research Realm" dashboard)
 *  /realm/:id    → TownExplorerView (protected — the isometric town explorer)
 *
 * createWebHistory() uses the browser History API for clean URLs (no hash).
 * The FastAPI backend doesn't need to handle these routes — Vite's dev server
 * and Nginx/Vercel in production serve index.html for all unknown paths.
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      // No auth required — this is the entry point
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/realm/:documentId',
      name: 'town-explorer',
      component: () => import('@/views/TownExplorerView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

/**
 * Navigation guard — runs before every route change.
 * If the route requires auth and there's no token in localStorage,
 * redirect to /login. Simple and sufficient for v1.
 */
router.beforeEach((to) => {
  const isAuthenticated = !!localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'login' }
  }
})

export default router

