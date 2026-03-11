import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/features/auth/store/auth.store";

declare module "vue-router" {
  interface RouteMeta {
    requiresAuth?: boolean;
    requiresGuest?: boolean;
    requiresAgent?: boolean;
    requiresMember?: boolean;
    title?: string;
  }
}

const DEFAULT_NAME = "Evently";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/features/auth/components/Auth.vue"),
    meta: { requiresGuest: true, title: "Login" },
  },
  {
    path: "/reset-password",
    name: "reset-password",
    component: () => import("@/features/auth/components/Auth.vue"),
    props: (route) => ({ resetToken: route.query.token || null }),
    meta: { requiresGuest: true },
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () =>
      import("@/features/dashboard/components/DashboardView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/profile",
    name: "profile",
    component: () => import("@/features/profile/components/Profile.vue"),
    meta: { requiresAuth: true, title: "My Profile" },
  },
  {
    path: "/helpdesk",
    name: "helpdesk",
    component: () => import("@/features/helpdesk/components/Helpdesk.vue"),
    meta: { requiresAuth: true, requiresMember: true, title: "Help" },
  },
  {
    path: "/helpdesk/agent",
    name: "helpdesk-agent",
    component: () => import("@/features/helpdesk/components/Agent.vue"),
    meta: { requiresAuth: true, requiresAgent: true, title: "Helpdesk" },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/dashboard",
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (auth.isAuthenticated && !auth.user) await auth.fetchMe();

  const notAuthenticated = to.meta.requiresAuth && !auth.isAuthenticated
  const accessingGuestPage = to.meta.requiresGuest && auth.isAuthenticated
  const accessingMemberPageAsAgent = to.meta.requiresMember && auth.user.is_helpdesk_agent
  const accessingAgentPageAsMember = to.meta.requiresAgent && !auth.user.is_helpdesk_agent

  if (notAuthenticated) {
    return { name: "login" };
  }
  if (accessingGuestPage || accessingMemberPageAsAgent || accessingAgentPageAsMember) {
    return { name: "dashboard" };
  }

  document.title = to.meta.title
    ? `${to.meta.title} | ${DEFAULT_NAME}`
    : DEFAULT_NAME;

  return true;
});

export default router;
