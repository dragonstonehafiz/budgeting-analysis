<template>
  <div class="page-container">

    <!-- ── Controls bar ─────────────────────────────────────────── -->
    <FilterBar :showSearch="true" />

    <!-- ── KPI Cards ─────────────────────────────────────────────── -->
    <section class="kpi-section">
      <!-- Row 1 -->
      <div class="kpi-row kpi-row--2">
        <StatCard label="Total Spent"   :value="stats.totalSpent"  format="currency" />
        <StatCard label="Items Bought"  :value="stats.itemsBought" format="integer"  />
      </div>

      <!-- Row 2 -->
      <div class="kpi-row kpi-row--5">
        <StatCard label="Average Spend"       :value="stats.averageSpend" format="currency" />
        <StatCard label="Lower 25th Pctile"   :value="stats.p25"          format="currency" />
        <StatCard label="Median Spend"        :value="stats.median"       format="currency" />
        <StatCard label="Upper 75th Pctile"   :value="stats.p75"          format="currency" />
        <StatCard label="Std Deviation"       :value="stats.stdDev"       format="currency" />
      </div>

      <!-- Row 3 -->
      <div class="kpi-row kpi-row--4">
        <StatCard label="Avg Weekly Spend"   :value="stats.avgWeeklySpend"   format="currency" />
        <StatCard label="Avg Monthly Spend"  :value="stats.avgMonthlySpend"  format="currency" />
        <StatCard label="Avg Yearly Spend"   :value="stats.avgYearlySpend"   format="currency" />
        <StatCard label="Spending Volatility" :value="stats.spendingVolatility" format="percent" />
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
        v-if="activeChart === 'trend'"
        :series="spendingSeries"
        :averageLine="spendingAverage"
        title="Monthly Spending Trend"
        :height="340"
      />
      <LineChart
        v-else-if="activeChart === 'cumulative'"
        :series="cumulativeSeries"
        title="Cumulative Spending"
        :height="340"
      />
      <LineChart
        v-else-if="activeChart === 'category'"
        :series="categorySeries"
        title="Spending by Category"
        :showLegend="true"
        :height="380"
      />
    </section>

    <!-- ── Donut charts ──────────────────────────────────────────────── -->
    <div class="donut-row" :class="{ 'donut-row--single': selectedYear === 'All' }">
      <section class="chart-section">
        <DonutChart
          :key="'cat-' + selectedYear"
          :series="categoryDonutSeries"
          title="Spending by Category"
          :topN="0"
          :showLegend="true"
          :height="360"
        />
      </section>
      <section v-if="selectedYear !== 'All'" class="chart-section">
        <DonutChart
          :series="monthlyDonutSeries"
          title="Spending by Month"
          :topN="0"
          :showLegend="true"
          :height="360"
        />
      </section>
    </div>

    <!-- ── Top items bar chart ────────────────────────────────────── -->
    <section class="chart-section">
      <HorizontalBarChart
        :series="topItems.series"
        :itemNames="topItems.itemNames"
        :itemColors="topItems.itemColors"
        title="Top 10 Items by Spend"
        :showTotals="true"
        :height="420"
      />
    </section>

    <!-- ── Top 10 transactions table ─────────────────────────────── -->
    <section class="chart-section">
      <h2 class="section-title">Top 10 Most Expensive Transactions</h2>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Item</th>
              <th>Category</th>
              <th class="col-cost">Cost</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(tx, i) in top10Transactions" :key="i">
              <td>{{ tx.Date }}</td>
              <td>{{ tx.Item }}</td>
              <td>
                <span class="category-badge" :style="{ background: getCategoryColor(tx.Category) }">
                  {{ tx.Category }}
                </span>
              </td>
              <td class="col-cost">${{ tx.Cost.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
              <td class="col-notes">{{ tx.Notes || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LineChart           from '../components/charts/LineChart.vue'
import HorizontalBarChart  from '../components/charts/HorizontalBarChart.vue'
import DonutChart          from '../components/charts/DonutChart.vue'
import StatCard            from '../components/StatCard.vue'
import {
  toSpendingSeries,
  toCumulativeSeries,
  toCategorySpendingSeries,
  toCategoryDonutSeries,
  toMonthlyDonutSeries,
  computeAverage,
  toTopItemsSeries,
  computeStats,
  getCategoryColor,
} from '../composables/useChartData.js'
import FilterBar          from '../components/FilterBar.vue'
import { useGlobalFilters } from '../composables/useGlobalFilters.js'

const { availableYears, selectedYear, search, transactions, loading, initFilters } = useGlobalFilters()

onMounted(() => initFilters())

// ── Chart controls ─────────────────────────────────────────────────────────
const chartOptions = [
  { key: 'trend',      label: 'Monthly Trend' },
  { key: 'category',   label: 'By Category' },
  { key: 'cumulative', label: 'Cumulative' },
]
const activeChart = ref('trend')

const bucketOptions = [
  { label: '1-day',  value: 1  },
  { label: '7-day',  value: 7  },
  { label: '28-day', value: 28 },
]
const bucketDays = ref(28)

// ── Filtered transactions (drives all charts + stats) ─────────────────────
const filteredTransactions = computed(() => {
  let txs = transactions.value
  const q = search.value.trim().toLowerCase()
  if (q) txs = txs.filter(t =>
    t.Item.toLowerCase().includes(q) || t.Category.toLowerCase().includes(q)
  )
  return txs
})

// ── Stats ──────────────────────────────────────────────────────────────────
const stats = computed(() => computeStats(filteredTransactions.value))

// ── Line chart series (only compute the active chart) ────────────────────
const spendingSeries    = computed(() => activeChart.value !== 'trend'      ? [] : toSpendingSeries(filteredTransactions.value, bucketDays.value))
const spendingAverage   = computed(() => activeChart.value !== 'trend'      ? 0  : computeAverage(filteredTransactions.value,   bucketDays.value))
const cumulativeSeries  = computed(() => activeChart.value !== 'cumulative' ? [] : toCumulativeSeries(filteredTransactions.value, bucketDays.value))
const categorySeries    = computed(() => activeChart.value !== 'category'   ? [] : toCategorySpendingSeries(filteredTransactions.value, bucketDays.value))

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

/* ── Table ───────────────────────────────────────── */
.table-wrapper { overflow-x: auto; }

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.data-table th {
  text-align: left;
  padding: 0.6rem 0.75rem;
  background: #f5f5f5;
  border-bottom: 2px solid #e0e0e0;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #666;
}
.data-table td {
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: middle;
}
.data-table tbody tr:hover { background: #fafafa; }
.col-cost  { text-align: right; font-weight: 600; font-variant-numeric: tabular-nums; }
.col-notes { color: #888; font-style: italic; max-width: 200px; }

.category-badge {
  display: inline-block;
  padding: 0.15rem 0.55rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.7);
  white-space: nowrap;
}
</style>
