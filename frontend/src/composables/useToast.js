import { ref } from 'vue'

const toast = ref({
  visible: false,
  type: 'info',
  message: '',
})

let hideTimer = null

function clearHideTimer() {
  if (!hideTimer) return
  clearTimeout(hideTimer)
  hideTimer = null
}

function hideToast() {
  clearHideTimer()
  toast.value.visible = false
}

function showToast(message, { type = 'info', duration = 2200, persistent = false } = {}) {
  clearHideTimer()
  toast.value = {
    visible: true,
    type,
    message,
  }

  if (!persistent) {
    hideTimer = setTimeout(() => {
      toast.value.visible = false
      hideTimer = null
    }, duration)
  }
}

export function useToast() {
  return {
    toast,
    showToast,
    hideToast,
  }
}
