<template>
  <div>
    <h3 v-if="title" class="chart-title">{{ title }}</h3>
    <!-- External legend — rendered as HTML so it never squishes the canvas -->
    <div v-if="showLegend && legendItems.length" class="chart-legend">
      <span v-for="item in legendItems" :key="item.label" class="legend-item">
        <span class="legend-swatch" :style="{ background: item.color }"></span>
        {{ item.label }}
      </span>
    </div>
    <div :style="{ height: height + 'px', position: 'relative' }">
      <Line :data="chartData" :options="chartOptions" />
    </div>
    <p v-if="caption" class="chart-caption">{{ caption }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  TimeScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js'
import 'chartjs-adapter-date-fns'

ChartJS.register(TimeScale, LinearScale, PointElement, LineElement, Tooltip, Filler, Legend)

const props = defineProps({
  series:      { type: Array,   required: true },
  title:       { type: String,  default: '' },
  averageLine: { type: Number,  default: null },
  caption:     { type: String,  default: '' },
  height:      { type: Number,  default: 320 },
  showLegend:  { type: Boolean, default: false },
})

// Items for the external HTML legend (excludes rangeArea and empty-label entries)
const legendItems = computed(() =>
  props.series
    .filter(s => s.type !== 'rangeArea' && s.name)
    .map(s => ({ label: s.name, color: s.color ?? '#3b82f6' }))
)

const chartData = computed(() => {
  if (!props.series?.length) return { datasets: [] }

  const datasets = []
  const allX = props.series.flatMap(s => s.data.map(d => d.x))
  const minX  = Math.min(...allX)
  const maxX  = Math.max(...allX)

  for (const s of props.series) {
    if (s.type === 'rangeArea') {
      const upper = s.data.map(d => ({ x: d.x, y: Array.isArray(d.y) ? d.y[1] : d.y }))
      const lower = s.data.map(d => ({ x: d.x, y: Array.isArray(d.y) ? d.y[0] : d.y }))
      datasets.push({ label: s.name, data: upper, borderWidth: 0, backgroundColor: 'rgba(59,130,246,0.12)', fill: '+1', pointRadius: 0, tension: 0.3 })
      datasets.push({ label: '',     data: lower, borderWidth: 0, backgroundColor: 'transparent',           fill: false, pointRadius: 0, tension: 0.3 })
    } else if (s.type === 'scatter') {
      datasets.push({ label: s.name, data: s.data, type: 'scatter', backgroundColor: 'rgba(100,149,237,0.45)', pointRadius: 0, pointHoverRadius: 5 })
    } else {
      const color = s.color ?? '#3b82f6'
      const bg    = s.color ? `${s.color}18` : 'rgba(59,130,246,0.07)'
      datasets.push({
        label: s.name,
        data: s.data,
        borderColor: color,
        backgroundColor: bg,
        fill: false,
        pointRadius: 0,
        pointHoverRadius: 5,
        tension: 0.2,
        borderWidth: 2,
        spanGaps: false,
      })
    }
  }

  if (props.averageLine != null && allX.length) {
    datasets.push({
      label: 'Average',
      data: [{ x: minX, y: props.averageLine }, { x: maxX, y: props.averageLine }],
      borderColor: 'rgba(220,53,69,0.75)',
      borderDash: [6, 3],
      borderWidth: 1.5,
      pointRadius: 0,
      pointHoverRadius: 0,
      fill: false,
    })
  }

  return { datasets }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: { display: false }, // always off — we use external HTML legend
    tooltip: {
      callbacks: {
        label: ctx => {
          if (ctx.parsed.y == null) return null
          const name = ctx.dataset.label
          const val  = `$${ctx.parsed.y.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
          return name ? ` ${name}: ${val}` : ` ${val}`
        },
      },
    },
  },
  scales: {
    x: {
      type: 'time',
      time: { displayFormats: { day: 'dd MMM', week: 'dd MMM', month: 'MMM yy' }, tooltipFormat: 'dd MMM yyyy' },
      grid: { display: false },
      ticks: { color: '#666', maxTicksLimit: 12 },
    },
    y: {
      ticks: { callback: v => `$${Number(v).toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, color: '#666' },
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
  },
}))
</script>

<style scoped>
.chart-title   { font-size: 0.95rem; font-weight: 600; color: #333; margin: 0 0 0.5rem; }
.chart-caption { font-size: 0.78rem; color: #888; text-align: center; margin: 0.25rem 0 0; }

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.25rem;
  margin-bottom: 0.75rem;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: #444;
  white-space: nowrap;
}
.legend-swatch {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}
</style>
