<template>
  <div class="page-container">

    <!-- ── Controls bar ─────────────────────────────────────────── -->
    <FilterBar :showSearch="true" />

    <!-- ── Card 1: Category selector ─────────────────────────────── -->
    <div class="drill-controls">
      <label class="control-label">Drill into category</label>
      <select v-model="selectedCategory" class="category-select">
        <option v-for="cat in availableCategories" :key="cat" :value="cat">{{ cat }}</option>
      </select>
    </div>

    <!-- ── Card 2: KPI Stats (only when data exists) ────────────── -->
    <KPIStats :stats="stats" :privacyMode="privacyMode" />

    <!-- ── Card 3: Bar chart (only when data exists) ───────────── -->
    <section v-if="filteredByCategory.length" class="chart-section">
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
    </section>

    <!-- ── Card 4: Top 10 transactions table (only when data exists) ─ -->
    <section v-if="filteredByCategory.length" class="chart-section">
      <TransactionsTable
        title="Top 10 Most Expensive Transactions"
        :transactions="top10ByCategory"
        :privacyMode="privacyMode"
      />
    </section>

    <!-- ── Card 5: Frequent items table (only when data exists) ─── -->
    <section v-if="filteredByCategory.length" class="chart-section">
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
    </section>

    <!-- ── Empty state: shown as its own card when no data ───────── -->
    <section v-if="!filteredByCategory.length" class="chart-section">
      <div class="empty-state">
        No transactions found for the selected filters.
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import HorizontalBarChart from '../components/charts/HorizontalBarChart.vue'
import TransactionsTable from '../components/tables/TransactionsTable.vue'
import KPIStats from '../components/ui/KPIStats.vue'
import DataTable from '../components/tables/DataTable.vue'
import {
  toTopItemsSeries,
  computeStats,
} from '../composables/useChartData.js'
import FilterBar          from '../components/ui/FilterBar.vue'
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

// ── Category totals for sorting ────────────────────────────────────────────
const categoryTotals = computed(() => {
  const totals = new Map()
  for (const tx of yearFiltered.value) {
    const cat = tx.Category
    const cost = Number(tx.Cost) || 0
    totals.set(cat, (totals.get(cat) || 0) + cost)
  }
  return totals
})

// ── All categories present in this year's data, sorted by total spent ──────
const availableCategories = computed(() =>
  [...new Set(yearFiltered.value.map(t => t.Category))].sort((a, b) =>
    (categoryTotals.value.get(b) || 0) - (categoryTotals.value.get(a) || 0)
  )
)

// Reset selectedCategory to first available (most spent) whenever the list changes
watch(availableCategories, (cats) => {
  if (cats.length && !cats.includes(selectedCategory.value)) {
    selectedCategory.value = cats[0]
  }
}, { immediate: true })

// ── Transactions filtered by year AND selected category ─────────────────────
const filteredByCategory = computed(() =>
  yearFiltered.value.filter(t => t.Category === selectedCategory.value)
)

// ── Stats ──────────────────────────────────────────────────────────────────
const stats = computed(() => computeStats(filteredByCategory.value))

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
  max-width: 1600px;
  margin: 0 auto;
  padding: 1.35rem 2rem 3rem;
}

.chart-section {
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.2rem 1.35rem;
  margin-bottom: 1.15rem;
  box-shadow: var(--shadow-sm);
}

.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
.section-title  {
  font-size: 1.02rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 1rem;
  letter-spacing: -0.01em;
}

.drill-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  padding: 0.75rem 0.95rem;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid var(--border);
}

.control-label {
  font-size: 0.86rem;
  color: var(--text-muted);
  font-weight: 600;
}

.category-select {
  min-height: 36px;
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
  outline: none;
  min-width: 200px;
  transition: border-color var(--transition), box-shadow var(--transition);
}
.category-select:focus {
  border-color: var(--ring);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.18);
}

.empty-state {
  text-align: center;
  color: var(--text-faint);
  padding: 1.8rem;
  font-style: italic;
}
</style>


