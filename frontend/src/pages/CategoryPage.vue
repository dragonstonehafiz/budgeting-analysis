<template>
  <div class="page-container">

    <!-- ── Controls bar ─────────────────────────────────────────── -->
    <FilterBar :showSearch="true" />


    <!-- ── Category drill-down ───────────────────────────────────── -->
    <section class="chart-section">
      <div class="drill-controls">
        <label class="control-label">Drill into category</label>
        <select v-model="selectedCategory" class="category-select">
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

        <TransactionsTable
          title="Top 10 Most Expensive Transactions"
          :transactions="top10ByCategory"
        />
      </template>

      <div v-else class="empty-state">
        No transactions found for the selected filters.
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import HorizontalBarChart from '../components/charts/HorizontalBarChart.vue'
import TransactionsTable from '../components/TransactionsTable.vue'
import {
  toTopItemsSeries,
} from '../composables/useChartData.js'
import FilterBar          from '../components/FilterBar.vue'
import { useGlobalFilters } from '../composables/useGlobalFilters.js'

const { availableYears, selectedYear, search, transactions, loading, initFilters } = useGlobalFilters()

onMounted(() => initFilters())

// ── Category filter ────────────────────────────────────────────────────────
const selectedCategory = ref('')

// ── Transactions filtered by year + search (backend handles year) ────────
const yearFiltered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return transactions.value
  return transactions.value.filter(t =>
    t.Item.toLowerCase().includes(q) || t.Category.toLowerCase().includes(q)
  )
})

// ── All categories present in this year's data ────────────────────────────
const availableCategories = computed(() =>
  [...new Set(yearFiltered.value.map(t => t.Category))].sort()
)

// Reset selectedCategory to first available whenever the list changes
watch(availableCategories, (cats) => {
  if (cats.length && !cats.includes(selectedCategory.value)) {
    selectedCategory.value = cats[0]
  }
}, { immediate: true })

// ── Transactions filtered by year AND selected category ─────────────────────
const filteredByCategory = computed(() =>
  yearFiltered.value.filter(t => t.Category === selectedCategory.value)
)

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

</style>
