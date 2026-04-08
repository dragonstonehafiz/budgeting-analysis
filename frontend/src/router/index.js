import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import CategoryPage from '../pages/CategoryPage.vue'
import SettingsPage from '../pages/SettingsPage.vue'
import SubscriptionsPage from '../pages/SubscriptionsPage.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',          component: HomePage,     name: 'home' },
    { path: '/category',  component: CategoryPage, name: 'category' },
    { path: '/subscriptions', component: SubscriptionsPage, name: 'subscriptions' },
    { path: '/settings',  component: SettingsPage, name: 'settings' },
  ],
})
