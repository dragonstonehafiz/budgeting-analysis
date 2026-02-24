<template>
  <div class="line-chart-wrapper">
    <h3 v-if="title" class="chart-title">{{ title }}</h3>

    <apexchart
      type="line"
      :height="height"
      :options="chartOptions"
      :series="series"
    />

    <p v-if="caption" class="chart-caption">{{ caption }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

// Register the component locally
const apexchart = VueApexCharts

const props = defineProps({
  /** ApexCharts series array — already bucketed and transformed by useChartData.js */
  series: {
    type: Array,
    required: true,
  },
  /** Chart heading displayed above the chart */
  title: {
    type: String,
    default: '',
  },
  /** Optional y-value for a dashed horizontal average annotation line */
  averageLine: {
    type: Number,
    default: null,
  },
  /** Optional caption rendered below the chart (e.g. rolling average explanation) */
  caption: {
    type: String,
    default: '',
  },
  /** Chart height in pixels */
  height: {
    type: Number,
    default: 320,
  },
})

const chartOptions = computed(() => {
  // Detect whether any series uses rangeArea (rolling band) — affects stroke config
  const hasRangeArea = props.series.some(s => s.type === 'rangeArea')
  const hasScatter = props.series.some(s => s.type === 'scatter')

  // Per-series stroke widths: scatter → 0, rangeArea → 0, line → 2
  const strokeWidths = props.series.map(s => {
    if (s.type === 'scatter' || s.type === 'rangeArea') return 0
    return 2
  })

  // Per-series fill: rangeArea gets semi-transparent fill, others solid/none
  const fills = {
    type: props.series.map(s => (s.type === 'rangeArea' ? 'solid' : 'solid')),
    opacity: props.series.map(s => (s.type === 'rangeArea' ? 0.12 : 1)),
  }

  // Per-series colors
  const defaultColors = ['#9E9E9E', '#1976D2', '#1976D2']
  const colors =
    props.series.length > 1
      ? defaultColors.slice(0, props.series.length)
      : ['#1976D2']

  // Average annotation
  const yAnnotations = []
  if (props.averageLine !== null && props.averageLine !== undefined) {
    yAnnotations.push({
      y: props.averageLine,
      borderColor: '#d32f2f',
      strokeDashArray: 6,
      label: {
        text: `Avg: $${props.averageLine.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
        position: 'left',
        offsetX: 10,
        style: { color: '#d32f2f', background: 'transparent', fontSize: '12px' },
      },
    })
  }

  return {
    chart: {
      type: hasRangeArea ? 'rangeArea' : hasScatter ? 'line' : 'line',
      toolbar: { show: false },
      zoom: { enabled: false },
      animations: { enabled: true, speed: 300 },
      background: 'transparent',
    },
    // mixed types need explicit per-series type declarations
    ...(hasRangeArea || hasScatter
      ? {}
      : {}),
    colors,
    stroke: {
      curve: 'smooth',
      width: strokeWidths,
    },
    fill: fills,
    markers: {
      size: props.series.map(s => (s.type === 'scatter' ? 4 : s.type === 'rangeArea' ? 0 : 4)),
    },
    dataLabels: {
      enabled: false,
    },
    xaxis: {
      type: 'datetime',
      labels: {
        datetimeUTC: false,
        style: { fontSize: '12px', colors: '#555' },
        datetimeFormatter: {
          year: 'yyyy',
          month: "MMM 'yy",
          day: 'dd MMM',
        },
      },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: {
      labels: {
        formatter: val => `$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`,
        style: { fontSize: '12px', colors: '#555' },
      },
    },
    tooltip: {
      x: { format: "MMM yyyy" },
      y: {
        formatter: val =>
          val === null || val === undefined
            ? ''
            : `$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      },
    },
    annotations: {
      yaxis: yAnnotations,
    },
    grid: {
      borderColor: '#e0e0e0',
      strokeDashArray: 4,
      xaxis: { lines: { show: false } },
    },
    legend: {
      show: props.series.length > 1,
      position: 'top',
      horizontalAlign: 'right',
      fontSize: '12px',
    },
  }
})
</script>

<style scoped>
.line-chart-wrapper {
  width: 100%;
}

.chart-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.chart-caption {
  font-size: 0.78rem;
  color: #888;
  text-align: center;
  margin: 0.25rem 0 0;
}
</style>
