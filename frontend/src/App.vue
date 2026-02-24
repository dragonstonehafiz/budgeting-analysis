<template>
  <div style="width: 80%; margin: 2rem auto; padding: 0 1rem;">
    <h1>Chart Demos</h1>

    <!-- Bucket selector shared across line charts -->
    <div style="margin-bottom: 1rem;">
      <label><b>Bucket size:</b></label>
      <button
        v-for="opt in bucketOptions"
        :key="opt.value"
        @click="bucketDays = opt.value"
        :style="{ marginLeft: '0.5rem', fontWeight: bucketDays === opt.value ? 'bold' : 'normal' }"
      >
        {{ opt.label }}
      </button>
    </div>

    <h2>Spending Trend</h2>
    <LineChart
      :series="spendingSeries"
      :averageLine="spendingAverage"
      title="Monthly Spending"
    />

    <h2>Rolling Average</h2>
    <LineChart
      :series="rollingSeries"
      title="3-Period Rolling Average"
      caption="Blue line = rolling average. Shaded band = typical variability around the average."
    />

    <h2>Cumulative Spending</h2>
    <LineChart
      :series="cumulativeSeries"
      title="Cumulative Spend"
    />

    <hr style="margin: 2rem 0;" />

    <h2>Top Items</h2>
    <HorizontalBarChart
      :series="topItems.series"
      :itemNames="topItems.itemNames"
      :itemColors="topItems.itemColors"
      title="Top 10 Items by Spend"
      :showTotals="true"
    />

    <hr style="margin: 2rem 0;" />

    <h2>Donut Charts</h2>
    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
      <div style="flex: 1; min-width: 300px;">
        <DonutChart
          :series="categorySeries"
          title="Spending by Category"
          :topN="10"
        />
      </div>
      <div style="flex: 1; min-width: 300px;">
        <DonutChart
          :series="monthlySeries"
          title="Spending by Month"
          :topN="0"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import LineChart from './components/charts/LineChart.vue'
import DonutChart from './components/charts/DonutChart.vue'
import HorizontalBarChart from './components/charts/HorizontalBarChart.vue'
import {
  toSpendingSeries,
  toRollingSeries,
  toCumulativeSeries,
  computeAverage,
  toCategoryDonutSeries,
  toMonthlyDonutSeries,
  toTopItemsSeries,
} from './composables/useChartData.js'

// --- Generate 100 mock grocery purchases spread across 2025 ---
const MONTHS = [
  { name: 'January', num: 1 }, { name: 'February', num: 2 }, { name: 'March', num: 3 },
  { name: 'April', num: 4 }, { name: 'May', num: 5 }, { name: 'June', num: 6 },
  { name: 'July', num: 7 }, { name: 'August', num: 8 }, { name: 'September', num: 9 },
  { name: 'October', num: 10 }, { name: 'November', num: 11 }, { name: 'December', num: 12 },
]
const GROCERY_ENTRIES = Array.from({ length: 100 }, (_, i) => {
  const month = MONTHS[i % 12]
  const day   = ((i * 3) % 27) + 1
  const cost  = parseFloat((20 + (i * 7.3) % 60).toFixed(2))
  return {
    Date: `2025-${String(month.num).padStart(2, '0')}-${String(day).padStart(2, '0')}`,
    Cost: cost,
    Category: 'Food & Beverages',
    Item: 'Groceries',
    Month: month.name,
    MonthNum: month.num,
  }
})

// --- Mock transaction data ---
const MOCK_TRANSACTIONS = [
  ...GROCERY_ENTRIES,
  { Date: '2025-01-03', Cost: 12.50,  Category: 'Food & Beverages',         Item: 'Lunch',          Month: 'January',   MonthNum: 1  },
  { Date: '2025-01-10', Cost: 85.00,  Category: 'Gaming',                   Item: 'Steam',          Month: 'January',   MonthNum: 1  },
  { Date: '2025-01-18', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'January',   MonthNum: 1  },
  { Date: '2025-02-02', Cost: 45.00,  Category: 'Food & Beverages',         Item: 'Groceries',      Month: 'February',  MonthNum: 2  },
  { Date: '2025-02-14', Cost: 120.00, Category: 'Electronics & Accessories',Item: 'USB Hub',        Month: 'February',  MonthNum: 2  },
  { Date: '2025-02-20', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'February',  MonthNum: 2  },
  { Date: '2025-03-05', Cost: 60.00,  Category: 'Movies & Media',           Item: 'Blu-ray Box Set',Month: 'March',     MonthNum: 3  },
  { Date: '2025-03-15', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'March',     MonthNum: 3  },
  { Date: '2025-03-28', Cost: 250.00, Category: 'Gaming',                   Item: 'Steam',          Month: 'March',     MonthNum: 3  },
  { Date: '2025-04-01', Cost: 35.00,  Category: 'Food & Beverages',         Item: 'Groceries',      Month: 'April',     MonthNum: 4  },
  { Date: '2025-04-10', Cost: 70.00,  Category: 'Clothing & Apparel',       Item: 'Jacket',         Month: 'April',     MonthNum: 4  },
  { Date: '2025-04-15', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'April',     MonthNum: 4  },
  { Date: '2025-04-22', Cost: 22.00,  Category: 'Food & Beverages',         Item: 'Lunch',          Month: 'April',     MonthNum: 4  },
  { Date: '2025-05-03', Cost: 90.00,  Category: 'Health & Personal Care',   Item: 'Gym Membership', Month: 'May',       MonthNum: 5  },
  { Date: '2025-05-15', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'May',       MonthNum: 5  },
  { Date: '2025-05-19', Cost: 45.00,  Category: 'Books & Literature',       Item: 'Novel',          Month: 'May',       MonthNum: 5  },
  { Date: '2025-06-07', Cost: 200.00, Category: 'Electronics & Accessories',Item: 'Keyboard',       Month: 'June',      MonthNum: 6  },
  { Date: '2025-06-15', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'June',      MonthNum: 6  },
  { Date: '2025-06-25', Cost: 55.00,  Category: 'Food & Beverages',         Item: 'Groceries',      Month: 'June',      MonthNum: 6  },
  { Date: '2025-07-04', Cost: 30.00,  Category: 'Movies & Media',           Item: 'Blu-ray Box Set',Month: 'July',      MonthNum: 7  },
  { Date: '2025-07-14', Cost: 110.00, Category: 'Gaming',                   Item: 'Steam',          Month: 'July',      MonthNum: 7  },
  { Date: '2025-07-15', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'July',      MonthNum: 7  },
  { Date: '2025-08-01', Cost: 75.00,  Category: 'Collectibles',             Item: 'Figurine',       Month: 'August',    MonthNum: 8  },
  { Date: '2025-08-15', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'August',    MonthNum: 8  },
  { Date: '2025-08-20', Cost: 40.00,  Category: 'Food & Beverages',         Item: 'Groceries',      Month: 'August',    MonthNum: 8  },
  { Date: '2025-09-10', Cost: 95.00,  Category: 'Music & Audio',            Item: 'Headphones',     Month: 'September', MonthNum: 9  },
  { Date: '2025-09-15', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'September', MonthNum: 9  },
  { Date: '2025-10-05', Cost: 25.00,  Category: 'Food & Beverages',         Item: 'Lunch',          Month: 'October',   MonthNum: 10 },
  { Date: '2025-10-15', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'October',   MonthNum: 10 },
  { Date: '2025-10-18', Cost: 180.00, Category: 'Gaming',                   Item: 'Steam',          Month: 'October',   MonthNum: 10 },
  { Date: '2025-11-02', Cost: 60.00,  Category: 'Miscellaneous',            Item: 'Misc Item',      Month: 'November',  MonthNum: 11 },
  { Date: '2025-11-15', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'November',  MonthNum: 11 },
  { Date: '2025-11-28', Cost: 320.00, Category: 'Electronics & Accessories',Item: 'Monitor',        Month: 'November',  MonthNum: 11 },
  { Date: '2025-12-10', Cost: 145.00, Category: 'Gaming',                   Item: 'Steam',          Month: 'December',  MonthNum: 12 },
  { Date: '2025-12-15', Cost: 15.00,  Category: 'Digital Subscriptions',    Item: 'Netflix',        Month: 'December',  MonthNum: 12 },
  { Date: '2025-12-24', Cost: 85.00,  Category: 'Food & Beverages',         Item: 'Groceries',      Month: 'December',  MonthNum: 12 },
]

const bucketOptions = [
  { label: '1-day',  value: 1  },
  { label: '7-day',  value: 7  },
  { label: '28-day', value: 28 },
]

const bucketDays = ref(28)

// Line chart series
const spendingSeries   = computed(() => toSpendingSeries(MOCK_TRANSACTIONS, bucketDays.value))
const spendingAverage  = computed(() => computeAverage(MOCK_TRANSACTIONS, bucketDays.value))
const rollingSeries    = computed(() => toRollingSeries(MOCK_TRANSACTIONS, 3, bucketDays.value))
const cumulativeSeries = computed(() => toCumulativeSeries(MOCK_TRANSACTIONS, bucketDays.value))

// Donut chart series
const categorySeries = computed(() => toCategoryDonutSeries(MOCK_TRANSACTIONS))
const monthlySeries  = computed(() => toMonthlyDonutSeries(MOCK_TRANSACTIONS))

// Horizontal bar chart
const topItems = computed(() => toTopItemsSeries(MOCK_TRANSACTIONS, 10))
</script>
