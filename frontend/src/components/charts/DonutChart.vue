<template>
  <div class="donut-chart-wrapper">
    <h3 v-if="title" class="chart-title">{{ title }}</h3>

    <apexchart
      type="donut"
      :height="height"
      :options="chartOptions"
      :series="displayValues"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const apexchart = VueApexCharts

const props = defineProps({
  /**
   * Array of segment objects:
   *   { label: string, value: number, color?: string }
   * Color is optional — falls back to a default palette if omitted.
   */
  series: {
    type: Array,
    required: true,
  },

  /** Chart heading displayed above the chart */
  title: {
    type: String,
    default: '',
  },

  /**
   * Max number of segments to show individually.
   * Segments beyond this are collapsed into a single "Other" segment.
   * Set to 0 or null to show all.
   */
  topN: {
    type: Number,
    default: 10,
  },

  /** Chart height in pixels */
  height: {
    type: Number,
    default: 380,
  },

  /** Show the legend. Defaults to false — pass :showLegend="true" to enable. */
  showLegend: {
    type: Boolean,
    default: false,
  },
})

/** Apply topN collapsing — returns the display-ready segment list */
const displaySeries = computed(() => {
  if (!props.series || props.series.length === 0) return []

  const sorted = [...props.series].sort((a, b) => b.value - a.value)

  if (!props.topN || props.topN <= 0 || sorted.length <= props.topN) {
    return sorted
  }

  const top = sorted.slice(0, props.topN)
  const otherValue = sorted.slice(props.topN).reduce((sum, s) => sum + s.value, 0)

  if (otherValue > 0) {
    top.push({ label: 'Other', value: otherValue, color: '#BDBDBD' })
  }

  return top
})

/** Flat arrays extracted from displaySeries for ApexCharts */
const displayValues = computed(() => displaySeries.value.map(s => s.value))
const displayLabels = computed(() => displaySeries.value.map(s => s.label))
const displayColors = computed(() => {
  // Use provided colors; fall back to ApexCharts default palette for missing entries
  const defaults = [
    '#1976D2', '#43A047', '#FB8C00', '#8E24AA', '#E53935',
    '#00ACC1', '#F4511E', '#6D4C41', '#546E7A', '#FFB300',
  ]
  return displaySeries.value.map((s, i) => s.color || defaults[i % defaults.length])
})

/** Center text: always the sum of all original series values (not just top N) */
const total = computed(() =>
  (props.series || []).reduce((sum, s) => sum + s.value, 0)
)

const chartOptions = computed(() => ({
  chart: {
    type: 'donut',
    toolbar: { show: false },
    animations: { enabled: false },
    background: 'transparent',
    redrawOnParentResize: false,
    redrawOnWindowResize: false,
  },
  labels: displayLabels.value,
  colors: displayColors.value,
  plotOptions: {
    pie: {
      donut: {
        size: '62%',
        labels: {
          show: true,
          total: {
            show: true,
            showAlways: true,
            label: 'Total',
            fontSize: '14px',
            fontWeight: 600,
            color: '#333',
            formatter: () =>
              `$${total.value.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}`,
          },
          value: {
            show: true,
            fontSize: '16px',
            fontWeight: 700,
            color: '#111',
            formatter: val =>
              `$${Number(val).toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}`,
          },
        },
      },
    },
  },
  dataLabels: {
    enabled: false,
  },
  legend: {
    show: props.showLegend,
    position: 'right',
    fontSize: '13px',
    markers: { width: 10, height: 10, radius: 2 },
    itemMargin: { horizontal: 4, vertical: 6 },
    offsetY: 0,
  },
  tooltip: {
    y: {
      formatter: val =>
        `$${Number(val).toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}`,
    },
  },
  stroke: {
    width: 2,
    colors: ['#fff'],
  },
}))
</script>

<style scoped>
.donut-chart-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chart-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
  text-align: center;
  width: 100%;
}
</style>
