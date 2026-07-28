import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '../views/HomePage.vue'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import DrivesPage from '../views/DrivesPage.vue'
import AdminPanel from '../views/AdminPanel.vue'
import AdminSummary from '../views/AdminSummary.vue'
import UserPanel from '../views/UserPanel.vue'
import UserSummary from '../views/UserSummary.vue'
import NotFound from '../views/NotFound.vue'

const routes = [
    { path: '/', name: 'Home', component: HomePage },
    {
        path: '/login',
        name: 'Login',
        component: LoginPage,
        meta: { guestOnly: true }
    },
    {
        path: '/register',
        name: 'Register',
        component: RegisterPage,
        meta: { guestOnly: true }
    },
    {
        path: '/drives',
        name: 'Drives',
        component: DrivesPage,
        meta: { requiresAuth: true }
    },
    {
        path: '/admin',
        name: 'AdminPanel',
        component: AdminPanel,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/admin/summary',
        name: 'AdminSummary',
        component: AdminSummary,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/dashboard',
        name: 'UserPanel',
        component: UserPanel,
        meta: { requiresAuth: true }
    },
    {
        path: '/user/summary',
        name: 'UserSummary',
        component: UserSummary,
        meta: { requiresAuth: true, role: 'student' }
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: NotFound
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('access_token')
    const role = localStorage.getItem('role')

    if (to.meta.requiresAuth && !token) {
        return next('/login')
    }

    if (to.meta.role && to.meta.role !== role) {
        return next('/')
    }

    if (to.meta.guestOnly && token) {
        if (role === 'admin') {
            return next('/admin')
        }
        return next('/dashboard')
    }

    next()
})

export default router
