<template>
  <DataTable
    :title="title"
    :columns="txColumns"
    :rows="tableRows"
    rowKey="id"
    emptyMessage="No transactions found."
  >
    <template #cell-category="{ value }">
      <span class="category-badge" :style="{ background: getCategoryColor(value) }">
        {{ value }}
      </span>
    </template>
    <template #cell-cost="{ value }">
      {{ formatCost(value) }}
    </template>
    <template #cell-store="{ value }">
      <div v-if="getStoreDisplayName(value)" class="store-cell">
        <img
          v-if="getStoreIcon(value)"
          :src="getStoreIcon(value)"
          :alt="getStoreDisplayName(value)"
          :title="getStoreDisplayName(value)"
          class="store-icon"
        />
        <span v-else>{{ getStoreDisplayName(value) }}</span>
      </div>
      <span v-else>—</span>
    </template>
    <template #cell-tags="{ row }">
      <div v-if="hasTags(row.tags)" class="tags-list">
        <span v-for="tag in parseTags(row.tags)" :key="`${row.id}-${tag}`" class="tag-chip">
          {{ tag }}
        </span>
      </div>
      <span v-else>—</span>
    </template>
    <template #cell-notes="{ value }">
      <span class="col-notes">{{ value || '—' }}</span>
    </template>
  </DataTable>
</template>

<script setup>
import { computed } from 'vue'
import DataTable from './DataTable.vue'
import { getCategoryColor } from '../composables/useChartData.js'
import { getStoreIcon } from '../config/storeIcons.js'

const props = defineProps({
  title: { type: String, default: 'Transactions' },
  transactions: { type: Array, required: true },
  privacyMode: { type: Boolean, default: false },
})

const txColumns = [
  { key: 'date', label: 'Date', align: 'left' },
  { key: 'item', label: 'Item', align: 'left' },
  { key: 'category', label: 'Category', align: 'left' },
  { key: 'cost', label: 'Cost', align: 'center' },
  { key: 'store', label: 'Store', align: 'center' },
  { key: 'tags', label: 'Tags', align: 'left' },
  { key: 'notes', label: 'Notes', align: 'left' },
]

const tableRows = computed(() =>
  props.transactions.map((tx, index) => ({
    id: tx.ID ?? index,
    date: tx.Date,
    item: tx.Item,
    category: tx.Category,
    cost: tx.Cost,
    store: tx.Store,
    tags: tx.Tags,
    notes: tx.Notes,
  }))
)

function parseTags(tags) {
  if (!tags || typeof tags !== 'string') return []
  return tags
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

function hasTags(tags) {
  return parseTags(tags).length > 0
}

function getStoreDisplayName(store) {
  const rawStore = String(store || '').trim()
  return rawStore || null
}

function formatCost(cost) {
  if (props.privacyMode) return '$••••'
  return `$${Number(cost).toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}
</script>

<style scoped>
.col-notes { color: #888; font-style: italic; max-width: 220px; }

.category-badge {
  display: inline-block;
  padding: 0.15rem 0.55rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.7);
  white-space: nowrap;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.tag-chip {
  display: inline-block;
  background: #eef2f7;
  border: 1px solid #d7dde8;
  color: #44506a;
  border-radius: 999px;
  padding: 0.1rem 0.5rem;
  font-size: 0.72rem;
  white-space: nowrap;
}

.store-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 1.4rem;
}

.store-icon {
  width: 1.8rem;
  height: 1.8rem;
  object-fit: contain;
}
</style>
