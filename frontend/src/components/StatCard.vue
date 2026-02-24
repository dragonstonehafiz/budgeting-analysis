<template>
  <div class="stat-card">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value">{{ formattedValue }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label:  { type: String,  required: true },
  value:  { type: Number,  required: true },
  /** 'currency' | 'currency-rate' | 'integer' | 'percent' */
  format: { type: String,  default: 'currency' },
})

const formattedValue = computed(() => {
  const v = props.value
  if (!isFinite(v)) return '—'
  switch (props.format) {
    case 'integer':
      return v.toLocaleString('en-AU', { maximumFractionDigits: 0 })
    case 'percent':
      return `${v.toFixed(1)}%`
    case 'currency-rate':
      return `$${v.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} / period`
    default: // 'currency'
      return `$${v.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }
})
</script>

<style scoped>
.stat-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #888;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1a1a2e;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
