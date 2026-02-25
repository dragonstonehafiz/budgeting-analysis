/**
 * useChartData.js
 *
 * Data transformation composable for time-series charts and donut charts.
 * All functions accept raw transactions and return chart-ready data arrays.
 *
 * Raw transaction shape expected:
 *   { Date: string|Date, Cost: number, Category: string, Item: string, Notes?: string }
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

/**
 * Returns one bucketed line series per category, each carrying its preset color.
 * Series are sorted by total spend descending.
 *
 * @param {Array}  transactions
 * @param {number} bucketDays
 * @returns {Array<{name: string, color: string, data: {x: number, y: number}[]}>}
 */
export function toCategorySpendingSeries(transactions, bucketDays = 28) {
  if (!transactions || transactions.length === 0) return []

  // Group raw transactions by category first
  const catMap = new Map()
  for (const tx of transactions) {
    const cat = tx.Category || 'Miscellaneous'
    if (!catMap.has(cat)) catMap.set(cat, [])
    catMap.get(cat).push(tx)
  }

  const rawSeries = []
  for (const [cat, txs] of catMap.entries()) {
    const data = bucketTransactions(txs, bucketDays)
    if (data.length === 0) continue
    rawSeries.push({ name: cat, color: getCategoryColor(cat), data })
  }

  // Build a union of all x timestamps so we can insert null where a category
  // has no data — Chart.js then breaks the line instead of drawing across the gap
  const allTimestamps = [
    ...new Set(rawSeries.flatMap(s => s.data.map(p => p.x))),
  ].sort((a, b) => a - b)

  const series = rawSeries.map(s => {
    const pointMap = new Map(s.data.map(p => [p.x, p.y]))
    const data = allTimestamps.map(x => ({ x, y: pointMap.has(x) ? pointMap.get(x) : 0 }))
    return { ...s, data }
  })

  // Sort by total spend descending so the biggest category is listed first
  return series.sort((a, b) => {
    const sumA = a.data.reduce((s, p) => s + (p.y ?? 0), 0)
    const sumB = b.data.reduce((s, p) => s + (p.y ?? 0), 0)
    return sumB - sumA
  })
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
 * Month name and sort order are derived from the Date field — Month/MonthNum
 * fields are not required.
 * Months are sorted chronologically.
 *
 * @param {Array} transactions
 * @returns {Array<{label: string, value: number}>}
 */
export function toMonthlyDonutSeries(transactions) {
  if (!transactions || transactions.length === 0) return []

  // Derive month number and name from the Date string — no Month/MonthNum fields needed
  const map = new Map()
  for (const tx of transactions) {
    const date = new Date(tx.Date)
    if (isNaN(date)) continue
    const cost = parseFloat(tx.Cost)
    if (isNaN(cost)) continue
    // Zero-padded month number as sort key, e.g. "01", "12"
    const monthNum  = String(date.getMonth() + 1).padStart(2, '0')
    const monthName = date.toLocaleString('en-AU', { month: 'long' })  // e.g. "January"
    const key = `${monthNum}_${monthName}`
    map.set(key, (map.get(key) ?? 0) + cost)
  }

  return Array.from(map.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => ({
      label: key.split('_')[1],
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

  // 1. Group by Item — collect purchases and the dominant category
  const groups = {}
  for (const tx of transactions) {
    const name = tx.Item ?? 'Unknown'
    if (!groups[name]) groups[name] = { purchases: [], categories: {} }
    const cost = parseFloat(tx.Cost)
    if (!isNaN(cost)) {
      groups[name].purchases.push({
        cost,
        store: String(tx.Store || '').trim(),
        tags: String(tx.Tags || '').trim(),
        notes: String(tx.Notes || '').trim(),
      })
    }
    const cat = tx.Category ?? 'Miscellaneous'
    groups[name].categories[cat] = (groups[name].categories[cat] ?? 0) + 1
  }

  // 2. Sort by total spend descending, pick top N
  const itemNames = Object.entries(groups)
    .map(([name, g]) => ({ name, total: g.purchases.reduce((s, p) => s + p.cost, 0) }))
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
  const maxSlots = Math.max(...itemNames.map(name => groups[name].purchases.length))

  // 5. Transpose into slot-major series
  const series = []
  for (let slot = 0; slot < maxSlots; slot++) {
    series.push({
      name: `Purchase ${slot + 1}`,
      data: itemNames.map(name => {
        const purchases = groups[name].purchases
        return purchases[slot] ? parseFloat(purchases[slot].cost.toFixed(2)) : 0
      }),
      details: itemNames.map(name => {
        const purchases = groups[name].purchases
        const purchase = purchases[slot]
        return purchase
          ? { store: purchase.store, tags: purchase.tags, notes: purchase.notes }
          : null
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
