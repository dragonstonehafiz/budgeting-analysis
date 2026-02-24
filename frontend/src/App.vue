<template>
  <NavBar />
  <RouterView v-slot="{ Component }">
    <KeepAlive>
      <component :is="Component" />
    </KeepAlive>
  </RouterView>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
</script>
