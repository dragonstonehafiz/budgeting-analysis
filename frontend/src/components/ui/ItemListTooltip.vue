<template>
  <div
    v-if="isVisible && items.length"
    class="expensive-item-tooltip"
    :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <div v-for="item in items.slice(0, 3)" :key="item.Item" class="tooltip-row">
      <div class="tooltip-item-name">{{ item.Item }}</div>
      <div class="tooltip-item-price">${{ item.Cost.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  tooltipX: { type: Number, default: 0 },
  tooltipY: { type: Number, default: 0 },
  hideDelay: { type: Number, default: 750 }, // ms before auto-hiding
})

const isVisible = ref(false)
let hideTimeout = null

const show = () => {
  if (hideTimeout) clearTimeout(hideTimeout)
  isVisible.value = true
}

const hide = () => {
  if (hideTimeout) clearTimeout(hideTimeout)
  hideTimeout = setTimeout(() => {
    isVisible.value = false
  }, props.hideDelay)
}

const onMouseEnter = () => {
  if (hideTimeout) clearTimeout(hideTimeout)
}

const onMouseLeave = () => {
  hide()
}

// Show tooltip when items change
watch(() => props.items.length, (newLength) => {
  if (newLength > 0) {
    show()
  }
})

defineExpose({ show, hide })
</script>

<style scoped>
.expensive-item-tooltip {
  position: absolute;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 100;
  max-height: 120px;
  overflow-y: auto;
  font-size: 0.8rem;
  width: 220px;
  transform: translate(-50%, 0);
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 5px 0;
  border-bottom: 1px solid #f0f0f0;
}

.tooltip-row:last-child {
  border-bottom: none;
}

.tooltip-item-name {
  flex: 0 1 130px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.75rem;
}

.tooltip-item-price {
  flex: 0 0 auto;
  color: #dc3545;
  font-weight: 600;
  white-space: nowrap;
  font-size: 0.75rem;
}
</style>
