<template>
  <div class="filter-bar">
    <div class="filter-left">
      <label class="filter-label">Year</label>
      <select v-model="selectedYear" class="year-select">
        <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
      </select>
    </div>
    <div v-if="showSearch" class="filter-right">
      <input
        v-model="search"
        class="search-input"
        placeholder="Search item or category…"
        type="search"
      />
    </div>
  </div>
</template>

<script setup>
import { useGlobalFilters } from '../composables/useGlobalFilters.js'

defineProps({
  showSearch: { type: Boolean, default: false },
})

const { availableYears, selectedYear, search } = useGlobalFilters()
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
</style>
