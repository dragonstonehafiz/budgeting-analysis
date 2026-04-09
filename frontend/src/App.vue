<template>
  <NavBar />
  <ToastContainer />
  <RouterView v-slot="{ Component }">
    <KeepAlive>
      <component :is="Component" />
    </KeepAlive>
  </RouterView>
</template>

<script setup>
import NavBar from './components/layout/NavBar.vue'
import ToastContainer from './components/ui/ToastContainer.vue'
</script>
