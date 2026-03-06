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
    <div :style="{ height: height + 'px', position: 'relative' }" @mousemove="handleMouseMove">
      <Line :data="chartData" :options="chartOptions" />
      <ItemListTooltip ref="tooltip" :items="hoveredItems" :tooltip-x="tooltipX" :tooltip-y="tooltipY" />
    </div>
    <p v-if="caption" class="chart-caption">{{ caption }}</p>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Line } from 'vue-chartjs'
import ItemListTooltip from '../ui/ItemListTooltip.vue'
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

// Register custom plugin for average line label
const averageLinePlugin = {
  id: 'averageLineLabel',
  afterDraw(chart) {
    const options = chart.options.plugins?.averageLineLabel
    if (!options?.averageValue) return

    const ctx = chart.ctx
    const yScale = chart.scales.y
    const xScale = chart.scales.x

    if (!yScale || !xScale) return

    const yPixel = yScale.getPixelForValue(options.averageValue)
    const xPixel = xScale.left - 12

    ctx.save()
    ctx.font = 'bold 12px sans-serif'
    ctx.textAlign = 'right'
    ctx.textBaseline = 'middle'

    const label = `$${options.averageValue.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    ctx.fillStyle = 'rgba(220,53,69,0.85)'
    ctx.fillText(label, xPixel, yPixel)
    ctx.restore()
  }
}

ChartJS.register(averageLinePlugin)

// Register custom plugin for year separator lines
const yearSeparatorPlugin = {
  id: 'yearSeparator',
  afterDraw(chart) {
    const ctx = chart.ctx
    const xScale = chart.scales.x
    const yScale = chart.scales.y

    if (!xScale || !yScale) return

    // Collect all unique timestamps from datasets
    const timestamps = new Set()
    for (const dataset of chart.data.datasets) {
      if (dataset.data && Array.isArray(dataset.data)) {
        for (const point of dataset.data) {
          if (point?.x) timestamps.add(point.x)
        }
      }
    }

    if (timestamps.size === 0) return

    // Sort timestamps and find year boundaries
    const sortedTimestamps = Array.from(timestamps).sort((a, b) => a - b)
    const yearBoundaries = []
    let lastYear = null

    for (const ts of sortedTimestamps) {
      const date = new Date(ts)
      const year = date.getFullYear()
      if (lastYear !== null && year !== lastYear) {
        // Year boundary found, mark the start of the new year
        const newYearStart = new Date(year, 0, 1).getTime()
        yearBoundaries.push(newYearStart)
      }
      lastYear = year
    }

    // Draw vertical lines at year boundaries
    ctx.save()
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)'
    ctx.lineWidth = 1
    ctx.setLineDash([4, 4])

    for (const boundary of yearBoundaries) {
      const xPixel = xScale.getPixelForValue(boundary)
      if (xPixel >= xScale.left && xPixel <= xScale.right) {
        ctx.beginPath()
        ctx.moveTo(xPixel, yScale.top)
        ctx.lineTo(xPixel, yScale.bottom)
        ctx.stroke()

        // Draw year label at the top
        const date = new Date(boundary)
        const year = date.getFullYear()
        ctx.font = '12px sans-serif'
        ctx.fillStyle = 'rgba(0, 0, 0, 0.6)'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'bottom'
        ctx.fillText(year, xPixel, yScale.top + 2)
      }
    }

    ctx.restore()
  }
}

ChartJS.register(yearSeparatorPlugin)

// Store expensive items and dot positions for hover interaction
let expensiveItemsData = new Map()

// Register custom plugin for expensive items
const expensiveItemsPlugin = {
  id: 'expensiveItems',
  afterDraw(chart) {
    const options = chart.options.plugins?.expensiveItems
    if (!options?.itemsByBucket || options.itemsByBucket.size === 0) return

    const ctx = chart.ctx
    const xScale = chart.scales.x
    const yScale = chart.scales.y

    if (!xScale || !yScale) return

    expensiveItemsData.clear()
    const dotRadius = 5

    // Draw dots below x-axis for each bucket with expensive items
    ctx.save()

    for (const [timestamp, items] of options.itemsByBucket) {
      const xPixel = xScale.getPixelForValue(timestamp)
      if (xPixel < xScale.left || xPixel > xScale.right) continue

      // Position dot below x-axis labels
      const yPixel = yScale.bottom + 30

      // Draw dot
      ctx.fillStyle = 'rgba(220, 53, 69, 0.8)'
      ctx.beginPath()
      ctx.arc(xPixel, yPixel, dotRadius, 0, 2 * Math.PI)
      ctx.fill()

      // If multiple items, draw count
      if (items.length > 1) {
        ctx.font = '8px sans-serif'
        ctx.fillStyle = '#fff'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(items.length, xPixel, yPixel)
      }

      // Store dot position for hover detection
      expensiveItemsData.set(`${xPixel},${yPixel}`, { items, xPixel, yPixel, dotRadius })
    }

    ctx.restore()
  }
}

ChartJS.register(expensiveItemsPlugin)

const props = defineProps({
  series:       { type: Array,          required: true },
  title:        { type: String,         default: '' },
  averageLine:  { type: Number,         default: null },
  caption:      { type: String,         default: '' },
  height:       { type: Number,         default: 320 },
  showLegend:   { type: Boolean,        default: false },
  privacyMode:  { type: Boolean,        default: false },
  transactions: { type: Array,          default: () => [] },
  bucketDays:   { type: [Number, String], default: 28 },
})

// Tooltip state
const tooltip = ref(null)
const tooltipX = ref(0)
const tooltipY = ref(0)
const hoveredItems = ref([])

// Calculate 99.5th percentile of transaction costs
const percentile99 = computed(() => {
  if (props.transactions.length === 0) return 0
  const costs = props.transactions.map(t => parseFloat(t.Cost)).sort((a, b) => a - b)
  const idx = Math.ceil(costs.length * 0.995) - 1
  return costs[Math.max(0, idx)]
})

// Group expensive items by bucket
const expensiveItemsByBucket = computed(() => {
  if (percentile99.value === 0) return new Map()

  const MS_PER_DAY = 86_400_000
  const map = new Map()

  for (const tx of props.transactions) {
    const cost = parseFloat(tx.Cost)
    if (cost < percentile99.value) continue

    const date = new Date(tx.Date)
    let bucketKey

    if (props.bucketDays === 'month') {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      bucketKey = `${year}-${month}`
      const monthStart = new Date(year, date.getMonth(), 1).getTime()
      if (!map.has(monthStart)) map.set(monthStart, [])
      map.get(monthStart).push(tx)
    } else {
      const bucketMs = props.bucketDays * MS_PER_DAY
      bucketKey = Math.floor(date.getTime() / bucketMs) * bucketMs
      if (!map.has(bucketKey)) map.set(bucketKey, [])
      map.get(bucketKey).push(tx)
    }
  }

  return map
})

const handleMouseMove = (e) => {
  const rect = e.currentTarget.getBoundingClientRect()
  const mouseX = e.clientX - rect.left
  const mouseY = e.clientY - rect.top

  let foundItems = null
  const hoverDistance = 10

  // Check if hovering over any expensive item dots
  for (const data of expensiveItemsData.values()) {
    const dist = Math.sqrt(Math.pow(mouseX - data.xPixel, 2) + Math.pow(mouseY - data.yPixel, 2))
    if (dist <= data.dotRadius + hoverDistance) {
      foundItems = data.items
      tooltipX.value = data.xPixel
      tooltipY.value = data.yPixel + 15 // Position below the dot
      break
    }
  }

  if (foundItems) {
    hoveredItems.value = foundItems
    tooltip.value?.show()
  }
}

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

const chartOptions = computed(() => {
  const privacyMode = props.privacyMode

  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    layout: {
      padding: {
        bottom: 50
      }
    },
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
      averageLineLabel: {
        averageValue: props.averageLine
      },
      expensiveItems: {
        itemsByBucket: expensiveItemsByBucket.value
      }
    },
    scales: {
      x: {
        type: 'time',
        time: { displayFormats: { day: 'dd MMM', week: 'dd MMM', month: 'MMM yy' }, tooltipFormat: 'dd MMM yyyy' },
        grid: { display: false },
        ticks: { color: '#666', maxTicksLimit: 12 },
      },
      y: {
        ticks: {
          callback: v => privacyMode
            ? '$••••'
            : `$${Number(v).toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
          color: '#666',
        },
        grid: { color: 'rgba(0,0,0,0.05)' },
      },
    },
  }
})
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
