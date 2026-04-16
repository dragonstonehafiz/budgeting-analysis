/**
 * useGlobalFilters.js
 *
 * Module-level singleton refs for year, search, and transactions.
 * Because ES modules are only evaluated once, these refs persist across
 * page navigation for the entire browser session.
 *
 * Usage in any page:
 *   const { availableYears, selectedYear, search, transactions, loading, initFilters } = useGlobalFilters()
 *   onMounted(() => initFilters())
 */
import { ref, watch } from 'vue'

const STORAGE_KEY = 'budgeting-analysis.global-filters'

// Singleton state
const availableYears = ref(['Last 365 Days', 'All'])
const selectedYear = ref('Last 365 Days')
const search = ref('')
const selectedTags = ref([])
const privacyMode = ref(false)
const transactions = ref([])
const loading = ref(false)

let yearsLoaded = false // guard so we only hit /years once
let sessionStateHydrated = false

function canUseSessionStorage() {
  return typeof window !== 'undefined' && typeof window.sessionStorage !== 'undefined'
}

function sanitizeStoredState(parsed) {
  if (!parsed || typeof parsed !== 'object') return null

  return {
    selectedYear: typeof parsed.selectedYear === 'string' ? parsed.selectedYear : 'Last 365 Days',
    search: typeof parsed.search === 'string' ? parsed.search : '',
    selectedTags: Array.isArray(parsed.selectedTags)
      ? parsed.selectedTags.filter((tag) => typeof tag === 'string')
      : [],
    privacyMode: typeof parsed.privacyMode === 'boolean' ? parsed.privacyMode : false,
  }
}

function hydrateSessionState() {
  if (sessionStateHydrated || !canUseSessionStorage()) return

  sessionStateHydrated = true

  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return

    const saved = sanitizeStoredState(JSON.parse(raw))
    if (!saved) return

    selectedYear.value = saved.selectedYear
    search.value = saved.search
    selectedTags.value = saved.selectedTags
    privacyMode.value = saved.privacyMode
  } catch {
    // Ignore malformed session state and keep defaults.
  }
}

function persistSessionState() {
  if (!sessionStateHydrated || !canUseSessionStorage()) return

  const payload = {
    selectedYear: selectedYear.value,
    search: search.value,
    selectedTags: selectedTags.value,
    privacyMode: privacyMode.value,
  }

  try {
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
  } catch {
    // Ignore storage failures and continue using in-memory state.
  }
}

// Data fetching
async function fetchTransactions(year) {
  loading.value = true
  try {
    let url = ''
    if (year === 'All') {
      url = '/api/transactions/'
    } else if (year === 'Last 365 Days') {
      const startDate = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
      const endDate = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
      url = `/api/transactions/?start_date=${startDate}&end_date=${endDate}`
    } else {
      url = `/api/transactions/?year=${year}`
    }

    transactions.value = await fetch(url).then((r) => r.json())
  } catch {
    transactions.value = []
  } finally {
    loading.value = false
  }
}

async function fetchYears(force = false) {
  if (yearsLoaded && !force) return
  try {
    const data = await fetch('/api/transactions/years').then((r) => r.json())
    availableYears.value = ['Last 365 Days', 'All', ...data.years.slice().sort((a, b) => b - a)]
    yearsLoaded = true
  } catch {
    // backend not available - dropdown stays with defaults
  }
}

/**
 * Call once in each page's onMounted.
 * Fetches years on first call only; always ensures transactions are loaded.
 */
async function initFilters() {
  hydrateSessionState()
  await fetchYears()

  // Fetch transactions if not yet loaded (e.g. first page visit)
  if (transactions.value.length === 0) {
    await fetchTransactions(selectedYear.value)
  }
}

// Re-fetch whenever the year changes.
watch(selectedYear, (year) => fetchTransactions(year))
watch([selectedYear, search, selectedTags, privacyMode], persistSessionState, { deep: true })

async function refreshTransactions() {
  await fetchTransactions(selectedYear.value)
}

async function reloadFromXlsx() {
  await fetchYears(true)
  await fetchTransactions(selectedYear.value)
}

// Public API
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
    reloadFromXlsx,
  }
}
