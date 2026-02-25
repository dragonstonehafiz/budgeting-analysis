/**
 * useGlobalFilters.js
 *
 * Module-level singleton refs for year, search, and transactions.
 * Because ES modules are only evaluated once, these refs persist across
 * page navigation for the entire browser session — no Pinia required.
 *
 * Usage in any page:
 *   const { availableYears, selectedYear, search, transactions, loading, initFilters } = useGlobalFilters()
 *   onMounted(() => initFilters())
 */
import { ref, watch } from 'vue'

// ── Singleton state ────────────────────────────────────────────────────────
const availableYears = ref(['All'])
const selectedYear   = ref('All')
const search         = ref('')
const transactions   = ref([])
const loading        = ref(false)

let yearsLoaded = false  // guard so we only hit /years once

// ── Data fetching ──────────────────────────────────────────────────────────
async function fetchTransactions(year) {
  loading.value = true
  try {
    const url = year === 'All' ? '/api/transactions/' : `/api/transactions/?year=${year}`
    transactions.value = await fetch(url).then(r => r.json())
  } catch {
    transactions.value = []
  } finally {
    loading.value = false
  }
}

/**
 * Call once in each page's onMounted.
 * Fetches years on first call only; always ensures transactions are loaded.
 */
async function initFilters() {
  if (!yearsLoaded) {
    try {
      const data = await fetch('/api/transactions/years').then(r => r.json())
      availableYears.value = ['All', ...data.years.slice().sort((a, b) => b - a)]
      yearsLoaded = true
    } catch {
      // backend not available — dropdown stays as ['All']
    }
  }
  // Fetch transactions if not yet loaded (e.g. first page visit)
  if (transactions.value.length === 0) {
    await fetchTransactions(selectedYear.value)
  }
}

// Re-fetch whenever the year changes — fires regardless of which page triggered it
watch(selectedYear, (year) => fetchTransactions(year))

// ── Public API ─────────────────────────────────────────────────────────────
export function useGlobalFilters() {
  return {
    availableYears,
    selectedYear,
    search,
    transactions,
    loading,
    initFilters,
  }
}
