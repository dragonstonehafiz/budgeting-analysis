<template>
  <div class="page-container">

    <!-- ── Controls bar ─────────────────────────────────────────── -->
    <div class="controls-bar">
      <div class="controls-left">
        <label class="control-label">Year</label>
        <div class="btn-group">
          <button
            v-for="y in availableYears"
            :key="y"
            class="btn"
            :class="{ 'btn--active': selectedYear === y }"
            @click="selectedYear = y"
          >{{ y }}</button>
        </div>
      </div>
    </div>

    <!-- ── Category overview donut ───────────────────────────────── -->
    <section class="chart-section">
      <div class="section-header">
        <h2 class="section-title">Spending by Category</h2>
      </div>
      <DonutChart
        :series="categorySeries"
        title=""
        :topN="0"
        :height="400"
      />
    </section>

    <!-- ── Category drill-down ───────────────────────────────────── -->
    <section class="chart-section">
      <div class="drill-controls">
        <label class="control-label">Drill into category</label>
        <select v-model="selectedCategory" class="category-select">
          <option value="All">All Categories</option>
          <option v-for="cat in availableCategories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>

      <template v-if="filteredByCategory.length">
        <!-- top items bar chart -->
        <HorizontalBarChart
          :series="categoryTopItems.series"
          :itemNames="categoryTopItems.itemNames"
          :itemColors="categoryTopItems.itemColors"
          :title="`Top Items — ${selectedCategory}`"
          :showTotals="true"
          :height="380"
        />

        <!-- top 10 transactions table -->
        <h3 class="sub-title">Top 10 Most Expensive Transactions</h3>
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
              <tr v-for="(tx, i) in top10ByCategory" :key="i">
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
      </template>

      <div v-else class="empty-state">
        No transactions found for the selected filters.
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import DonutChart         from '../components/charts/DonutChart.vue'
import HorizontalBarChart from '../components/charts/HorizontalBarChart.vue'
import {
  toCategoryDonutSeries,
  toTopItemsSeries,
  getCategoryColor,
} from '../composables/useChartData.js'
import { MOCK_TRANSACTIONS } from '../data/mockTransactions.js'

// ── Year filter ────────────────────────────────────────────────────────────
const availableYears = ['All', ...new Set(MOCK_TRANSACTIONS.map(t => String(t.Year || t.Date.slice(0, 4)))).values()].sort()
const selectedYear   = ref('All')

// ── Category filter ────────────────────────────────────────────────────────
const selectedCategory = ref('All')

// ── Transactions filtered by year ─────────────────────────────────────────
const yearFiltered = computed(() => {
  if (selectedYear.value === 'All') return MOCK_TRANSACTIONS
  return MOCK_TRANSACTIONS.filter(t =>
    (t.Year ?? t.Date.slice(0, 4)) == selectedYear.value
  )
})

// ── All categories present in this year's data ────────────────────────────
const availableCategories = computed(() =>
  [...new Set(yearFiltered.value.map(t => t.Category))].sort()
)

// ── Donut: full category breakdown for the selected year ──────────────────
const categorySeries = computed(() => toCategoryDonutSeries(yearFiltered.value))

// ── Transactions filtered by year AND selected category ───────────────────
const filteredByCategory = computed(() => {
  if (selectedCategory.value === 'All') return yearFiltered.value
  return yearFiltered.value.filter(t => t.Category === selectedCategory.value)
})

// ── Bar chart and table for drilled-down category ─────────────────────────
const categoryTopItems = computed(() => toTopItemsSeries(filteredByCategory.value, 10))

const top10ByCategory = computed(() =>
  [...filteredByCategory.value]
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

/* ── Controls bar ────────────────────────────────── */
.controls-bar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.controls-left { display: flex; align-items: center; gap: 0.75rem; }
.control-label { font-size: 0.8rem; font-weight: 600; color: #666; text-transform: uppercase; }

/* ── Buttons ─────────────────────────────────────── */
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

/* ── Chart sections ──────────────────────────────── */
.chart-section {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
.section-title  { font-size: 1rem; font-weight: 700; color: #333; margin: 0 0 1rem; }
.sub-title      { font-size: 0.95rem; font-weight: 700; color: #444; margin: 1.5rem 0 0.75rem; }

/* ── Drill controls ──────────────────────────────── */
.drill-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.category-select {
  padding: 0.35rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 0.85rem;
  background: #fff;
  cursor: pointer;
  outline: none;
  min-width: 200px;
  transition: border-color 0.15s;
}
.category-select:focus { border-color: #1a1a2e; }

/* ── Empty state ─────────────────────────────────── */
.empty-state {
  text-align: center;
  color: #aaa;
  padding: 2rem;
  font-style: italic;
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
