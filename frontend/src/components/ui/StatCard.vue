<template>
  <div class="stat-card">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value" :class="{ 'stat-value--text': format === 'text' }">{{ formattedValue }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label:  { type: String,  required: true },
  value:  { type: [Number, String], required: true },
  /** 'currency' | 'currency-rate' | 'integer' | 'percent' | 'text' */
  format: { type: String,  default: 'currency' },
  privacyMode: { type: Boolean, default: false },
})

const formattedValue = computed(() => {
  const v = props.value
  if (props.format === 'text') return String(v || 'â€”')
  if (!isFinite(v)) return '—'
  if (props.privacyMode && (props.format === 'currency' || props.format === 'currency-rate')) {
    return props.format === 'currency-rate' ? '$•••• / period' : '$••••'
  }
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
  position: relative;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
}

.stat-card::before {
  content: "";
  position: absolute;
  inset: 0 auto auto 0;
  width: 100%;
  height: 2px;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(15, 62, 168, 0.85), rgba(56, 189, 248, 0.7));
}

.stat-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
  border-color: #c9d7ea;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-faint);
}

.stat-value {
  font-size: 1.42rem;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-value--text {
  letter-spacing: normal;
  font-variant-numeric: normal;
  white-space: normal;
  overflow: visible;
  text-overflow: clip;
  word-spacing: 0.24em;
}
</style>
