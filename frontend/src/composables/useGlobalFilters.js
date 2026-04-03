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
const availableYears = ref(['Last 365 Days', 'All'])
const selectedYear   = ref('Last 365 Days')
const search         = ref('')
const selectedTags   = ref([])
const privacyMode    = ref(false)
const transactions   = ref([])
const loading        = ref(false)

let yearsLoaded = false  // guard so we only hit /years once

// ── Data fetching ──────────────────────────────────────────────────────────
async function fetchTransactions(year) {
  loading.value = true
  try {
    let url = ''
    if (year === 'All') {
      url = '/api/transactions/'
    }
    else if (year === 'Last 365 Days') {
      const startDate = new Date(Date.now() - 365*24*60*60*1000).toISOString().slice(0,10)
      const endDate = new Date(Date.now() + 24*60*60*1000).toISOString().slice(0,10)
      url = `/api/transactions/?start_date=${startDate}&end_date=${endDate}`
    }
    else {
      url = `/api/transactions/?year=${year}`
    }

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
      availableYears.value = ['Last 365 Days', 'All', ...data.years.slice().sort((a, b) => b - a)]
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

async function refreshTransactions() {
  await fetchTransactions(selectedYear.value)
}

// ── Public API ─────────────────────────────────────────────────────────────
export function useGlobalFilters() {
  return {
    availableYears,
    selectedYear,
    search,
    selectedTags,
    privacyMode,
    transactions,
    loading,
    initFilters,
    refreshTransactions,
  }
}
