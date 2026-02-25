<template>
  <section class="chart-section">
    <h2 class="section-title">{{ title }}</h2>
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Item</th>
            <th>Category</th>
            <th class="col-cost">Cost</th>
            <th>Store</th>
            <th>Tags</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(tx, i) in transactions" :key="i">
            <td>{{ tx.Date }}</td>
            <td>{{ tx.Item }}</td>
            <td>
              <span class="category-badge" :style="{ background: getCategoryColor(tx.Category) }">
                {{ tx.Category }}
              </span>
            </td>
            <td class="col-cost">${{ Number(tx.Cost).toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
            <td>{{ tx.Store || '—' }}</td>
            <td>{{ tx.Tags || '—' }}</td>
            <td class="col-notes">{{ tx.Notes || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { getCategoryColor } from '../composables/useChartData.js'

defineProps({
  title: { type: String, default: 'Transactions' },
  transactions: { type: Array, required: true },
})
</script>

<style scoped>
.chart-section {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 1rem;
}

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
</style>
