<template>
  <transition name="status-toast">
    <div v-if="toast.visible" class="status-toast" :class="`status-toast--${toast.type}`">
      {{ toast.message }}
    </div>
  </transition>
</template>

<script setup>
import { useToast } from '../../composables/useToast.js'

const { toast } = useToast()
</script>

<style scoped>
.status-toast {
  position: fixed;
  top: 90%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 0.8rem 1.2rem;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  font-weight: 600;
  box-shadow: var(--shadow-md);
  border: 1px solid transparent;
  pointer-events: none;
  z-index: 1200;
  min-width: min(72vw, 460px);
  max-width: min(92vw, 720px);
  text-align: center;
}

.status-toast--info {
  background: #eaf2ff;
  border-color: #bfd6ff;
  color: #1e4b9a;
}

.status-toast--success {
  background: #eaf9ef;
  border-color: #bde8c8;
  color: #116033;
}

.status-toast--error {
  background: #fff0f0;
  border-color: #f5c2c2;
  color: #8d1f1f;
}

.status-toast-enter-active,
.status-toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.status-toast-enter-from,
.status-toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -42%);
}
</style>
