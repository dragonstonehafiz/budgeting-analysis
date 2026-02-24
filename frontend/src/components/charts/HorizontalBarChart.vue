<template>
  <div class="bar-chart-wrapper">
    <h3 v-if="title" class="chart-title">{{ title }}</h3>

    <apexchart
      type="bar"
      :height="height"
      :options="chartOptions"
      :series="series"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const apexchart = VueApexCharts

const props = defineProps({
  /**
   * Slot-major series array from toTopItemsSeries():
   *   [{ name: 'Purchase 1', data: [15, 60, 70] }, { name: 'Purchase 2', data: [15, 40, 0] }, ...]
   */
  series: {
    type: Array,
    required: true,
  },

  /**
   * Item name labels for the y-axis, one per bar, largest total first.
   * Matches positionally with every series[n].data array.
   */
  itemNames: {
    type: Array,
    required: true,
  },

  /**
   * One hex color per item bar, derived from its dominant spending category.
   * Matches positionally with itemNames.
   */
  itemColors: {
    type: Array,
    required: true,
  },

  /** Chart heading displayed above the chart */
  title: {
    type: String,
    default: '',
  },

  /** Chart height in pixels */
  height: {
    type: Number,
    default: 400,
  },

  /** Show the summed total label at the end of each bar */
  showTotals: {
    type: Boolean,
    default: false,
  },
})

const chartOptions = computed(() => ({
  chart: {
    type: 'bar',
    stacked: true,
    toolbar: { show: false },
    animations: { enabled: false },
    background: 'transparent',
    redrawOnParentResize: false,
    redrawOnWindowResize: false,
  },
  plotOptions: {
    bar: {
      horizontal: true,
      barHeight: '60%',
      dataLabels: {
        position: 'top',
        total: {
          enabled: props.showTotals,
          offsetX: 6,
          style: { fontSize: '12px', fontWeight: 600, color: '#333' },
          formatter: val =>
            `$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
        },
      },
    },
  },
  // Color every segment of a bar using that bar's item color.
  // dataPointIndex = which item/bar (0 = first item, 1 = second, etc.)
  colors: [({ dataPointIndex }) => props.itemColors[dataPointIndex] ?? '#D9D9D9'],
  stroke: {
    width: 2,
    colors: ['#ffffff'],  // white dividers between segments
  },
  xaxis: {
    categories: props.itemNames,
    labels: {
      formatter: val => `$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`,
    },
  },
  yaxis: {
    labels: {
      maxWidth: 200,
      style: { fontSize: '12px' },
    },
  },
  dataLabels: {
    enabled: false,
  },
  tooltip: {
    shared: false,
    x: { show: true },
    y: {
      formatter: val =>
        val === 0
          ? null
          : `$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
    },
  },
  legend: {
    show: false,
  },
  grid: {
    xaxis: { lines: { show: true } },
    yaxis: { lines: { show: false } },
  },
}))
</script>

<style scoped>
.bar-chart-wrapper {
  width: 100%;
}

.chart-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}
</style>
