<template>
  <div>
    <h3 v-if="title" class="chart-title">{{ title }}</h3>
    <div :style="{ height: height + 'px', position: 'relative' }">
      <Doughnut :data="chartData" :options="chartOptions" :plugins="chartPlugins" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const FALLBACK = ['#1976D2','#43A047','#FB8C00','#8E24AA','#E53935','#00ACC1','#F4511E','#6D4C41','#546E7A','#FFB300']

const props = defineProps({
  series:     { type: Array,   required: true },
  title:      { type: String,  default: '' },
  topN:       { type: Number,  default: 10 },
  showLegend: { type: Boolean, default: false },
  height:     { type: Number,  default: 380 },
  privacyMode: { type: Boolean, default: false },
})

const displaySeries = computed(() => {
  if (!props.series?.length) return []
  const sorted = [...props.series].sort((a, b) => b.value - a.value)
  if (!props.topN || props.topN <= 0 || sorted.length <= props.topN) return sorted
  const top        = sorted.slice(0, props.topN)
  const otherValue = sorted.slice(props.topN).reduce((s, i) => s + i.value, 0)
  if (otherValue > 0) top.push({ label: 'Other', value: otherValue, color: '#BDBDBD' })
  return top
})

const total = computed(() => (props.series || []).reduce((s, i) => s + i.value, 0))

const chartData = computed(() => ({
  labels: displaySeries.value.map(i => i.label),
  datasets: [{
    data:            displaySeries.value.map(i => i.value),
    backgroundColor: displaySeries.value.map((i, idx) => i.color ?? FALLBACK[idx % FALLBACK.length]),
    borderWidth: 2,
    borderColor: '#fff',
    hoverOffset: 4,
  }],
}))

const centerLabelPlugin = {
  id: 'centerLabel',
  afterDraw(chart) {
    const { ctx, chartArea } = chart
    if (!chartArea) return
    const cx = (chartArea.left + chartArea.right) / 2
    const cy = (chartArea.top  + chartArea.bottom) / 2
    const t  = total.value
    ctx.save()
    ctx.font         = 'bold 13px sans-serif'
    ctx.fillStyle    = '#333'
    ctx.textAlign    = 'center'
    ctx.textBaseline = 'middle'
    const totalLabel = props.privacyMode
      ? '$••••'
      : `$${t.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    ctx.fillText(totalLabel, cx, cy)
    ctx.restore()
  },
}

const chartPlugins = [centerLabelPlugin]

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  cutout: '62%',
  plugins: {
    legend: { display: props.showLegend, position: 'right' },
    tooltip: {
      callbacks: {
        label: ctx => {
          const v   = ctx.parsed
          const pct = total.value > 0 ? ((v / total.value) * 100).toFixed(1) : '0.0'
          return ` $${v.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (${pct}%)`
        },
      },
    },
  },
}))
</script>

<style scoped>
.chart-title { font-size: 0.95rem; font-weight: 600; color: #333; margin: 0 0 0.5rem; text-align: center; }
</style>
