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

      <button class="remake-btn" :disabled="remaking || reloading" @click="handleRemakeXlsx">
        {{ remaking ? 'Remaking...' : 'Remake XLSX' }}
      </button>

      <button class="reload-btn" :disabled="reloading || remaking" @click="handleReloadXlsx">
        {{ reloading ? 'Reloading...' : 'Reload XLSX' }}
      </button>

      <button
        type="button"
        class="privacy-btn"
        :class="{ 'privacy-btn--active': privacyMode }"
        @click="privacyMode = !privacyMode"
      >
        {{ privacyMode ? 'Privacy: On' : 'Privacy: Off' }}
      </button>
    </div>

    <div v-if="showSearch" class="filter-right">
      <input
        v-model="search"
        class="search-input"
        placeholder="Search item or notes..."
        type="search"
      />
    </div>

  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useGlobalFilters } from '../../composables/useGlobalFilters.js'
import { useToast } from '../../composables/useToast.js'

defineProps({
  showSearch: { type: Boolean, default: false },
})

const {
  availableYears,
  selectedYear,
  selectedTags,
  privacyMode,
  search,
  transactions,
  refreshTransactions,
  reloadFromXlsx,
} = useGlobalFilters()

const remaking = ref(false)
const reloading = ref(false)
const isTagPickerOpen = ref(false)
const tagPickerRef = ref(null)
const { showToast } = useToast()

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
  showToast('Remaking XLSX...', { type: 'info', persistent: true })

  try {
    const response = await fetch('/api/xlsx/reformat', { method: 'POST' })
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data?.detail || 'Failed to remake XLSX file.')
    }

    await refreshTransactions()
    showToast(data?.message || 'XLSX remake completed.', { type: 'success' })
  } catch (error) {
    showToast(error?.message || 'Failed to remake XLSX file.', { type: 'error', duration: 3000 })
  } finally {
    remaking.value = false
  }
}

async function handleReloadXlsx() {
  reloading.value = true
  showToast('Reloading XLSX data...', { type: 'info', persistent: true })

  try {
    await reloadFromXlsx()
    showToast('XLSX data reloaded.', { type: 'success' })
  } catch {
    showToast('Failed to reload XLSX data.', { type: 'error', duration: 3000 })
  } finally {
    reloading.value = false
  }
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  position: relative;
  z-index: 40;
  padding: 0.9rem 1rem;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(4px);
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  align-items: center;
  margin-left: auto;
}

.filter-label {
  font-size: 0.74rem;
  font-weight: 700;
  color: var(--text-faint);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.year-select {
  min-height: 36px;
  padding: 0.35rem 0.72rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.84rem;
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
  outline: none;
  transition: border-color var(--transition), box-shadow var(--transition);
}

.year-select:focus {
  border-color: var(--ring);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

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
  min-height: 36px;
  padding: 0.35rem 0.7rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: border-color var(--transition), box-shadow var(--transition), background var(--transition);
}

.tag-picker-caret {
  color: var(--text-faint);
  font-size: 0.78rem;
}

.tag-picker-menu {
  position: absolute;
  top: calc(100% + 0.35rem);
  left: 0;
  z-index: 120;
  min-width: 230px;
  max-width: 300px;
  max-height: 220px;
  overflow-y: auto;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 0.45rem;
}

.tag-option {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.28rem 0.32rem;
  border-radius: 6px;
  font-size: 0.84rem;
  color: var(--text-muted);
}

.tag-option:hover {
  background: var(--surface-soft);
}

.tag-clear-btn {
  width: 100%;
  margin: 0 0 0.35rem;
  padding: 0.28rem 0.45rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--surface-soft);
  color: var(--text-muted);
  font-size: 0.8rem;
  text-align: left;
  cursor: pointer;
}

.tag-empty {
  margin: 0.3rem 0.1rem;
  color: var(--text-faint);
  font-size: 0.8rem;
}

.tag-picker-btn:focus,
.tag-picker-btn:hover {
  border-color: var(--ring);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.18);
}

.tag-picker-menu:focus-within {
  outline: none;
  border-color: var(--ring);
}

.search-input {
  min-height: 36px;
  padding: 0.4rem 0.78rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  width: 240px;
  outline: none;
  background: var(--surface);
  color: var(--text);
  transition: border-color var(--transition), box-shadow var(--transition);
}

.search-input::placeholder {
  color: var(--text-faint);
}

.search-input:focus {
  border-color: var(--ring);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.remake-btn {
  min-height: 36px;
  padding: 0.35rem 0.82rem;
  border: 1px solid var(--accent);
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: #fff;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform var(--transition), box-shadow var(--transition), opacity var(--transition);
}

.remake-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 18px rgba(15, 62, 168, 0.3);
}

.remake-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.reload-btn {
  min-height: 36px;
  padding: 0.35rem 0.82rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color var(--transition), box-shadow var(--transition), background var(--transition);
}

.reload-btn:hover:not(:disabled),
.reload-btn:focus:not(:disabled) {
  border-color: var(--ring);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.18);
}

.reload-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.privacy-btn {
  min-height: 36px;
  padding: 0.35rem 0.78rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition), border-color var(--transition), color var(--transition);
}

.privacy-btn--active {
  border-color: var(--accent);
  background: var(--accent-soft);
  color: var(--accent-strong);
}

.privacy-btn:hover,
.privacy-btn:focus {
  border-color: var(--ring);
}

@media (max-width: 900px) {
  .filter-right {
    margin-left: 0;
    width: 100%;
  }

  .search-input {
    width: 100%;
  }
}
</style>
