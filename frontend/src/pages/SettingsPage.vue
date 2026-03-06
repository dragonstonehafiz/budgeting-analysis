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
  max-width: 1300px;
  margin: 0 auto;
  padding: 1.5rem 2rem 3rem;
}

.panel {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.panel-header {
  margin-bottom: 1rem;
}

.panel-title {
  margin: 0;
  font-size: 1.1rem;
  color: #1f2937;
}

.panel-subtitle {
  margin: 0.35rem 0 0;
  color: #6b7280;
  font-size: 0.88rem;
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

.data-table tbody tr:hover {
  background: #fafafa;
}

.store-icon {
  width: 1.2rem;
  height: 1.2rem;
  object-fit: contain;
}

.col-source {
  font-size: 0.8rem;
  word-break: break-all;
}

.col-source a {
  color: #2563eb;
  text-decoration: none;
}

.col-source a:hover {
  text-decoration: underline;
}

.empty-state {
  color: #6b7280;
  font-style: italic;
}
</style>
