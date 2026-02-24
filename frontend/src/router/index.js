import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import CategoryPage from '../pages/CategoryPage.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',          component: HomePage,     name: 'home' },
    { path: '/category',  component: CategoryPage, name: 'category' },
  ],
})
