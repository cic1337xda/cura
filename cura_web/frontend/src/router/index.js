import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../views/WelcomePage.vue'),
    meta: { guest: true }
  },
  {
    path: '/login',
    component: () => import('../views/LoginPage.vue'),
    meta: { guest: true }
  },
  {
    path: '/dashboard',
    component: () => import('../views/DashboardPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/patients',
    component: () => import('../views/PatientsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/patients/:id',
    component: () => import('../views/PatientDetailPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/doctors',
    component: () => import('../views/DoctorsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/doctors/:id',
    component: () => import('../views/DoctorDetailPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/pharmacy',
    component: () => import('../views/PharmacyPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/prescriptions',
    component: () => import('../views/PrescriptionsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/laboratory',
    component: () => import('../views/LaboratoryPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/vitals',
    component: () => import('../views/VitalsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/medical-records',
    component: () => import('../views/MedicalRecordsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/surgery',
    component: () => import('../views/SurgeryPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/equipment',
    component: () => import('../views/EquipmentPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/vendors',
    component: () => import('../views/VendorsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/accounts',
    component: () => import('../views/AccountsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/payrolls',
    component: () => import('../views/PayrollsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    component: () => import('../views/SettingsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/privacy',
    component: () => import('../views/PrivacyPage.vue'),
    meta: { guest: false }
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('../views/NotFoundPage.vue'),
    meta: { guest: false }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('cura_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.guest && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router