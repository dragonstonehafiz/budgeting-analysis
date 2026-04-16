<template>
  <div class="page-container">

    <!-- ── Controls bar ─────────────────────────────────────────── -->
    <FilterBar :showSearch="true" />

    <!-- ── KPI Cards ─────────────────────────────────────────────── -->
    <KPIStats :stats="stats" :privacyMode="privacyMode" />

    <!-- ── Chart section ─────────────────────────────────────────── -->
    <section class="chart-section">
      <div class="chart-controls">
        <div class="btn-group">
          <button
            v-for="opt in chartOptions"
            :key="opt.key"
            class="btn"
            :class="{ 'btn--active': activeChart === opt.key }"
            @click="activeChart = opt.key"
          >{{ opt.label }}</button>
        </div>
        <div class="btn-group" style="margin-left: auto;">
          <button
            v-for="opt in bucketOptions"
            :key="opt.value"
            class="btn btn--sm"
            :class="{ 'btn--active': bucketDays === opt.value }"
            @click="bucketDays = opt.value"
          >{{ opt.label }}</button>
        </div>
      </div>

      <LineChart
        :key="`trend-${privacyMode}`"
        v-if="activeChart === 'trend'"
        :series="spendingSeries"
        :averageLine="spendingAverage"
        :transactions="filteredTransactions"
        :bucketDays="bucketDays"
        title="Monthly Spending Trend"
        :height="340"
        :privacyMode="privacyMode"
      />
      <LineChart
        :key="`cumulative-${privacyMode}`"
        v-else-if="activeChart === 'cumulative'"
        :series="cumulativeSeries"
        :averageLine="movingAverageAverage"
        :transactions="filteredTransactions"
        :bucketDays="bucketDays"
        title="Moving Average"
        :height="340"
        :privacyMode="privacyMode"
      />
      <LineChart
        :key="`category-${privacyMode}`"
        v-else-if="activeChart === 'category'"
        :series="categorySeries"
        :transactions="filteredTransactions"
        :bucketDays="bucketDays"
        title="Spending by Category"
        :showLegend="true"
        :height="380"
        :privacyMode="privacyMode"
      />
    </section>

    <!-- ── Donut charts ──────────────────────────────────────────────── -->
    <div class="donut-row">
      <section class="chart-section">
        <DonutChart
          :key="`cat-${selectedYear}-${privacyMode}`"
          :series="categoryDonutSeries"
          title="Spending by Category"
          :topN="0"
          :showLegend="true"
          :height="360"
          :privacyMode="privacyMode"
        />
      </section>
      <section class="chart-section">
        <DonutChart
          :key="`cat-monthly-average-${selectedYear}-${privacyMode}`"
          :series="categoryMonthlyAverageDonutSeries"
          title="Monthly Average Spend by Category"
          :topN="0"
          :showLegend="true"
          :height="360"
          :privacyMode="privacyMode"
        />
      </section>
    </div>
    <div class="donut-row" :class="{ 'donut-row--single': selectedYear === 'All' }">
      <section v-if="selectedYear !== 'All'" class="chart-section">
        <DonutChart
          :key="`month-${selectedYear}-${privacyMode}`"
          :series="monthlyDonutSeries"
          title="Spending by Month"
          :topN="0"
          :showLegend="true"
          :height="360"
          :privacyMode="privacyMode"
        />
      </section>
      <section class="chart-section">
        <DonutChart
          :key="`store-${selectedYear}-${privacyMode}`"
          :series="storeDonutSeries"
          title="Spending at Specific Stores"
          :topN="0"
          :showLegend="true"
          :height="360"
          :privacyMode="privacyMode"
        />
      </section>
    </div>

    <!-- ── Top items bar chart ────────────────────────────────────── -->
    <section class="chart-section">
      <HorizontalBarChart
        :key="`top-items-${privacyMode}`"
        :series="topItems.series"
        :itemNames="topItems.itemNames"
        :itemColors="topItems.itemColors"
        title="Top 10 Items by Spend"
        :showTotals="true"
        :height="420"
        :privacyMode="privacyMode"
      />
    </section>

    <!-- ── Top 10 transactions table ─────────────────────────────── -->
    <section class="chart-section">
      <TransactionsTable
        title="Top 10 Most Expensive Transactions"
        :transactions="top10Transactions"
        :privacyMode="privacyMode"
        defaultSortKey="cost"
        defaultSortDir="desc"
      />
    </section>

    <!-- ── Monthly drill-down ─────────────────────────────────── -->
    <section v-if="isNumericYear" class="chart-section">
      <div class="chart-controls">
        <div class="btn-group month-btn-group">
          <button
            v-for="(name, idx) in MONTH_NAMES"
            :key="idx + 1"
            class="btn btn--sm"
            :class="{ 'btn--active': selectedMonth === idx + 1 }"
            @click="selectedMonth = idx + 1"
          >{{ name }}</button>
        </div>
      </div>
      <TransactionsTable
        :title="`${MONTH_NAMES[selectedMonth - 1]} ${selectedYear} — All Transactions`"
        :transactions="monthTransactions"
        :privacyMode="privacyMode"
      />
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LineChart           from '../components/charts/LineChart.vue'
import HorizontalBarChart  from '../components/charts/HorizontalBarChart.vue'
import DonutChart          from '../components/charts/DonutChart.vue'
import KPIStats            from '../components/ui/KPIStats.vue'
import TransactionsTable   from '../components/tables/TransactionsTable.vue'
import {
  toSpendingSeries,
  toMovingAverageSeries,
  toCumulativeCategorySeries,
  toCategoryDonutSeries,
  toCategoryMonthlyAverageDonutSeries,
  toMonthlyDonutSeries,
  toStoreDonutSeries,
  computeAverage,
  toTopItemsSeries,
  computeStats,
} from '../composables/useChartData.js'
import FilterBar          from '../components/ui/FilterBar.vue'
import { useGlobalFilters } from '../composables/useGlobalFilters.js'

const { selectedYear, search, selectedTags, privacyMode, transactions, initFilters } = useGlobalFilters()

onMounted(() => initFilters())

// ── Chart controls ─────────────────────────────────────────────────────────
const chartOptions = [
  { key: 'trend',      label: 'Monthly Trend' },
  { key: 'category',   label: 'Cumulative Spend' },
  { key: 'cumulative', label: 'Moving Average' },
]
const activeChart = ref('trend')

const bucketOptions = [
  { label: '1-day',  value: 1  },
  { label: '7-day',  value: 7  },
  { label: '28-day', value: 28 },
  { label: 'Monthly', value: 'month' },
]
const bucketDays = ref('month')

// For the monthly drill-down card (only relevant when selectedYear is numeric)
const MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const selectedMonth = ref(new Date().getMonth() + 1) // 1-12, default to current month

function parseTags(tags) {
  if (!tags || typeof tags !== 'string') return []
  return tags
    .split(',')
    .map((tag) => tag.trim().toLowerCase())
    .filter(Boolean)
}

// ── Filtered transactions (drives all charts + stats) ─────────────────────
const filteredTransactions = computed(() => {
  let txs = transactions.value
  const q = search.value.trim().toLowerCase()
  if (q) txs = txs.filter(t =>
    t.Item.toLowerCase().includes(q) || String(t.Notes || '').toLowerCase().includes(q)
  )
  if (selectedTags.value.length) {
    txs = txs.filter((t) => {
      const txTags = parseTags(t.Tags)
      return txTags.some((tag) => selectedTags.value.includes(tag))
    })
  }
  return txs
})

// ── Monthly drill-down ─────────────────────────────────────────────────────
// True only when selectedYear is a numeric year like '2024'
const isNumericYear = computed(() => /^\d{4}$/.test(selectedYear.value))

// All raw transactions for the selected month (no search/tag filters, no limit)
const monthTransactions = computed(() => {
  if (!isNumericYear.value) return []
  const mm = String(selectedMonth.value).padStart(2, '0')
  return transactions.value.filter(tx => tx.Date?.slice(5, 7) === mm)
})

// ── Stats ──────────────────────────────────────────────────────────────────
const stats = computed(() => computeStats(filteredTransactions.value))

// ── Line chart series (only compute the active chart) ────────────────────
const spendingSeries    = computed(() => activeChart.value !== 'trend'      ? [] : toSpendingSeries(filteredTransactions.value, bucketDays.value))
const spendingAverage   = computed(() => activeChart.value !== 'trend'      ? 0  : computeAverage(filteredTransactions.value,   bucketDays.value))
const cumulativeSeries  = computed(() => activeChart.value !== 'cumulative' ? [] : toMovingAverageSeries(filteredTransactions.value, bucketDays.value))
const movingAverageAverage = computed(() => {
  if (activeChart.value !== 'cumulative' || cumulativeSeries.value.length === 0) return 0
  const data = cumulativeSeries.value[0]?.data ?? []
  if (data.length === 0) return 0
  const sum = data.reduce((acc, point) => acc + point.y, 0)
  return sum / data.length
})
const categorySeries    = computed(() => activeChart.value !== 'category'   ? [] : toCumulativeCategorySeries(filteredTransactions.value, bucketDays.value))

// ── Donut charts ──────────────────────────────────────────────────────────
const categoryDonutSeries = computed(() => toCategoryDonutSeries(filteredTransactions.value))
const categoryMonthlyAverageDonutSeries = computed(() => toCategoryMonthlyAverageDonutSeries(filteredTransactions.value))
const monthlyDonutSeries  = computed(() => toMonthlyDonutSeries(filteredTransactions.value))
const storeDonutSeries = computed(() => toStoreDonutSeries(filteredTransactions.value))

// ── Bar chart & table ──────────────────────────────────────────────────────
const topItems = computed(() => toTopItemsSeries(filteredTransactions.value, 10))

const top10Transactions = computed(() =>
  [...filteredTransactions.value]
    .sort((a, b) => b.Cost - a.Cost)
    .slice(0, 10)
)
</script>

<style scoped>
.page-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 1.35rem 2rem 3rem;
}

.btn-group { display: flex; gap: 0.3rem; flex-wrap: wrap; }
.month-btn-group {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 0.35rem;
}

.btn {
  padding: 0.38rem 0.88rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-soft);
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition), color var(--transition), border-color var(--transition), box-shadow var(--transition);
}
.btn:hover {
  background: #e8f0fd;
  color: var(--accent-strong);
  border-color: #c9dbfb;
}
.btn--active {
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: #fff;
  border-color: var(--accent);
  font-weight: 600;
  box-shadow: 0 8px 16px rgba(15, 62, 168, 0.24);
}
.btn--sm { padding: 0.25rem 0.65rem; font-size: 0.78rem; }
.month-btn-group .btn--sm {
  width: 100%;
  text-align: center;
}

.chart-section {
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.2rem 1.35rem;
  margin-bottom: 1.15rem;
  box-shadow: var(--shadow-sm);
}

.donut-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.15rem;
  margin-bottom: 1.15rem;
}
.donut-row--single {
  grid-template-columns: 1fr;
}
.donut-row > .chart-section {
  margin-bottom: 0;
}

@media (max-width: 700px) {
  .donut-row { grid-template-columns: 1fr; }
  .month-btn-group { grid-template-columns: repeat(6, minmax(0, 1fr)); }
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.9rem;
  flex-wrap: wrap;
}

.section-title {
  font-size: 1.02rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 1rem;
  letter-spacing: -0.01em;
}
</style>


