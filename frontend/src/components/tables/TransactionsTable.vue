<template>
  <DataTable
    :title="title"
    :columns="txColumns"
    :rows="tableRows"
    rowKey="id"
    emptyMessage="No transactions found."
    :defaultSortKey="defaultSortKey"
    :defaultSortDir="defaultSortDir"
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
import { getCategoryColor } from '../../composables/useChartData.js'
import { getStoreIcon } from '../../config/storeIcons.js'

const props = defineProps({
  title: { type: String, default: 'Transactions' },
  transactions: { type: Array, required: true },
  privacyMode: { type: Boolean, default: false },
  defaultSortKey: { type: String, default: null },
  defaultSortDir: { type: String, default: 'asc' },
})

const txColumns = [
  { key: 'date', label: 'Date', align: 'left', sortable: true },
  { key: 'item', label: 'Item', align: 'left', sortable: true },
  { key: 'category', label: 'Category', align: 'left', sortable: true },
  { key: 'cost', label: 'Cost', align: 'center', sortable: true },
  { key: 'store', label: 'Store', align: 'center' },
  { key: 'tags', label: 'Tags', align: 'left' },
  { key: 'notes', label: 'Notes', align: 'left' },
]

const tableRows = computed(() =>
  props.transactions.map((tx, index) => ({
    id: `${tx.Date ?? ''}-${tx.Item ?? ''}-${tx.Cost ?? ''}-${index}`,
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
.col-notes { color: var(--text-faint); font-style: italic; max-width: 220px; }

.category-badge {
  display: inline-block;
  padding: 0.18rem 0.58rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  color: rgba(15, 23, 42, 0.78);
  white-space: nowrap;
  border: 1px solid rgba(148, 163, 184, 0.36);
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.tag-chip {
  display: inline-block;
  background: #e9f1ff;
  border: 1px solid #c8dbfb;
  color: #1e3a8a;
  border-radius: 999px;
  padding: 0.1rem 0.5rem;
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
}

.store-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 1.4rem;
}

.store-icon {
  width: 1.55rem;
  height: 1.55rem;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.15);
}

/* Column width definitions */
:deep(.data-table) {
  td:nth-child(1),
  th:nth-child(1) { width: 120px; }  /* Date */

  td:nth-child(2),
  th:nth-child(2) { width: auto; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }   /* Item */

  td:nth-child(3),
  th:nth-child(3) { width: 170px; }   /* Category */

  td:nth-child(4),
  th:nth-child(4) { width: 80px; }  /* Cost */

  td:nth-child(5),
  th:nth-child(5) { width: 100px; } /* Store */

  td:nth-child(6),
  th:nth-child(6) { width: 12%; }   /* Tags */

  td:nth-child(7),
  th:nth-child(7) { width: auto; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; } /* Notes */
}
</style>
