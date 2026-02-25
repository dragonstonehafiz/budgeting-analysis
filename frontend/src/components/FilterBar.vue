<template>
  <div class="filter-bar">
    <div class="filter-left">
      <label class="filter-label">Year</label>
      <select v-model="selectedYear" class="year-select">
        <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
      </select>
      <label class="filter-label">Tags</label>
      <div ref="tagPickerRef" class="tag-picker">
        <button type="button" class="tag-picker-btn" @click="isTagPickerOpen = !isTagPickerOpen">
          <span>{{ selectedTagsLabel }}</span>
          <span class="tag-picker-caret">▾</span>
        </button>
        <div v-if="isTagPickerOpen" class="tag-picker-menu">
          <button
            v-if="selectedTags.length"
            type="button"
            class="tag-clear-btn"
            @click="selectedTags = []"
          >
            Clear
          </button>
          <label v-for="tag in availableTags" :key="tag" class="tag-option">
            <input v-model="selectedTags" type="checkbox" :value="tag" />
            <span>{{ tag }}</span>
          </label>
          <p v-if="!availableTags.length" class="tag-empty">No tags available.</p>
        </div>
      </div>
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
        placeholder="Search item or notes…"
        type="search"
      />
    </div>
    <p v-if="remakeMessage" class="remake-message">{{ remakeMessage }}</p>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useGlobalFilters } from '../composables/useGlobalFilters.js'

defineProps({
  showSearch: { type: Boolean, default: false },
})

const { availableYears, selectedYear, selectedTags, search, transactions, refreshTransactions } = useGlobalFilters()
const remaking = ref(false)
const remakeMessage = ref('')
const isTagPickerOpen = ref(false)
const tagPickerRef = ref(null)

function parseTags(tags) {
  if (!tags || typeof tags !== 'string') return []
  return tags
    .split(',')
    .map((tag) => tag.trim().toLowerCase())
    .filter(Boolean)
}

const availableTags = computed(() =>
  [...new Set(transactions.value.flatMap((tx) => parseTags(tx.Tags)))].sort((a, b) => a.localeCompare(b))
)

watch(availableTags, (tags) => {
  selectedTags.value = selectedTags.value.filter((tag) => tags.includes(tag))
})

const selectedTagsLabel = computed(() => {
  if (!selectedTags.value.length) return 'All tags'
  if (selectedTags.value.length <= 2) return selectedTags.value.join(', ')
  return `${selectedTags.value.length} tags selected`
})

function handleDocumentClick(event) {
  if (!tagPickerRef.value) return
  if (!tagPickerRef.value.contains(event.target)) {
    isTagPickerOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})

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

.tag-picker {
  position: relative;
}

.tag-picker-btn {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  min-width: 210px;
  max-width: 280px;
  padding: 0.35rem 0.7rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 0.85rem;
  background: #fff;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tag-picker-caret {
  color: #6b7280;
  font-size: 0.78rem;
}

.tag-picker-menu {
  position: absolute;
  top: calc(100% + 0.35rem);
  left: 0;
  z-index: 20;
  min-width: 230px;
  max-width: 300px;
  max-height: 220px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 0.45rem;
}

.tag-option {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.28rem 0.32rem;
  border-radius: 4px;
  font-size: 0.84rem;
}

.tag-option:hover {
  background: #f3f4f6;
}

.tag-clear-btn {
  width: 100%;
  margin: 0 0 0.35rem;
  padding: 0.28rem 0.45rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #f9fafb;
  color: #374151;
  font-size: 0.8rem;
  text-align: left;
  cursor: pointer;
}

.tag-empty {
  margin: 0.3rem 0.1rem;
  color: #6b7280;
  font-size: 0.8rem;
}

.tag-picker-btn:focus,
.tag-picker-btn:hover {
  border-color: #1e293b;
}

.tag-picker-menu:focus-within {
  outline: none;
  border-color: #1e293b;
}

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
