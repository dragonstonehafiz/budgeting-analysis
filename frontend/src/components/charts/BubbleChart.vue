<template>
  <div>
    <h3 v-if="title" class="chart-title">{{ title }}</h3>
    <div class="chart-row" :class="{ 'chart-row--packed': layout === 'packed' }">
      <div
        v-if="showLegend && legendItems.length"
        class="legend-left"
        :style="{ maxHeight: `${height}px` }"
      >
        <span v-for="item in legendItems" :key="item.label" class="legend-item">
          <span class="legend-swatch" :style="{ background: item.color }"></span>
          {{ item.label }}
        </span>
      </div>
      <div
        class="chart-canvas-wrap"
        :style="layout === 'packed' ? { height: `${height}px`, width: `${height}px` } : { height: `${height}px` }"
      >
        <svg
          v-if="layout === 'packed'"
          ref="packedSvgRef"
          class="packed-svg"
          :viewBox="packedViewBox"
          preserveAspectRatio="xMidYMid meet"
          @mouseleave="hidePackedTooltip"
        >
          <g>
            <circle
              v-for="point in packedRenderPoints"
              :key="point.label"
              :cx="point.cx"
              :cy="point.cy"
              :r="point.r"
              :fill="`${point.color}66`"
              :stroke="`${point.color}CC`"
              stroke-width="1.2"
              @mousemove="showPackedTooltip($event, point)"
              @mouseleave="hidePackedTooltip"
            />
            <text
              v-for="point in packedRenderPoints"
              :key="`label-${point.label}`"
              :x="point.cx"
              :y="point.cy"
              class="packed-label"
              :style="{ fontSize: `${Math.max(8, Math.min(13, point.r * 0.28))}px` }"
            >
              {{ shortenLabel(point.label, point.r) }}
            </text>
          </g>
        </svg>
        <Bubble v-else :data="chartData" :options="chartOptions" />
        <div
          v-if="packedTooltip.visible"
          class="packed-tooltip"
          :style="{ left: `${packedTooltip.x}px`, top: `${packedTooltip.y}px` }"
        >
          <div class="packed-tooltip-title">{{ packedTooltip.label }}</div>
          <div class="packed-tooltip-value">{{ packedTooltip.value }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Bubble } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(LinearScale, PointElement, Tooltip, Legend)

const props = defineProps({
  title: { type: String, default: '' },
  points: { type: Array, default: () => [] },
  layout: { type: String, default: 'xy' }, // 'xy' | 'packed'
  showLegend: { type: Boolean, default: false },
  xLabel: { type: String, default: '' },
  yLabel: { type: String, default: '' },
  xFormat: { type: String, default: 'number' }, // 'number' | 'currency'
  yFormat: { type: String, default: 'number' }, // 'number' | 'currency'
  height: { type: Number, default: 340 },
  privacyMode: { type: Boolean, default: false },
})

const packedSvgRef = ref(null)
const packedTooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  label: '',
  value: '',
})

function formatValue(value, format, allowMask = true) {
  const num = Number(value)
  if (!Number.isFinite(num)) return '-'
  if (allowMask && props.privacyMode && format === 'currency') return '$••••'
  if (format === 'currency') {
    return `$${num.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }
  return num.toLocaleString('en-AU', { maximumFractionDigits: 2 })
}

function shortenLabel(label, radius) {
  const text = String(label || '').trim()
  if (!text) return ''
  const maxChars = Math.max(3, Math.floor(radius / 3.1))
  if (text.length <= maxChars) return text
  if (maxChars <= 3) return text.slice(0, maxChars)
  return `${text.slice(0, maxChars - 1)}…`
}

const PALETTE = [
  '#1D4ED8', '#EA580C', '#16A34A', '#7C3AED', '#DC2626',
  '#0891B2', '#A16207', '#0F766E', '#9333EA', '#2563EB',
  '#C2410C', '#0E7490',
]

function colorForLabel(label, fallbackIndex = 0) {
  const text = String(label || '')
  if (!text) return PALETTE[fallbackIndex % PALETTE.length]
  let hash = 0
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash * 31 + text.charCodeAt(i)) | 0
  }
  return PALETTE[Math.abs(hash) % PALETTE.length]
}

function buildPackedPoints(rawPoints) {
  if (!rawPoints.length) return []

  const values = rawPoints.map((point) => Math.max(0, Number(point.value ?? point.y ?? 0)))
  const minVal = Math.min(...values)
  const maxVal = Math.max(...values)
  const span = Math.max(0.0001, maxVal - minVal)

  const circles = rawPoints
    .map((point, idx) => {
      const value = Math.max(0, Number(point.value ?? point.y ?? 0))
      const t = (value - minVal) / span
      return {
        label: point.label || `Item ${idx + 1}`,
        value,
        r: 8 + t * 34,
        color: point.color || colorForLabel(point.label, idx),
      }
    })
    .sort((a, b) => b.r - a.r)

  const packed = circles.map((circle, idx) => {
    const angle = idx * 2.399963229728653
    const dist = Math.sqrt(idx) * 12
    return {
      ...circle,
      x: dist * Math.cos(angle),
      y: dist * Math.sin(angle),
      vx: 0,
      vy: 0,
    }
  })

  const padding = 1.6
  const iterations = 900
  for (let k = 0; k < iterations; k += 1) {
    for (let i = 0; i < packed.length; i += 1) {
      for (let j = i + 1; j < packed.length; j += 1) {
        const a = packed[i]
        const b = packed[j]
        let dx = b.x - a.x
        let dy = b.y - a.y
        let d2 = dx * dx + dy * dy
        if (d2 < 0.0001) {
          dx = 0.01
          dy = 0.01
          d2 = dx * dx + dy * dy
        }
        const d = Math.sqrt(d2)
        const minDist = a.r + b.r + padding
        if (d < minDist) {
          const overlap = (minDist - d) / d
          const ox = dx * overlap * 0.5
          const oy = dy * overlap * 0.5
          a.x -= ox
          a.y -= oy
          b.x += ox
          b.y += oy
        }
      }
    }

    for (const c of packed) {
      c.vx += (0 - c.x) * 0.0046
      c.vy += (0 - c.y) * 0.0046
      c.vx *= 0.9
      c.vy *= 0.9
      c.x += c.vx
      c.y += c.vy
    }
  }

  return packed
}

const computedPoints = computed(() => {
  if (props.layout === 'packed') return buildPackedPoints(props.points)
  return props.points.map((point, idx) => ({
    x: Number(point.x) || 0,
    y: Number(point.y) || 0,
    r: Math.max(5, Number(point.r) || 8),
    label: point.label || '',
    value: Number(point.value ?? point.y ?? 0) || 0,
    color: point.color || colorForLabel(point.label, idx),
  }))
})

const packedRenderPoints = computed(() => {
  if (props.layout !== 'packed' || !computedPoints.value.length) return []
  return computedPoints.value.map((p) => ({
    ...p,
    cx: p.x,
    cy: p.y,
    r: Math.max(3, p.r),
  }))
})

const packedBounds = computed(() => {
  if (!packedRenderPoints.value.length) {
    return { minX: 0, minY: 0, width: 100, height: 100 }
  }
  const pad = 12
  const minX = Math.min(...packedRenderPoints.value.map((p) => p.cx - p.r)) - pad
  const maxX = Math.max(...packedRenderPoints.value.map((p) => p.cx + p.r)) + pad
  const minY = Math.min(...packedRenderPoints.value.map((p) => p.cy - p.r)) - pad
  const maxY = Math.max(...packedRenderPoints.value.map((p) => p.cy + p.r)) + pad
  const width = Math.max(1, maxX - minX)
  const height = Math.max(1, maxY - minY)
  return { minX, minY, width, height }
})

const packedViewBox = computed(() =>
  `${packedBounds.value.minX} ${packedBounds.value.minY} ${packedBounds.value.width} ${packedBounds.value.height}`
)

const bounds = computed(() => {
  if (!computedPoints.value.length) return { xMin: 0, xMax: 1, yMin: 0, yMax: 1 }
  const xMin = Math.min(...computedPoints.value.map((point) => point.x - point.r))
  const xMax = Math.max(...computedPoints.value.map((point) => point.x + point.r))
  const yMin = Math.min(...computedPoints.value.map((point) => point.y - point.r))
  const yMax = Math.max(...computedPoints.value.map((point) => point.y + point.r))
  return { xMin, xMax, yMin, yMax }
})

const legendItems = computed(() =>
  [...computedPoints.value]
    .sort((a, b) => (b.value ?? b.y ?? 0) - (a.value ?? a.y ?? 0))
    .map((point) => ({
    label: point.label || 'Item',
    value: point.value ?? point.y ?? 0,
    color: point.color || '#64748B',
  }))
)

const chartData = computed(() => ({
  datasets: [
    {
      label: props.title || 'Bubble Series',
      data: computedPoints.value.map((point) => ({
        x: point.x,
        y: point.y,
        r: point.r,
        label: point.label || '',
        value: point.value ?? point.y ?? 0,
      })),
      backgroundColor: computedPoints.value.map((point) => `${point.color}66`),
      borderColor: computedPoints.value.map((point) => `${point.color}CC`),
      borderWidth: 1,
      hoverBackgroundColor: computedPoints.value.map((point) => `${point.color}99`),
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        title: (items) => {
          const item = items?.[0]
          return item?.raw?.label || ''
        },
        label: (ctx) => {
          if (props.layout === 'packed') {
            return `Total Spent: ${formatValue(ctx.raw.value, props.yFormat, false)}`
          }
          const x = formatValue(ctx.raw.x, props.xFormat, false)
          const y = formatValue(ctx.raw.y, props.yFormat, false)
          return [
            `${props.xLabel || 'X'}: ${x}`,
            `${props.yLabel || 'Y'}: ${y}`,
          ]
        },
      },
    },
  },
  scales: {
    x: {
      min: bounds.value.xMin,
      max: bounds.value.xMax,
      title: { display: Boolean(props.xLabel), text: props.xLabel },
      display: props.layout !== 'packed',
      ticks: {
        color: '#666',
        callback: (value) => formatValue(value, props.xFormat),
      },
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
    y: {
      min: bounds.value.yMin,
      max: bounds.value.yMax,
      title: { display: Boolean(props.yLabel), text: props.yLabel },
      display: props.layout !== 'packed',
      ticks: {
        color: '#666',
        callback: (value) => formatValue(value, props.yFormat),
      },
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
  },
}))

function showPackedTooltip(event, point) {
  const host = packedSvgRef.value?.parentElement
  if (!host) return
  const rect = host.getBoundingClientRect()
  packedTooltip.value = {
    visible: true,
    x: event.clientX - rect.left + 10,
    y: event.clientY - rect.top - 10,
    label: point.label || 'Item',
    value: formatValue(point.value, props.yFormat, false),
  }
}

function hidePackedTooltip() {
  packedTooltip.value.visible = false
}
</script>

<style scoped>
.chart-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.6rem;
}

.chart-canvas-wrap {
  position: relative;
  flex: 0 0 auto;
}

.packed-svg {
  display: block;
  width: 100%;
  height: 100%;
}

.chart-row--packed .packed-svg {
  max-height: 70vh;
  display: block;
}

.chart-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.chart-row--packed {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  width: fit-content;
  max-width: 100%;
  margin: 0 auto;
}

.legend-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
  width: 320px;
  overflow: auto;
  padding: 0;
  background: transparent;
  border: 0;
  border-radius: 0;
  align-self: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: #374151;
  font-size: 0.78rem;
  line-height: 1.25;
}

.legend-swatch {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.packed-tooltip {
  position: absolute;
  z-index: 5;
  pointer-events: none;
  background: rgba(17, 24, 39, 0.95);
  color: #fff;
  border-radius: 6px;
  padding: 0.4rem 0.5rem;
  font-size: 0.76rem;
  min-width: 120px;
}

.packed-tooltip-title {
  font-weight: 700;
  line-height: 1.2;
}

.packed-tooltip-value {
  margin-top: 0.2rem;
  line-height: 1.2;
}

.packed-label {
  fill: #111827;
  text-anchor: middle;
  dominant-baseline: middle;
  font-weight: 600;
  pointer-events: none;
}

@media (max-width: 900px) {
  .chart-row {
    flex-direction: column;
  }

  .chart-row--packed {
    width: 100%;
    flex-direction: column;
  }

  .legend-left {
    width: 100%;
    max-height: 180px;
  }
}
</style>
