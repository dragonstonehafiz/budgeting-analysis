/**
 * useChartData.js
 *
 * Data transformation composable for time-series charts and donut charts.
 * All functions accept raw transactions and return chart-ready data arrays.
 *
 * Raw transaction shape expected:
 *   { Date: string|Date, Cost: number, Category: string, Month: string, MonthNum: number, ... }
 *
 * bucketDays controls the aggregation period:
 *   1  = daily
 *   7  = weekly
 *   28 = 4-weekly (approx monthly)
 */

// ---------------------------------------------------------------------------
// Category color map — mirrors category_colors.py on the Python side
// ---------------------------------------------------------------------------
export const CATEGORY_COLORS = {
  'Food & Beverages':          '#D9D9D9',
  'Books & Literature':        '#e9a9ff',
  'Gaming':                    '#bbe33d',
  'Digital Subscriptions':     '#fbffa9',
  'Movies & Media':            '#a05eff',
  'Music & Audio':             '#ffa9f2',
  'Electronics & Accessories': '#729fcf',
  'Clothing & Apparel':        '#D9D9D9',
  'Health & Personal Care':    '#a9ffc4',
  'Collectibles':              '#ffc85d',
  'Miscellaneous':             '#D9D9D9',
}

/**
 * Returns the hex color for a category, falling back to Miscellaneous.
 * @param {string} category
 * @returns {string} hex color
 */
export function getCategoryColor(category) {
  return CATEGORY_COLORS[category] ?? CATEGORY_COLORS['Miscellaneous']
}

/**
 * Groups transactions into fixed-size day buckets and sums the cost per bucket.
 *
 * @param {Array} transactions - raw transaction objects
 * @param {number} bucketDays  - bucket size in days (1, 7, or 28)
 * @returns {Array<{x: number, y: number}>} - sorted array of {x: timestamp ms, y: summed cost}
 */
export function bucketTransactions(transactions, bucketDays = 28) {
  if (!transactions || transactions.length === 0) return []

  const MS_PER_DAY = 86_400_000
  const bucketMs = bucketDays * MS_PER_DAY
  const map = new Map()

  for (const tx of transactions) {
    const date = new Date(tx.Date)
    if (isNaN(date)) continue
    const cost = parseFloat(tx.Cost)
    if (isNaN(cost)) continue

    // Floor to the nearest bucket boundary (from Unix epoch)
    const bucketKey = Math.floor(date.getTime() / bucketMs) * bucketMs
    map.set(bucketKey, (map.get(bucketKey) ?? 0) + cost)
  }

  return Array.from(map.entries())
    .sort(([a], [b]) => a - b)
    .map(([x, y]) => ({ x, y }))
}

/**
 * Returns a single spending series (bucketed totals).
 * Used for the Monthly Spending Trend chart.
 *
 * @param {Array}  transactions
 * @param {number} bucketDays
 * @returns {Array} ApexCharts series array
 */
export function toSpendingSeries(transactions, bucketDays = 28) {
  const data = bucketTransactions(transactions, bucketDays)
  return [{ name: 'Spending', data }]
}

/**
 * Returns series for the Rolling Average chart:
 *   - 'Raw' series: bucketed points (rendered as scatter dots)
 *   - 'Rolling Average' series: rolling mean over `window` buckets
 *   - 'Band' series: rangeArea between mean±std for volatility shading
 *
 * @param {Array}  transactions
 * @param {number} window     - number of buckets to include in each rolling window
 * @param {number} bucketDays
 * @returns {Array} ApexCharts series array (3 series)
 */
export function toRollingSeries(transactions, window = 3, bucketDays = 28) {
  const bucketed = bucketTransactions(transactions, bucketDays)
  if (bucketed.length === 0) return []

  const values = bucketed.map(p => p.y)

  const rollingMean = values.map((_, i) => {
    const slice = values.slice(Math.max(0, i - window + 1), i + 1)
    return slice.reduce((a, b) => a + b, 0) / slice.length
  })

  const rollingStd = values.map((_, i) => {
    const slice = values.slice(Math.max(0, i - window + 1), i + 1)
    if (slice.length < 2) return 0
    const mean = slice.reduce((a, b) => a + b, 0) / slice.length
    const variance = slice.reduce((a, b) => a + (b - mean) ** 2, 0) / slice.length
    return Math.sqrt(variance)
  })

  return [
    {
      name: 'Raw',
      type: 'scatter',
      data: bucketed.map((p, i) => ({ x: p.x, y: parseFloat(values[i].toFixed(2)) })),
    },
    {
      name: 'Rolling Average',
      type: 'line',
      data: bucketed.map((p, i) => ({ x: p.x, y: parseFloat(rollingMean[i].toFixed(2)) })),
    },
    {
      name: 'Volatility Band',
      type: 'rangeArea',
      data: bucketed.map((p, i) => ({
        x: p.x,
        y: [
          parseFloat(Math.max(0, rollingMean[i] - rollingStd[i]).toFixed(2)),
          parseFloat((rollingMean[i] + rollingStd[i]).toFixed(2)),
        ],
      })),
    },
  ]
}

/**
 * Returns a single cumulative spending series.
 * Each point's y-value is the running total of all spend up to that bucket.
 *
 * @param {Array}  transactions
 * @param {number} bucketDays
 * @returns {Array} ApexCharts series array
 */
export function toCumulativeSeries(transactions, bucketDays = 1) {
  const bucketed = bucketTransactions(transactions, bucketDays)
  let running = 0
  const data = bucketed.map(p => {
    running += p.y
    return { x: p.x, y: parseFloat(running.toFixed(2)) }
  })
  return [{ name: 'Cumulative Spend', data }]
}

/**
 * Computes the mean of all bucketed y-values.
 * Used for the average annotation line on the spending trend chart.
 *
 * @param {Array} transactions
 * @param {number} bucketDays
 * @returns {number}
 */
export function computeAverage(transactions, bucketDays = 28) {
  const bucketed = bucketTransactions(transactions, bucketDays)
  if (bucketed.length === 0) return 0
  const total = bucketed.reduce((sum, p) => sum + p.y, 0)
  return total / bucketed.length
}

// ---------------------------------------------------------------------------
// Donut chart helpers
// ---------------------------------------------------------------------------

/**
 * Groups transactions by Category and returns donut-ready series.
 * Each segment gets the category color from CATEGORY_COLORS.
 *
 * @param {Array} transactions
 * @returns {Array<{label: string, value: number, color: string}>}
 */
export function toCategoryDonutSeries(transactions) {
  if (!transactions || transactions.length === 0) return []

  const map = new Map()
  for (const tx of transactions) {
    const cat = tx.Category || 'Miscellaneous'
    const cost = parseFloat(tx.Cost)
    if (isNaN(cost)) continue
    map.set(cat, (map.get(cat) ?? 0) + cost)
  }

  return Array.from(map.entries())
    .map(([label, value]) => ({ label, value: parseFloat(value.toFixed(2)), color: getCategoryColor(label) }))
    .sort((a, b) => b.value - a.value)
}

/**
 * Groups transactions by calendar month and returns donut-ready series.
 * Months are sorted chronologically. Uses a generic color palette.
 *
 * @param {Array} transactions
 * @returns {Array<{label: string, value: number}>}
 */
export function toMonthlyDonutSeries(transactions) {
  if (!transactions || transactions.length === 0) return []

  // Use MonthNum + Month for correct sort order
  const map = new Map()
  for (const tx of transactions) {
    const key = `${String(tx.MonthNum).padStart(2, '0')}_${tx.Month}`
    const cost = parseFloat(tx.Cost)
    if (isNaN(cost)) continue
    map.set(key, (map.get(key) ?? 0) + cost)
  }

  return Array.from(map.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => ({
      label: key.split('_')[1],   // e.g. "January"
      value: parseFloat(value.toFixed(2)),
    }))
}

/**
 * Builds series data for a stacked horizontal bar chart of top items by spend.
 *
 * Each bar = one item. Each segment within a bar = one individual purchase.
 * Number of series = number of times the most-purchased item was bought.
 * Items with fewer purchases get 0 in the higher slots.
 *
 * @param {Array}  transactions  - raw transaction objects (must have Item, Cost, Category)
 * @param {number} topN          - how many items to include (default 10)
 * @returns {{ series: Array, itemNames: Array<string>, itemColors: Array<string> }}
 */
export function toTopItemsSeries(transactions, topN = 10) {
  if (!transactions || transactions.length === 0) {
    return { series: [], itemNames: [], itemColors: [] }
  }

  // 1. Group by Item — collect all purchase costs and the dominant category
  const groups = {}
  for (const tx of transactions) {
    const name = tx.Item ?? 'Unknown'
    if (!groups[name]) groups[name] = { costs: [], categories: {} }
    const cost = parseFloat(tx.Cost)
    if (!isNaN(cost)) groups[name].costs.push(cost)
    const cat = tx.Category ?? 'Miscellaneous'
    groups[name].categories[cat] = (groups[name].categories[cat] ?? 0) + 1
  }

  // 2. Sort by total spend descending, pick top N
  const itemNames = Object.entries(groups)
    .map(([name, g]) => ({ name, total: g.costs.reduce((s, c) => s + c, 0) }))
    .sort((a, b) => b.total - a.total)
    .slice(0, topN)
    .map(x => x.name)

  // 3. One color per item — derived from its most-common category
  const itemColors = itemNames.map(name => {
    const cats = groups[name].categories
    const dominant = Object.entries(cats).sort((a, b) => b[1] - a[1])[0][0]
    return getCategoryColor(dominant)
  })

  // 4. How many slots = max purchase count across top items
  const maxSlots = Math.max(...itemNames.map(name => groups[name].costs.length))

  // 5. Transpose into slot-major series
  const series = []
  for (let slot = 0; slot < maxSlots; slot++) {
    series.push({
      name: `Purchase ${slot + 1}`,
      data: itemNames.map(name => {
        const costs = groups[name].costs
        return costs[slot] !== undefined ? parseFloat(costs[slot].toFixed(2)) : 0
      }),
    })
  }

  return { series, itemNames, itemColors }
}

// ---------------------------------------------------------------------------
// Summary statistics
// ---------------------------------------------------------------------------

/**
 * Computes a full set of summary statistics from a transaction array.
 *
 * @param {Array} transactions
 * @returns {{
 *   totalSpent: number,
 *   itemsBought: number,
 *   averageSpend: number,
 *   p25: number,
 *   median: number,
 *   p75: number,
 *   stdDev: number,
 *   avgWeeklySpend: number,
 *   avgMonthlySpend: number,
 *   avgYearlySpend: number,
 *   spendingVolatility: number,
 * }}
 */
export function computeStats(transactions) {
  if (!transactions || transactions.length === 0) {
    return {
      totalSpent: 0, itemsBought: 0, averageSpend: 0,
      p25: 0, median: 0, p75: 0, stdDev: 0,
      avgWeeklySpend: 0, avgMonthlySpend: 0, avgYearlySpend: 0, spendingVolatility: 0,
    }
  }

  const costs = transactions.map(t => t.Cost).sort((a, b) => a - b)
  const count = costs.length
  const total = costs.reduce((s, c) => s + c, 0)
  const mean  = total / count

  const pct = (p) => {
    const idx = (p / 100) * (count - 1)
    const lo  = Math.floor(idx)
    const hi  = Math.ceil(idx)
    return costs[lo] + (costs[hi] - costs[lo]) * (idx - lo)
  }

  const variance = costs.reduce((s, c) => s + (c - mean) ** 2, 0) / count
  const stdDev   = Math.sqrt(variance)

  // Date range for time-averaged stats
  const dates     = transactions.map(t => new Date(t.Date)).sort((a, b) => a - b)
  const dayRange  = Math.max(1, (dates[dates.length - 1] - dates[0]) / 86_400_000)
  const weekRange = dayRange / 7

  // Average of actual monthly bucket totals (not total / months elapsed)
  const monthlyMap = {}
  transactions.forEach(t => {
    const key = t.Date.slice(0, 7)           // "YYYY-MM"
    monthlyMap[key] = (monthlyMap[key] || 0) + t.Cost
  })
  const monthlyTotals = Object.values(monthlyMap)
  const avgMonthlySpend = monthlyTotals.reduce((s, v) => s + v, 0) / monthlyTotals.length

  // Average of actual yearly bucket totals
  const yearlyMap = {}
  transactions.forEach(t => {
    const key = t.Date.slice(0, 4)           // "YYYY"
    yearlyMap[key] = (yearlyMap[key] || 0) + t.Cost
  })
  const yearlyTotals    = Object.values(yearlyMap)
  const avgYearlySpend  = yearlyTotals.reduce((s, v) => s + v, 0) / yearlyTotals.length

  // Spending volatility = coefficient of variation on monthly totals (%)
  const monthlyMean = avgMonthlySpend
  const monthlyStd  = Math.sqrt(
    monthlyTotals.reduce((s, v) => s + (v - monthlyMean) ** 2, 0) / monthlyTotals.length
  )
  const spendingVolatility = monthlyMean > 0 ? (monthlyStd / monthlyMean) * 100 : 0

  return {
    totalSpent:        total,
    itemsBought:       count,
    averageSpend:      mean,
    p25:               pct(25),
    median:            pct(50),
    p75:               pct(75),
    stdDev,
    avgWeeklySpend:    total / weekRange,
    avgMonthlySpend,
    avgYearlySpend,
    spendingVolatility,
  }
}
