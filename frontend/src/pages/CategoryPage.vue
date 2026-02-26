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
          :key="`category-top-items-${selectedCategory}-${privacyMode}`"
          :series="categoryTopItems.series"
          :itemNames="categoryTopItems.itemNames"
          :itemColors="categoryTopItems.itemColors"
          :title="`Top Items — ${selectedCategory}`"
          :showTotals="true"
          :height="380"
          :privacyMode="privacyMode"
        />

        <TransactionsTable
          title="Top 10 Most Expensive Transactions"
          :transactions="top10ByCategory"
          :privacyMode="privacyMode"
        />

        <DataTable
          title="Items Bought More Than 5 Times"
          :columns="frequentItemsColumns"
          :rows="frequentItems"
          rowKey="item"
          emptyMessage="No items were bought more than 5 times."
        >
          <template #cell-totalSpent="{ value }">
            {{ formatCurrency(value) }}
          </template>
          <template #cell-avgPerItem="{ value }">
            {{ formatCurrency(value) }}
          </template>
        </DataTable>
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
import DataTable from '../components/DataTable.vue'
import {
  toTopItemsSeries,
} from '../composables/useChartData.js'
import FilterBar          from '../components/FilterBar.vue'
import { useGlobalFilters } from '../composables/useGlobalFilters.js'

const { search, selectedTags, privacyMode, transactions, initFilters } = useGlobalFilters()

onMounted(() => initFilters())

// ── Category filter ────────────────────────────────────────────────────────
const selectedCategory = ref('')

function parseTags(tags) {
  if (!tags || typeof tags !== 'string') return []
  return tags
    .split(',')
    .map((tag) => tag.trim().toLowerCase())
    .filter(Boolean)
}

// ── Transactions filtered by year + search (backend handles year) ────────
const yearFiltered = computed(() => {
  const q = search.value.trim().toLowerCase()
  let txs = transactions.value
  if (q) {
    txs = txs.filter(t =>
      t.Item.toLowerCase().includes(q) || String(t.Notes || '').toLowerCase().includes(q)
    )
  }
  if (selectedTags.value.length) {
    txs = txs.filter((t) => {
      const txTags = parseTags(t.Tags)
      return txTags.some((tag) => selectedTags.value.includes(tag))
    })
  }
  return txs
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

const frequentItems = computed(() => {
  const byItem = new Map()

  for (const tx of filteredByCategory.value) {
    const item = String(tx.Item || 'Unknown').trim() || 'Unknown'
    const cost = Number(tx.Cost)
    if (!byItem.has(item)) byItem.set(item, { item, count: 0, totalSpent: 0 })
    const row = byItem.get(item)
    row.count += 1
    if (Number.isFinite(cost)) row.totalSpent += cost
  }

  return [...byItem.values()]
    .filter((row) => row.count > 5)
    .map((row) => ({
      ...row,
      totalSpent: Number(row.totalSpent.toFixed(2)),
      avgPerItem: Number((row.totalSpent / row.count).toFixed(2)),
    }))
    .sort((a, b) => b.totalSpent - a.totalSpent || b.count - a.count || a.item.localeCompare(b.item))
})

const frequentItemsColumns = [
  { key: 'item', label: 'Item', align: 'left' },
  { key: 'count', label: 'Times Bought', align: 'center' },
  { key: 'totalSpent', label: 'Total Spent', align: 'right' },
  { key: 'avgPerItem', label: 'Average Per Item', align: 'right' },
]

function formatCurrency(value) {
  if (privacyMode.value) return '$••••'
  return `$${Number(value).toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}
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
