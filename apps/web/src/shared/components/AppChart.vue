<script setup lang="ts">
import { onBeforeUnmount, onMounted, shallowRef, watch } from 'vue'
import * as echarts from 'echarts'
import type { ChartOption } from '../../features/dashboard/types/echarts'

const props = defineProps<{
  option: ChartOption
}>()

const chartRef = shallowRef<HTMLDivElement>()
let chart: echarts.ECharts | null = null

const renderChart = () => {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  chart.setOption(props.option, true)
}

const resizeChart = () => {
  chart?.resize()
}

onMounted(() => {
  renderChart()
  window.addEventListener('resize', resizeChart)
})

watch(
  () => props.option,
  () => renderChart(),
  { deep: true },
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
  chart = null
})
</script>

<template>
  <div ref="chartRef" class="app-chart" />
</template>

<style scoped>
.app-chart {
  width: 100%;
  height: 100%;
  min-height: 240px;
}
</style>
