<script setup lang="ts">
import { computed } from 'vue'
import {
  Activity,
  Building2,
  Database,
  FileImage,
  PlugZap,
  Upload,
  Waves,
} from 'lucide-vue-next'
import { ElProgress, ElTable, ElTableColumn, ElTag } from 'element-plus'
import AppChart from '../../shared/components/AppChart.vue'
import BuildingMap from './components/BuildingMap.vue'
import MetricTile from './components/MetricTile.vue'
import { behaviorScores, buildingRecords, trendData } from './data/campusData'
import { formatCompact, formatNumber } from './utils/format'
import type { ChartOption } from './types/echarts'

const totals = computed(() => {
  const electricityActual = buildingRecords.reduce((sum, item) => sum + item.electricityActual, 0)
  const electricityPredicted = buildingRecords.reduce(
    (sum, item) => sum + item.electricityPredicted,
    0,
  )
  const waterActual = buildingRecords.reduce((sum, item) => sum + item.waterActual, 0)
  const waterPredicted = buildingRecords.reduce((sum, item) => sum + item.waterPredicted, 0)
  const avgBehavior =
    behaviorScores.reduce((sum, item) => sum + item.score, 0) / behaviorScores.length

  return {
    electricityActual,
    electricityPredicted,
    waterActual,
    waterPredicted,
    avgBehavior,
  }
})

const topBuildings = computed(() =>
  [...buildingRecords]
    .sort((left, right) => right.electricityActual - left.electricityActual)
    .slice(0, 5),
)

const tableData = computed(() =>
  buildingRecords.map((item) => ({
    ...item,
    electricityGapRate: `${Math.round((item.electricityError / item.electricityActual) * 100)}%`,
    waterGapRate: `${Math.round((item.waterError / item.waterActual) * 100)}%`,
  })),
)

const electricityChartOption = computed<ChartOption>(() => ({
  color: ['#1f9d55', '#2f80ed'],
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 28, left: 56 },
  xAxis: {
    type: 'category',
    data: trendData.map((item) => item.step),
    axisTick: { show: false },
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: (value: number) => formatCompact(value),
    },
    splitLine: { lineStyle: { color: '#e8eee9' } },
  },
  series: [
    {
      name: '实际用电',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      data: trendData.map((item) => item.electricityActual),
    },
    {
      name: '预测用电',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      lineStyle: { type: 'dashed' },
      data: trendData.map((item) => item.electricityPredicted),
    },
  ],
}))

const waterChartOption = computed<ChartOption>(() => ({
  color: ['#0ea5a7', '#f59e0b'],
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 28, left: 56 },
  xAxis: {
    type: 'category',
    data: trendData.map((item) => item.step),
    axisTick: { show: false },
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: (value: number) => formatCompact(value),
    },
    splitLine: { lineStyle: { color: '#e8eee9' } },
  },
  series: [
    {
      name: '实际用水',
      type: 'bar',
      barWidth: 16,
      data: trendData.map((item) => item.waterActual),
    },
    {
      name: '预测用水',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      data: trendData.map((item) => item.waterPredicted),
    },
  ],
}))

const behaviorChartOption = computed<ChartOption>(() => ({
  color: ['#1f9d55'],
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 16, bottom: 34, left: 42 },
  xAxis: {
    type: 'category',
    data: behaviorScores.map((item) => item.major),
    axisTick: { show: false },
    axisLabel: { interval: 0 },
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 5,
    splitLine: { lineStyle: { color: '#e8eee9' } },
  },
  series: [
    {
      name: '低碳行为得分',
      type: 'bar',
      barWidth: 28,
      data: behaviorScores.map((item) => item.score),
      itemStyle: {
        borderRadius: [5, 5, 0, 0],
      },
    },
  ],
}))
</script>

<template>
  <main class="dashboard-shell">
    <header class="topbar">
      <div class="brand-block">
        <div class="brand-mark">碳眸</div>
        <div>
          <p class="eyebrow">上海电机学院临港校区</p>
          <h1>校园低碳行为与水电预测驾驶舱</h1>
        </div>
      </div>
      <div class="topbar-actions">
        <span class="connection-pill"><Database :size="15" /> MySQL 本地连接已预检</span>
        <span class="connection-pill muted">识别模型待接入</span>
      </div>
    </header>

    <section class="metrics-grid">
      <MetricTile
        label="实际用电总量"
        :value="`${formatCompact(totals.electricityActual)} kWh`"
        :meta="`预测 ${formatCompact(totals.electricityPredicted)} kWh`"
        tone="green"
      />
      <MetricTile
        label="实际用水总量"
        :value="`${formatCompact(totals.waterActual)} m³`"
        :meta="`预测 ${formatCompact(totals.waterPredicted)} m³`"
        tone="blue"
      />
      <MetricTile
        label="低碳行为均分"
        :value="totals.avgBehavior.toFixed(2)"
        meta="来自 6 类专业问卷聚合"
        tone="amber"
      />
      <MetricTile label="覆盖楼栋" value="15" meta="按现有预测结果统计" tone="red" />
    </section>

    <section class="workspace-grid">
      <aside class="panel recognition-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">图像入口</p>
            <h2>行为识别任务</h2>
          </div>
          <FileImage :size="22" />
        </div>

        <div class="upload-box">
          <Upload :size="28" />
          <strong>上传校园图片</strong>
          <span>当前先展示页面入口，行为和位置识别接口后续接入。</span>
        </div>

        <div class="task-list">
          <div class="task-item active">
            <Activity :size="18" />
            <div>
              <strong>低碳行为识别</strong>
              <span>等待模型服务</span>
            </div>
            <ElTag size="small" type="info">预留</ElTag>
          </div>
          <div class="task-item">
            <Building2 :size="18" />
            <div>
              <strong>楼栋归属判断</strong>
              <span>先由数据表选择楼栋</span>
            </div>
            <ElTag size="small" type="warning">暂缓</ElTag>
          </div>
        </div>

        <div class="ranking-block">
          <div class="section-title">高用电楼栋</div>
          <div v-for="building in topBuildings" :key="building.id" class="rank-row">
            <span>{{ building.name }}</span>
            <ElProgress
              :percentage="Math.round((building.electricityActual / topBuildings[0].electricityActual) * 100)"
              :show-text="false"
              :stroke-width="7"
            />
            <strong>{{ formatCompact(building.electricityActual) }}</strong>
          </div>
        </div>
      </aside>

      <BuildingMap :buildings="buildingRecords" />

      <aside class="panel table-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">楼栋水电数据</p>
            <h2>预测结果表</h2>
          </div>
          <span class="table-count">{{ tableData.length }} 条</span>
        </div>

        <ElTable :data="tableData" height="440" size="small" class="energy-table">
          <ElTableColumn prop="name" label="楼栋" min-width="128" fixed />
          <ElTableColumn prop="zone" label="区域" width="82" />
          <ElTableColumn prop="major" label="专业映射" width="98" />
          <ElTableColumn label="用电" width="112" align="right">
            <template #default="{ row }">{{ formatNumber(row.electricityActual) }}</template>
          </ElTableColumn>
          <ElTableColumn label="预测用电" width="112" align="right">
            <template #default="{ row }">{{ formatNumber(row.electricityPredicted) }}</template>
          </ElTableColumn>
          <ElTableColumn prop="electricityGapRate" label="电误差" width="84" align="right" />
          <ElTableColumn label="用水" width="112" align="right">
            <template #default="{ row }">{{ formatNumber(row.waterActual) }}</template>
          </ElTableColumn>
          <ElTableColumn label="预测用水" width="112" align="right">
            <template #default="{ row }">{{ formatNumber(row.waterPredicted) }}</template>
          </ElTableColumn>
        </ElTable>
      </aside>
    </section>

    <section class="charts-grid">
      <article class="panel chart-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">用电趋势</p>
            <h2><PlugZap :size="18" /> 实际/预测对比</h2>
          </div>
        </div>
        <AppChart :option="electricityChartOption" />
      </article>

      <article class="panel chart-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">用水趋势</p>
            <h2><Waves :size="18" /> 实际/预测对比</h2>
          </div>
        </div>
        <AppChart :option="waterChartOption" />
      </article>

      <article class="panel chart-panel behavior-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">问卷行为</p>
            <h2>专业低碳行为得分</h2>
          </div>
        </div>
        <AppChart :option="behaviorChartOption" />
      </article>
    </section>
  </main>
</template>
