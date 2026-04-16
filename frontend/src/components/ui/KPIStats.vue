<template>
  <section class="kpi-section">
    <!-- Row 1 -->
    <div class="kpi-row kpi-row--2">
      <StatCard label="Total Spent"   :value="stats.totalSpent"  format="currency" :privacyMode="privacyMode" />
      <StatCard label="Items Bought"  :value="stats.itemsBought" format="integer" :privacyMode="privacyMode" />
      <StatCard label="Total Data"    :value="stats.totalData"   format="text" />
    </div>

    <!-- Row 2 -->
    <div class="kpi-row kpi-row--5">
      <StatCard label="Average Spend"       :value="stats.averageSpend" format="currency" :privacyMode="privacyMode" />
      <StatCard label="Lower 25th Pctile"   :value="stats.p25"          format="currency" :privacyMode="privacyMode" />
      <StatCard label="Median Spend"        :value="stats.median"       format="currency" :privacyMode="privacyMode" />
      <StatCard label="Upper 75th Pctile"   :value="stats.p75"          format="currency" :privacyMode="privacyMode" />
      <StatCard label="Std Deviation"       :value="stats.stdDev"       format="currency" :privacyMode="privacyMode" />
    </div>

    <!-- Row 3 -->
    <div class="kpi-row kpi-row--4">
      <StatCard label="Avg Weekly Spend"   :value="stats.avgWeeklySpend"   format="currency" :privacyMode="privacyMode" />
      <StatCard label="Avg Monthly Spend"  :value="stats.avgMonthlySpend"  format="currency" :privacyMode="privacyMode" />
      <StatCard label="Avg Yearly Spend"   :value="stats.avgYearlySpend"   format="currency" :privacyMode="privacyMode" />
      <StatCard label="Spending Volatility" :value="stats.spendingVolatility" format="percent" :privacyMode="privacyMode" />
    </div>
  </section>
</template>

<script setup>
import StatCard from './StatCard.vue'

defineProps({
  stats: {
    type: Object,
    required: true,
  },
  privacyMode: {
    type: Boolean,
    default: false,
  },
})
</script>

<style scoped>
.kpi-section { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1.5rem; }

.kpi-row {
  display: grid;
  gap: 0.75rem;
}
.kpi-row--2 { grid-template-columns: repeat(3, 1fr); }
.kpi-row--5 { grid-template-columns: repeat(5, 1fr); }
.kpi-row--4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 860px) {
  .kpi-row--5 { grid-template-columns: repeat(3, 1fr); }
  .kpi-row--4 { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 540px) {
  .kpi-row--2, .kpi-row--5, .kpi-row--4 { grid-template-columns: 1fr 1fr; }
}
</style>
