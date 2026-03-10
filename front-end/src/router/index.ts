import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/features/auth/store/auth.store'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    requiresGuest?: boolean
    title?: string
  }
}

const DEFAULT_NAME = "Evently"

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/features/auth/components/Auth.vue'),
    meta: { requiresGuest: true, title: "Login" },
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: () => import('@/features/auth/components/Auth.vue'),
    props: (route) => ({ resetToken: route.query.token || null }),
    meta: { requiresGuest: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/features/dashboard/components/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/features/profile/components/Profile.vue'),
    meta: { requiresAuth: true },
  },
  /*
  {
    path: '/users',
    name: 'users',
    component: () => import('@/features/users/components/UsersView.vue'),
    meta: { requiresAuth: true },
  },
  */
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.meta.requiresGuest && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }

  document.title = to.meta.title? `${to.meta.title} | ${DEFAULT_NAME}` : DEFAULT_NAME;

  if (auth.isAuthenticated && !auth.user) auth.fetchMe()

  return true
})

export default router