<template>
  <section class="table-section">
    <h3 v-if="title" class="table-title">{{ title }}</h3>
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              :class="[alignClass(column.align), { 'th--sortable': column.sortable }]"
              @click="toggleSort(column)"
            >
              {{ column.label }}
              <span v-if="column.sortable && sortKey === column.key" class="sort-indicator">
                {{ sortDir === 'asc' ? '▲' : '▼' }}
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in sortedRows" :key="row[rowKey] ?? rowIndex">
            <td
              v-for="column in columns"
              :key="`${row[rowKey] ?? rowIndex}-${column.key}`"
              :class="alignClass(column.align)"
            >
              <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
                {{ row[column.key] ?? '—' }}
              </slot>
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td :colspan="columns.length" class="empty-row">{{ emptyMessage }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  rowKey: { type: String, default: 'id' },
  emptyMessage: { type: String, default: 'No data.' },
  defaultSortKey: { type: String, default: null },
  defaultSortDir: { type: String, default: 'asc' },
})

// Sort state
const sortKey = ref(props.defaultSortKey)
const sortDir = ref(props.defaultSortDir) // 'asc' | 'desc'

function alignClass(align = 'left') {
  return `col-${align}`
}

function toggleSort(column) {
  if (!column.sortable) return
  if (sortKey.value === column.key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = column.key
    sortDir.value = 'asc'
  }
}

const sortedRows = computed(() => {
  if (!sortKey.value) return props.rows
  return [...props.rows].sort((a, b) => {
    const av = a[sortKey.value]
    const bv = b[sortKey.value]
    const cmp = typeof av === 'number' && typeof bv === 'number'
      ? av - bv
      : String(av ?? '').localeCompare(String(bv ?? ''))
    return sortDir.value === 'asc' ? cmp : -cmp
  })
})
</script>

<style scoped>
.table-section {
  margin-top: 0.25rem;
}

.table-title {
  margin: 0 0 0.9rem;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.01em;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.84rem;
  table-layout: fixed;
}

.data-table th {
  position: sticky;
  top: 0;
  z-index: 1;
  padding: 0.68rem 0.75rem;
  background: var(--surface-muted);
  border-bottom: 1px solid var(--border);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-faint);
  font-weight: 700;
}

.data-table td {
  padding: 0.62rem 0.75rem;
  border-bottom: 1px solid #edf2f7;
  vertical-align: middle;
  color: var(--text-muted);
}

.data-table tbody tr:nth-child(even) {
  background: #fcfdff;
}

.data-table tbody tr:hover {
  background: #f1f7ff;
}

.col-left {
  text-align: left;
}

.col-center {
  text-align: center;
}

.col-right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.empty-row {
  text-align: center;
  color: var(--text-faint);
  font-style: italic;
  padding: 1.2rem 0.75rem;
}

.th--sortable {
  cursor: pointer;
  user-select: none;
  transition: background var(--transition), color var(--transition);
}

.th--sortable:hover {
  background: #e8f0fd;
  color: var(--accent-strong);
}

.sort-indicator {
  margin-left: 0.24rem;
  font-size: 0.65rem;
  opacity: 0.72;
}
</style>
