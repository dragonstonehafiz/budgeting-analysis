<template>
  <div class="page-container">

    <!-- ── Controls bar ─────────────────────────────────────────── -->
    <FilterBar :showSearch="true" />

    <!-- ── KPI Cards ─────────────────────────────────────────────── -->
    <section class="kpi-section">
      <!-- Row 1 -->
      <div class="kpi-row kpi-row--2">
        <StatCard label="Total Spent"   :value="stats.totalSpent"  format="currency" :privacyMode="privacyMode" />
        <StatCard label="Items Bought"  :value="stats.itemsBought" format="integer" :privacyMode="privacyMode" />
      </div>

      <!-- Row 2 -->
      <div class="kpi-row kpi-row--5">
        <StatCard label="Average Spend"       :value="stats.averageSpend" format="currency" :privacyMode="privacyMode" />
        <StatCard label="Lower 25th Pctile"   :value="stats.p25"          format="currency" :privacyMode="privacyMode" />
        <StatCard label="Median Spend"        :value="stats.median"       format="currency" :privacyMode="privacyMode" />
        <StatCard label="Upper 75th Pctile"   :value="stats.p75"          format="currency" :privacyMode="privacyMode" />
        <StatCard label="Std Deviation"       :value="stats.stdDev"       format="currency" :privacyMode="privacyMode" />
      </div>

      <!-- Row 3 -->
      <div class="kpi-row kpi-row--4">
        <StatCard label="Avg Weekly Spend"   :value="stats.avgWeeklySpend"   format="currency" :privacyMode="privacyMode" />
        <StatCard label="Avg Monthly Spend"  :value="stats.avgMonthlySpend"  format="currency" :privacyMode="privacyMode" />
        <StatCard label="Avg Yearly Spend"   :value="stats.avgYearlySpend"   format="currency" :privacyMode="privacyMode" />
        <StatCard label="Spending Volatility" :value="stats.spendingVolatility" format="percent" :privacyMode="privacyMode" />
      </div>
    </section>

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
        title="Monthly Spending Trend"
        :height="340"
        :privacyMode="privacyMode"
      />
      <LineChart
        :key="`cumulative-${privacyMode}`"
        v-else-if="activeChart === 'cumulative'"
        :series="cumulativeSeries"
        :averageLine="movingAverageAverage"
        title="Moving Average"
        :height="340"
        :privacyMode="privacyMode"
      />
      <LineChart
        :key="`category-${privacyMode}`"
        v-else-if="activeChart === 'category'"
        :series="categorySeries"
        title="Spending by Category"
        :showLegend="true"
        :height="380"
        :privacyMode="privacyMode"
      />
    </section>

    <!-- ── Donut charts ──────────────────────────────────────────────── -->
    <div class="donut-row" :class="{ 'donut-row--single': selectedYear === 'All' }">
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
      />
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LineChart           from '../components/charts/LineChart.vue'
import HorizontalBarChart  from '../components/charts/HorizontalBarChart.vue'
import DonutChart          from '../components/charts/DonutChart.vue'
import StatCard            from '../components/StatCard.vue'
import TransactionsTable   from '../components/TransactionsTable.vue'
import {
  toSpendingSeries,
  toMovingAverageSeries,
  toCumulativeCategorySeries,
  toCategoryDonutSeries,
  toMonthlyDonutSeries,
  computeAverage,
  toTopItemsSeries,
  computeStats,
} from '../composables/useChartData.js'
import FilterBar          from '../components/FilterBar.vue'
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
const monthlyDonutSeries  = computed(() => toMonthlyDonutSeries(filteredTransactions.value))

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
  max-width: 1300px;
  margin: 0 auto;
  padding: 1.5rem 2rem 3rem;
}

/* ── KPI cards ───────────────────────────────────── */
.btn-group { display: flex; gap: 0.3rem; flex-wrap: wrap; }

.btn {
  padding: 0.35rem 0.85rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  background: #fff;
  color: #555;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.btn:hover { background: #f0f0f0; }
.btn--active {
  background: #1e293b;
  color: #fff;
  border-color: #1e293b;
  font-weight: 600;
}
.btn--sm { padding: 0.25rem 0.65rem; font-size: 0.78rem; }

/* ── Buttons ─────────────────────────────────────── */
.kpi-section { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 2rem; }

.kpi-row {
  display: grid;
  gap: 0.75rem;
}
.kpi-row--2 { grid-template-columns: repeat(2, 1fr); }
.kpi-row--5 { grid-template-columns: repeat(5, 1fr); }
.kpi-row--4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 860px) {
  .kpi-row--5 { grid-template-columns: repeat(3, 1fr); }
  .kpi-row--4 { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 540px) {
  .kpi-row--2, .kpi-row--5, .kpi-row--4 { grid-template-columns: 1fr 1fr; }
}

/* ── Chart sections ──────────────────────────────── */
.chart-section {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.donut-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}
.donut-row--single {
  grid-template-columns: 1fr;
}
.donut-row > .chart-section {
  margin-bottom: 0;
}

@media (max-width: 700px) {
  .donut-row { grid-template-columns: 1fr; }
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 1rem;
}
</style>
