<script setup lang="ts">
import { onBeforeUnmount, onMounted, shallowRef, watch } from 'vue'
import * as echarts from 'echarts'
import type { ChartOption } from '../../features/dashboard/types/echarts'

// 这是一个通用图表组件：
// 父组件把 ECharts 配置 option 传进来，这里负责创建、更新、销毁图表实例。
const props = defineProps<{
  option: ChartOption
}>()

// chartRef 指向 template 里的 div，ECharts 会在这个 div 里绘图。
const chartRef = shallowRef<HTMLDivElement>()
let chart: echarts.ECharts | null = null

// 初始化图表，或者在 option 变化后重新设置配置
const renderChart = () => {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  chart.setOption(props.option, true)
}

// 浏览器窗口大小变化时，让图表跟着自适应
const resizeChart = () => {
  chart?.resize()
}

// 组件挂载完成后再初始化图表，因为这时 div 已经渲染到页面上了
onMounted(() => {
  renderChart()
  window.addEventListener('resize', resizeChart)
})

// 当父组件传入的新 option 发生变化时，重新画图
watch(
  () => props.option,
  () => renderChart(),
  { deep: true },
)

// 组件销毁前清理监听和图表实例，避免内存泄漏
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
  chart = null
})
</script>

<template>
  <!-- 这里本身没有写图表 HTML，图表内容由 echarts.init(...) 动态画进这个 div -->
  <div ref="chartRef" class="app-chart" />
</template>

<style scoped>
.app-chart {
  width: 100%;
  height: 100%;
  min-height: 240px;
}
</style>
