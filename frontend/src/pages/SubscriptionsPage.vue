<template>
  <div class="page-container">
    <FilterBar :showSearch="true" />

    <h1 class="section-title">Digital Subscriptions</h1>
    <div class="top-controls">
      <div class="toggle-row-group">
        <label class="toggle-row">
          <input v-model="includeStaleSubscriptions" type="checkbox" />
          <span>Include items that have not had a purchase in the last 365 days</span>
        </label>
        <label class="toggle-row">
          <input v-model="ignoreSoftware" type="checkbox" />
          <span>Ignore items named Software</span>
        </label>
        <label class="toggle-row">
          <input v-model="requireMinimumChargeCount" type="checkbox" />
          <span>Only include items with at least 6 charges</span>
        </label>
      </div>
      <div class="frequency-tabs">
        <button
          v-for="tab in frequencyTabs"
          :key="tab"
          class="tab-btn"
          :class="{ 'tab-btn--active': activeFrequencyTab === tab }"
          @click="activeFrequencyTab = tab"
        >
          {{ tab }}
        </button>
      </div>
      <div class="kpi-row kpi-row--top">
        <StatCard label="Subscriptions Tracked" :value="subscriptionSummaryRows.length" format="integer" />
        <StatCard label="Subscription Charges" :value="visibleSubscriptionTransactions.length" format="integer" />
        <StatCard label="Total Spent" :value="totalSubscriptionSpendSelected" format="currency" :privacyMode="privacyMode" />
      </div>
    </div>

    <section v-if="visibleSubscriptionTransactions.length" class="chart-section">
      <div class="bubble-chart-wrap">
        <BubbleChart
          title="Subscription Spend Bubble View"
          :points="bubblePoints"
          layout="packed"
          :showLegend="true"
          yLabel="Total Spent"
          yFormat="currency"
          :height="320"
          :privacyMode="privacyMode"
        />
      </div>
    </section>

    <section class="chart-section">
      <DataTable
        v-if="visibleSubscriptionTransactions.length"
        :columns="summaryColumns"
        :rows="subscriptionSummaryRows"
        rowKey="subscriptionKey"
        emptyMessage="No subscriptions found."
        defaultSortKey="totalSpent"
        defaultSortDir="desc"
      >
        <template #cell-averagePrice="{ value }">{{ formatCurrency(value) }}</template>
        <template #cell-mostRecentPrice="{ value }">{{ formatCurrency(value) }}</template>
        <template #cell-highestPrice="{ value }">{{ formatCurrency(value) }}</template>
        <template #cell-lowestPrice="{ value }">{{ formatCurrency(value) }}</template>
        <template #cell-totalSpent="{ value }">{{ formatCurrency(value) }}</template>
        <template #cell-avgIntervalDays="{ row, value }">
          {{ row.hasRecurringPattern ? `${value.toFixed(1)} days` : '-' }}
        </template>
      </DataTable>
      <div v-else class="empty-state">
        No transactions matched the current filters in category <code>Digital Subscriptions</code>.
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import BubbleChart from '../components/charts/BubbleChart.vue'
import FilterBar from '../components/ui/FilterBar.vue'
import StatCard from '../components/ui/StatCard.vue'
import DataTable from '../components/tables/DataTable.vue'
import { useGlobalFilters } from '../composables/useGlobalFilters.js'

const { search, selectedTags, privacyMode, transactions, initFilters } = useGlobalFilters()

onMounted(() => initFilters())
const includeStaleSubscriptions = ref(true)
const ignoreSoftware = ref(true)
const requireMinimumChargeCount = ref(true)
const activeFrequencyTab = ref('All')

const TAB_ORDER = [
  'One-Time',
  'Weekly',
  'Monthly',
  'Every Two Months',
  'Every Six Months',
  'Yearly',
  'Irregular',
]

const summaryColumns = [
  { key: 'subscriptionName', label: 'Subscription', align: 'left', sortable: true },
  { key: 'chargesCount', label: 'Charges', align: 'center', sortable: true },
  { key: 'avgIntervalDays', label: 'Avg Interval', align: 'right', sortable: true },
  { key: 'averagePrice', label: 'Average Price', align: 'right', sortable: true },
  { key: 'mostRecentPrice', label: 'Most Recent Price', align: 'right', sortable: true },
  { key: 'highestPrice', label: 'Highest Price', align: 'right', sortable: true },
  { key: 'lowestPrice', label: 'Lowest Price', align: 'right', sortable: true },
  { key: 'totalSpent', label: 'Total Spent', align: 'right', sortable: true },
]

function parseTags(tags) {
  if (!tags || typeof tags !== 'string') return []
  return tags
    .split(',')
    .map((tag) => tag.trim().toLowerCase())
    .filter(Boolean)
}

function normalizeSubscriptionName(name) {
  return String(name || '').trim()
}

function isSoftwareSubscription(name) {
  return normalizeSubscriptionName(name).toLowerCase() === 'software'
}

function toValidCost(value) {
  const cost = Number(value)
  return Number.isFinite(cost) ? cost : null
}

function toValidDate(dateString) {
  const d = new Date(dateString)
  return Number.isNaN(d.getTime()) ? null : d
}

function cadenceFromAvgInterval(avgIntervalDays, chargesCount) {
  if (chargesCount <= 1 || avgIntervalDays == null) return 'One-Time'
  if (avgIntervalDays <= 10) return 'Weekly'
  if (avgIntervalDays <= 45) return 'Monthly'
  if (avgIntervalDays <= 100) return 'Every Two Months'
  if (avgIntervalDays <= 260) return 'Every Six Months'
  if (avgIntervalDays <= 420) return 'Yearly'
  return 'Irregular'
}

function averageRecentIntervalDays(entries, recentChargeCount = 6) {
  const recentEntries = entries.slice(-recentChargeCount)
  const intervals = []

  for (let i = 1; i < recentEntries.length; i += 1) {
    const diffMs = recentEntries[i].date.getTime() - recentEntries[i - 1].date.getTime()
    if (diffMs > 0) intervals.push(diffMs / 86_400_000)
  }

  if (!intervals.length) return null
  return intervals.reduce((sum, d) => sum + d, 0) / intervals.length
}

const subscriptionTransactions = computed(() => {
  let txs = transactions.value.filter(
    (tx) => String(tx.Category || '').trim().toLowerCase() === 'digital subscriptions'
  )

  if (ignoreSoftware.value) {
    txs = txs.filter((tx) => !isSoftwareSubscription(tx.Item))
  }

  const q = search.value.trim().toLowerCase()
  if (q) {
    txs = txs.filter((tx) =>
      String(tx.Item || '').toLowerCase().includes(q) ||
      String(tx.Notes || '').toLowerCase().includes(q)
    )
  }

  if (selectedTags.value.length) {
    txs = txs.filter((tx) => {
      const txTags = parseTags(tx.Tags)
      return txTags.some((tag) => selectedTags.value.includes(tag))
    })
  }

  return txs
})

const groupedSubscriptions = computed(() => {
  const groups = new Map()

  for (const tx of subscriptionTransactions.value) {
    const subscriptionName = normalizeSubscriptionName(tx.Item) || 'Unknown subscription'
    const key = subscriptionName.toLowerCase()
    if (!groups.has(key)) {
      groups.set(key, {
        key,
        subscriptionName,
        entries: [],
      })
    }

    const cost = toValidCost(tx.Cost)
    const date = toValidDate(tx.Date)
    if (cost == null || !date) continue

    groups.get(key).entries.push({
      ...tx,
      cost,
      date,
      dateText: tx.Date,
    })
  }

  for (const group of groups.values()) {
    group.entries.sort((a, b) => a.date - b.date)
  }

  return [...groups.values()].filter((group) => group.entries.length > 0)
})

const summaryRows = computed(() =>
  groupedSubscriptions.value.map((group) => {
    const costs = group.entries.map((entry) => entry.cost)
    const totalSpent = costs.reduce((sum, cost) => sum + cost, 0)
    const chargesCount = costs.length
    const averagePrice = totalSpent / chargesCount
    const highestPrice = Math.max(...costs)
    const lowestPrice = Math.min(...costs)
    const mostRecentEntry = group.entries[group.entries.length - 1]

    const avgIntervalDays = averageRecentIntervalDays(group.entries)

    return {
      subscriptionKey: group.key,
      subscriptionName: group.subscriptionName,
      chargesCount,
      hasRecurringPattern: avgIntervalDays != null,
      avgIntervalDays: avgIntervalDays ?? -1,
      cadence: cadenceFromAvgInterval(avgIntervalDays, chargesCount),
      averagePrice,
      lastChargeDate: mostRecentEntry.dateText,
      mostRecentPrice: mostRecentEntry.cost,
      highestPrice,
      lowestPrice,
      totalSpent,
    }
  })
)

const staleCutoffDate = computed(() => {
  const now = new Date()
  return new Date(now.getFullYear() - 1, now.getMonth(), now.getDate())
})

const filteredSummaryRowsByStale = computed(() =>
  summaryRows.value.filter((row) =>
    includeStaleSubscriptions.value || new Date(row.lastChargeDate) >= staleCutoffDate.value
  )
)

const filteredSummaryRows = computed(() =>
  filteredSummaryRowsByStale.value.filter((row) =>
    !requireMinimumChargeCount.value || row.chargesCount >= 6
  )
)

const frequencyTabs = computed(() => {
  const set = new Set(filteredSummaryRows.value.map((row) => row.cadence))
  return ['All', ...TAB_ORDER.filter((tab) => set.has(tab))]
})

watch(frequencyTabs, (tabs) => {
  if (!tabs.includes(activeFrequencyTab.value)) {
    activeFrequencyTab.value = tabs[0] || ''
  }
}, { immediate: true })

const subscriptionSummaryRows = computed(() =>
  activeFrequencyTab.value === 'All'
    ? filteredSummaryRows.value
    : filteredSummaryRows.value.filter((row) => row.cadence === activeFrequencyTab.value)
)

const visibleSubscriptionKeys = computed(() =>
  new Set(subscriptionSummaryRows.value.map((row) => row.subscriptionKey))
)

const visibleSubscriptionTransactions = computed(() =>
  groupedSubscriptions.value
    .filter((group) => visibleSubscriptionKeys.value.has(group.key))
    .flatMap((group) => group.entries.map((entry) => ({
      Item: entry.Item,
      Category: entry.Category,
      Cost: entry.Cost,
      Date: entry.Date,
      Store: entry.Store,
      Tags: entry.Tags,
      Notes: entry.Notes,
    })))
)

const totalSubscriptionSpendSelected = computed(() =>
  visibleSubscriptionTransactions.value.reduce((sum, tx) => sum + (Number(tx.Cost) || 0), 0)
)

const bubblePoints = computed(() => {
  const rows = subscriptionSummaryRows.value
  if (!rows.length) return []

  return rows.map((row) => ({
    label: row.subscriptionName,
    value: row.totalSpent,
  }))
})

function formatCurrency(value) {
  if (privacyMode.value) return '$****'
  return `$${Number(value || 0).toLocaleString('en-AU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
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

.section-title {
  margin: 0 0 0.8rem;
  font-size: 1.1rem;
  color: var(--text);
  letter-spacing: -0.01em;
}

.top-controls {
  margin-bottom: 0.95rem;
}

.toggle-row-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.7rem;
}

.toggle-row {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.84rem;
  color: var(--text-muted);
  font-weight: 500;
}

.frequency-tabs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  width: 100%;
  gap: 0.45rem;
  margin-bottom: 0.85rem;
}

.tab-btn {
  width: 100%;
  min-height: 35px;
  padding: 0.3rem 0.65rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-soft);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
  transition: background var(--transition), border-color var(--transition), color var(--transition), box-shadow var(--transition);
}

.tab-btn:hover {
  background: #e8f0fd;
  border-color: #c9dbfb;
  color: var(--accent-strong);
}

.tab-btn--active {
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  border-color: var(--accent);
  color: #fff;
  box-shadow: 0 8px 16px rgba(15, 62, 168, 0.24);
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.kpi-row--top {
  margin-bottom: 0.85rem;
}

.bubble-chart-wrap {
  margin: 0.8rem 0 0.25rem;
}

.empty-state {
  color: var(--text-faint);
  font-style: italic;
}

@media (max-width: 860px) {
  .kpi-row {
    grid-template-columns: 1fr;
  }
}
</style>


