<template>
  <div>
    <h3 v-if="title" class="chart-title">{{ title }}</h3>
    <div :style="{ height: height + 'px', position: 'relative' }">
      <Bar :data="chartData" :options="chartOptions" :plugins="chartPlugins" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps({
  series:     { type: Array,   required: true },
  itemNames:  { type: Array,   required: true },
  itemColors: { type: Array,   required: true },
  title:      { type: String,  default: '' },
  showTotals: { type: Boolean, default: false },
  height:     { type: Number,  default: 400 },
  privacyMode: { type: Boolean, default: false },
})

const chartData = computed(() => ({
  labels: props.itemNames,
  datasets: props.series.map(s => ({
    label:           s.name,
    data:            s.data,
    details:         s.details || [],
    backgroundColor: props.itemColors,
    borderWidth:     1,
    borderColor:     '#fff',
    borderSkipped:   false,
  })),
}))

// Inline plugin: draw summed total at the right edge of each bar
const totalsPlugin = {
  id: 'barTotals',
  afterDatasetsDraw(chart) {
    if (!props.showTotals) return
    const { ctx, scales } = chart
    const totals = props.itemNames.map((_, i) =>
      props.series.reduce((sum, s) => sum + (s.data[i] || 0), 0)
    )
    ctx.save()
    ctx.font         = '600 11px sans-serif'
    ctx.fillStyle    = '#444'
    ctx.textAlign    = 'left'
    ctx.textBaseline = 'middle'
    totals.forEach((total, i) => {
      const x = scales.x.getPixelForValue(total) + 4
      const y = scales.y.getPixelForValue(i)
      const totalText = props.privacyMode
        ? '$••••'
        : `$${total.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
      ctx.fillText(totalText, x, y)
    })
    ctx.restore()
  },
}

const chartPlugins = [totalsPlugin]

const chartOptions = computed(() => ({
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => {
          const lines = [` $${ctx.parsed.x.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`]
          const details = ctx.dataset.details?.[ctx.dataIndex]
          if (!details) return lines

          lines.push(` Store: ${details.store || '—'}`)
          lines.push(` Tags: ${details.tags || '—'}`)
          lines.push(` Notes: ${details.notes || '—'}`)
          return lines
        },
      },
    },
  },
  scales: {
    x: {
      stacked: true,
      ticks: {
        callback: v => props.privacyMode
          ? '$••••'
          : `$${Number(v).toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
        color: '#666',
      },
      grid:  { color: 'rgba(0,0,0,0.05)' },
    },
    y: {
      stacked: true,
      ticks: { color: '#555', font: { size: 12 } },
      grid:  { display: false },
    },
  },
}))
</script>

<style scoped>
.chart-title { font-size: 0.95rem; font-weight: 600; color: #333; margin: 0 0 0.5rem; }
</style>
