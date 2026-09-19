import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@clerk/vue'

/**
 * Application router:
 *  /login        → LoginView    (public, Clerk SignIn)
 *  /register     → RegisterView (public, Clerk SignUp)
 *  /             → HomeView     (protected — the "Research Realm" dashboard)
 *  /realm/:id    → TownExplorerView (protected — the isometric town explorer)
 *
 * Notice the `:catchAll(.*)*` parameter on /login and /register.
 * This allows Clerk's multi-step flows (email verification codes, MFA, OAuth callbacks)
 * to navigate sub-paths without Vue Router throwing a 404.
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login/:catchAll(.*)*',
      alias: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { publicOnly: true },
    },
    {
      path: '/register/:catchAll(.*)*',
      alias: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { publicOnly: true },
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
    // Fallback redirect
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

/**
 * Navigation guard — ensures smooth routing between public and protected views.
 */
router.beforeEach(async (to) => {
  const { isSignedIn, isLoaded } = useAuth()

  // If Clerk is still bootstrapping, wait for it to finish so we have reliable auth state
  if (!isLoaded.value) {
    await new Promise<void>((resolve) => {
      const interval = setInterval(() => {
        if (isLoaded.value) {
          clearInterval(interval)
          resolve()
        }
      }, 20)
    })
  }

  // If page requires auth and user is NOT signed in -> send to /login
  if (to.meta.requiresAuth && !isSignedIn.value) {
    return { name: 'login' }
  }

  // If page is for unauthenticated guests only (login/register) and user IS signed in -> send to home
  if (to.meta.publicOnly && isSignedIn.value) {
    return { name: 'home' }
  }
})

export default router
