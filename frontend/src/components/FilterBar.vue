<template>
  <div class="filter-bar">
    <div class="filter-left">
      <label class="filter-label">Year</label>
      <select v-model="selectedYear" class="year-select">
        <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
      </select>
      <button
        class="remake-btn"
        :disabled="remaking"
        @click="handleRemakeXlsx"
      >
        {{ remaking ? 'Remaking…' : 'Remake XLSX' }}
      </button>
    </div>
    <div v-if="showSearch" class="filter-right">
      <input
        v-model="search"
        class="search-input"
        placeholder="Search item or category…"
        type="search"
      />
    </div>
    <p v-if="remakeMessage" class="remake-message">{{ remakeMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useGlobalFilters } from '../composables/useGlobalFilters.js'

defineProps({
  showSearch: { type: Boolean, default: false },
})

const { availableYears, selectedYear, search, refreshTransactions } = useGlobalFilters()
const remaking = ref(false)
const remakeMessage = ref('')

async function handleRemakeXlsx() {
  remaking.value = true
  remakeMessage.value = ''

  try {
    const response = await fetch('/api/xlsx/reformat', { method: 'POST' })
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data?.detail || 'Failed to remake XLSX file.')
    }

    await refreshTransactions()
    remakeMessage.value = data?.message || 'XLSX remake completed.'
  } catch (error) {
    remakeMessage.value = error?.message || 'Failed to remake XLSX file.'
  } finally {
    remaking.value = false
  }
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-left  { display: flex; align-items: center; gap: 0.75rem; }
.filter-right { display: flex; align-items: center; margin-left: auto; }
.filter-label { font-size: 0.8rem; font-weight: 600; color: #666; text-transform: uppercase; }

.year-select {
  padding: 0.35rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 0.85rem;
  background: #fff;
  cursor: pointer;
  outline: none;
  transition: border-color 0.15s;
}
.year-select:focus { border-color: #1e293b; }

.search-input {
  padding: 0.4rem 0.8rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 0.85rem;
  width: 240px;
  outline: none;
  transition: border-color 0.15s;
}
.search-input:focus { border-color: #1a1a2e; }

.remake-btn {
  padding: 0.35rem 0.75rem;
  border: 1px solid #1e293b;
  border-radius: 5px;
  background: #1e293b;
  color: #fff;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s ease;
}
.remake-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.remake-message {
  margin: 0;
  font-size: 0.8rem;
  color: #555;
  flex-basis: 100%;
}
</style>
