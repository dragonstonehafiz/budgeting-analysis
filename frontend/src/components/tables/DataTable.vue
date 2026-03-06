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
              :class="alignClass(column.align)"
            >
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in rows" :key="row[rowKey] ?? rowIndex">
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
defineProps({
  title: { type: String, default: '' },
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  rowKey: { type: String, default: 'id' },
  emptyMessage: { type: String, default: 'No data.' },
})

function alignClass(align = 'left') {
  return `col-${align}`
}
</script>

<style scoped>
.table-section {
  margin-top: 1.25rem;
}

.table-title {
  margin: 0 0 0.75rem;
  font-size: 0.95rem;
  font-weight: 700;
  color: #333;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.data-table th {
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

.data-table tbody tr:hover {
  background: #fafafa;
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
  color: #888;
  font-style: italic;
}
</style>
