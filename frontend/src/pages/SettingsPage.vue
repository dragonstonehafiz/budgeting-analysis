<template>
  <div class="page-container">
    <section class="panel">
      <div class="panel-header">
        <h1 class="panel-title">Store Icons</h1>
        <p class="panel-subtitle">
          Unique stores from transaction data and their configured icon mapping.
        </p>
      </div>

      <div v-if="loading" class="empty-state">Loading store list...</div>
      <div v-else-if="error" class="empty-state">{{ error }}</div>
      <div v-else-if="storeRows.length === 0" class="empty-state">No stores found.</div>
      <div v-else class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Store</th>
              <th>Icon</th>
              <th>Icon Source</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in storeRows" :key="row.key">
              <td>{{ row.displayName }}</td>
              <td>
                <img
                  v-if="row.iconUrl"
                  :src="row.iconUrl"
                  :alt="row.displayName"
                  :title="row.displayName"
                  class="store-icon"
                />
                <span v-else>—</span>
              </td>
              <td class="col-source">
                <a v-if="row.iconUrl" :href="row.iconUrl" target="_blank" rel="noreferrer noopener">
                  {{ row.iconUrl }}
                </a>
                <span v-else>No icon mapping</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getStoreIcon } from '../config/storeIcons.js'

const loading = ref(true)
const error = ref('')
const transactions = ref([])

const storeRows = computed(() => {
  const uniqueStores = [...new Set(
    transactions.value
      .map((tx) => String(tx?.Store || '').trim().toLowerCase())
      .filter(Boolean)
  )].sort((a, b) => a.localeCompare(b))

  return uniqueStores.map((storeName) => ({
    key: storeName,
    displayName: storeName,
    iconUrl: getStoreIcon(storeName),
  }))
})

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await fetch('/api/transactions/')
    if (!response.ok) throw new Error(`Request failed with status ${response.status}`)
    transactions.value = await response.json()
  } catch (err) {
    error.value = 'Unable to load stores from transactions.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 1.35rem 2rem 3rem;
}

.panel {
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.2rem 1.35rem;
  box-shadow: var(--shadow-sm);
}

.panel-header {
  margin-bottom: 0.9rem;
}

.panel-title {
  margin: 0;
  font-size: 1.12rem;
  color: var(--text);
  letter-spacing: -0.01em;
}

.panel-subtitle {
  margin: 0.35rem 0 0;
  color: var(--text-faint);
  font-size: 0.88rem;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.84rem;
}

.data-table th {
  text-align: left;
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
  padding: 0.6rem 0.75rem;
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

.store-icon {
  width: 1.35rem;
  height: 1.35rem;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.15);
}

.col-source {
  font-size: 0.8rem;
  word-break: break-all;
}

.col-source a {
  color: var(--accent);
  text-decoration: none;
}

.col-source a:hover {
  color: var(--accent-strong);
  text-decoration: underline;
}

.empty-state {
  color: var(--text-faint);
  font-style: italic;
}
</style>


