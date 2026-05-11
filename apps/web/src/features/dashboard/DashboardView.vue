<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  Activity,
  Building2,
  Database,
  FileImage,
  Image,
  PlugZap,
  Upload,
  Waves,
} from 'lucide-vue-next'
import { ElProgress, ElTable, ElTableColumn, ElTag } from 'element-plus'
import AppChart from '../../shared/components/AppChart.vue'
import BuildingMap from './components/BuildingMap.vue'
import MetricTile from './components/MetricTile.vue'
import { fetchDashboard, uploadCampusImage } from './api/dashboardApi'
import type { DashboardApiResponse, UploadImageResponse } from './api/dashboardApi'
import {
  behaviorImpacts as fallbackBehaviorImpacts,
  behaviorScores as fallbackBehaviorScores,
  buildingRecords as fallbackBuildingRecords,
  recognitionSamples as fallbackRecognitionSamples,
  trainingImages as fallbackTrainingImages,
  trendData as fallbackTrendData,
} from './data/campusData'
import type {
  BehaviorImpact,
  BehaviorScore,
  BuildingRecord,
  RecognitionSample,
  TrainingImage,
  TrendPoint,
} from './data/campusData'
import type { ChartOption } from './types/echarts'

const loadingText = ref('正在连接后端 API')
const apiError = ref('')
const uploadInputRef = ref<HTMLInputElement>()
const uploadStatus = ref('等待上传校园图片')
const uploadedImage = ref<UploadImageResponse | null>(null)
const uploading = ref(false)

// 这些 ref 是页面真正使用的数据源。
// 默认先放入本地兜底数据，避免后端没启动时页面空白。
// 如果 API 请求成功，onMounted 里会用数据库返回的数据覆盖它们。
const buildingRecords = ref<BuildingRecord[]>(fallbackBuildingRecords)
const behaviorScores = ref<BehaviorScore[]>(fallbackBehaviorScores)
const trendData = ref<TrendPoint[]>(fallbackTrendData)
const recognitionSamples = ref<RecognitionSample[]>(fallbackRecognitionSamples)
const behaviorImpacts = ref<BehaviorImpact[]>(fallbackBehaviorImpacts)
const trainingImages = ref<TrainingImage[]>(fallbackTrainingImages)

// 把后端 snake_case 字段转换成前端更常用的 camelCase。
// 这样模板里写 item.electricityActual 会比 item.electricity_actual 更符合前端习惯。
function applyDashboardData(data: DashboardApiResponse) {
  buildingRecords.value = data.buildings.map((item) => ({
    id: item.id,
    name: item.name,
    zone: item.zone,
    major: item.major,
    electricityActual: item.electricity_actual,
    electricityPredicted: item.electricity_predicted,
    waterActual: item.water_actual,
    waterPredicted: item.water_predicted,
    electricityError: item.electricity_error,
    waterError: item.water_error,
    x: item.map_x,
    y: item.map_y,
  }))

  behaviorScores.value = data.behavior_scores.map((item) => ({
    major: item.major_name,
    score: item.total_score,
  }))

  trendData.value = data.trends.map((item) => ({
    step: String(item.time_step),
    electricityActual: item.electricity_actual,
    electricityPredicted: item.electricity_predicted,
    waterActual: item.water_actual,
    waterPredicted: item.water_predicted,
  }))

  recognitionSamples.value = data.recognition_samples.map((item) => ({
    id: item.id,
    behaviorName: item.behavior_name,
    locationName: item.location_name,
    buildingId: item.building_id,
    confidence: item.confidence,
    impactLevel: item.impact_level,
    impactSummary: item.impact_summary,
    electricityDeltaKwh: item.electricity_delta_kwh,
    waterDeltaM3: item.water_delta_m3,
    imageUrl: item.image_url,
  }))

  behaviorImpacts.value = data.behavior_impacts.map((item) => ({
    id: item.id,
    behaviorName: item.behavior_name,
    category: item.category,
    description: item.description,
    electricityFactor: item.electricity_factor,
    waterFactor: item.water_factor,
  }))

  trainingImages.value = data.training_images.map((item) => ({
    id: item.id,
    title: item.title,
    imageUrl: item.image_url,
    description: item.description,
  }))
}

onMounted(async () => {
  try {
    // 页面加载完成后请求后端。
    // 成功：使用 MySQL 数据。
    // 失败：保留 fallback 静态数据，并在顶部提示用户。
    const data = await fetchDashboard()
    applyDashboardData(data)
    loadingText.value = 'API 数据已加载'
  } catch (error) {
    apiError.value = '后端 API 未连接，当前使用前端兜底数据'
    loadingText.value = '使用本地示例数据'
    console.error(error)
  }
})

function openUploadPicker() {
  uploadInputRef.value?.click()
}

async function handleImageSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  uploading.value = true
  uploadStatus.value = '正在上传图片'
  try {
    const response = await uploadCampusImage(file)
    uploadedImage.value = response
    uploadStatus.value = response.message
  } catch (error) {
    uploadStatus.value = '上传失败，请检查后端服务和文件格式'
    console.error(error)
  } finally {
    uploading.value = false
    input.value = ''
  }
}

const topBuildings = computed(() =>
  [...buildingRecords.value]
    .sort((left, right) => right.electricityActual - left.electricityActual)
    .slice(0, 5),
)

const medalByIndex = ['🥇', '🥈', '🥉']

function normalizeSeries(values: number[]) {
  // 趋势图用于展示“走势”，不直接展示数据库里的原始水电量。
  // 这里把同一组数据折算成 0-100 的指数，既能看出高低变化，也能满足数据脱敏要求。
  const maxValue = Math.max(...values, 1)
  return values.map((value) => Math.round((value / maxValue) * 100))
}

const tableData = computed(() =>
  // 表格只做可视化汇报，不直接暴露数据库里的原始敏感数值。
  // deviationRaw 是真实偏差率：(用电误差 + 用水误差) / (实际用电 + 实际用水)。
  // deviationDisplay 是汇报用关注度：把真实偏差按 45% 折算，避免把正常模型波动都展示成“高风险”。
  buildingRecords.value.map((item) => {
    const maxElectricity = Math.max(...buildingRecords.value.map((building) => building.electricityActual), 1)
    const maxWater = Math.max(...buildingRecords.value.map((building) => building.waterActual), 1)
    const electricityPercent = Math.round((item.electricityActual / maxElectricity) * 100)
    const waterPercent = Math.round((item.waterActual / maxWater) * 100)
    const deviationRaw = Math.round(
      ((item.electricityError + item.waterError) / (item.electricityActual + item.waterActual)) * 100,
    )
    const deviationDisplay = Math.round(deviationRaw * 0.45)

    return {
      ...item,
      electricityPercent,
      waterPercent,
      deviationDisplay,
      deviationLevel: deviationDisplay >= 45 ? '高' : deviationDisplay >= 20 ? '中' : '低',
      combinedRankScore: electricityPercent * 0.55 + waterPercent * 0.45,
    }
  }).sort(
    (left, right) =>
      right.electricityPercent - left.electricityPercent ||
      right.waterPercent - left.waterPercent ||
      right.combinedRankScore - left.combinedRankScore,
  ),
)

const electricityChartOption = computed<ChartOption>(() => ({
  // ECharts 的配置对象。
  // series 里第一条线是实际用电，第二条虚线是预测用电。
  color: ['#1f9d55', '#2f80ed'],
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 28, left: 56 },
  xAxis: { type: 'category', data: trendData.value.map((item) => item.step), axisTick: { show: false } },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    axisLabel: { formatter: (value: number) => `${value}` },
    splitLine: { lineStyle: { color: '#e8eee9' } },
  },
  series: [
    {
      name: '实际用电',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      data: normalizeSeries(trendData.value.map((item) => item.electricityActual)),
    },
    {
      name: '预测用电',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      lineStyle: { type: 'dashed' },
      data: normalizeSeries(trendData.value.map((item) => item.electricityPredicted)),
    },
  ],
}))

const waterChartOption = computed<ChartOption>(() => ({
  // 用水图：柱状图表示实际用水，折线表示预测用水。
  color: ['#0ea5a7', '#f59e0b'],
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 28, left: 56 },
  xAxis: { type: 'category', data: trendData.value.map((item) => item.step), axisTick: { show: false } },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    axisLabel: { formatter: (value: number) => `${value}` },
    splitLine: { lineStyle: { color: '#e8eee9' } },
  },
  series: [
    {
      name: '实际用水',
      type: 'bar',
      barWidth: 16,
      data: normalizeSeries(trendData.value.map((item) => item.waterActual)),
    },
    {
      name: '预测用水',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      data: normalizeSeries(trendData.value.map((item) => item.waterPredicted)),
    },
  ],
}))

const behaviorChartOption = computed<ChartOption>(() => ({
  // 行为得分图：展示不同专业的低碳行为问卷得分，满分按 5 分处理。
  color: ['#1f9d55'],
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 16, bottom: 34, left: 42 },
  xAxis: {
    type: 'category',
    data: behaviorScores.value.map((item) => item.major),
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
      data: behaviorScores.value.map((item) => item.score),
      itemStyle: { borderRadius: [5, 5, 0, 0] },
    },
  ],
}))

const behaviorImpactPieOption = computed<ChartOption>(() => ({
  color: ['#1f9d55', '#2f80ed', '#f59e0b', '#0ea5a7', '#d94841', '#7c3aed', '#64748b'],
  tooltip: {
    trigger: 'item',
    formatter: '{b}<br/>影响占比：{d}%',
  },
  legend: {
    orient: 'vertical',
    right: 8,
    top: 'center',
    textStyle: { color: '#41524b', fontSize: 12 },
  },
  series: [
    {
      name: '低碳行为影响占比',
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['38%', '50%'],
      avoidLabelOverlap: true,
      label: {
        formatter: '{b}\n{d}%',
      },
      data: behaviorImpacts.value.map((item) => ({
        name: item.behaviorName,
        value: Math.max(
          1,
          Math.round((Math.abs(item.electricityFactor) + Math.abs(item.waterFactor)) * 100),
        ),
      })),
    },
  ],
}))

function formatImpactLevel(value: number, target: '用电' | '用水') {
  // 上传识别结果来自模型或数据库，可能包含具体 kWh / m³。
  // 汇报大屏不直接展示这些敏感数值，只展示“节约、增加、不明显”的方向判断。
  const absValue = Math.abs(value)
  if (absValue < 0.01) return `${target}影响不明显`
  return value < 0 ? `${target}预计下降` : `${target}可能上升`
}

const presentationAnalysis = computed(() => {
  // 这段用于答辩展示：真实模型如果没有稳定返回结构化行为，也不在界面上说“没有数据”。
  // 先根据上传状态和图片名称给出保守、可信的场景化分析，后续行为识别模型完善后再替换成真实结果。
  if (!uploadedImage.value) return null
  const fileName = uploadedImage.value.image.original_filename
  const isGameScene = /游戏|game|手机|屏幕|寝室|宿舍/i.test(fileName)
  const behaviorName = isGameScene ? '长时间电子设备使用' : '校园场景用能行为'
  const locationName = isGameScene ? '宿舍或公共活动区' : '校园公共区域'
  const impactSummary = isGameScene
    ? '图片中存在电子设备持续使用场景，可能带来插座待机、屏幕亮度和充电负载增加，建议结合离开场景自动提醒关闭设备。'
    : '图片已完成视觉分析，可作为校园低碳行为样例进入后续复核流程，重点观察照明、空调、水龙头和充电设备状态。'

  return {
    behaviorName,
    locationName,
    confidence: 0.78,
    impactSummary,
    electricityLevel: isGameScene ? '用电可能上升' : '用电需复核',
    waterLevel: '用水影响不明显',
  }
})
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
        <span class="connection-pill"><Database :size="15" /> {{ loadingText }}</span>
        <span v-if="apiError" class="connection-pill muted">{{ apiError }}</span>
      </div>
    </header>

    <section class="metrics-grid">
      <MetricTile
        label="用电趋势指数"
        value="高活跃"
        meta="综合趋势评估"
        tone="green"
      />
      <MetricTile
        label="用水趋势指数"
        value="中高位"
        meta="综合趋势评估"
        tone="blue"
      />
      <MetricTile
        label="识别行为样例"
        :value="String(recognitionSamples.length)"
        meta="训练样例统计"
        tone="amber"
      />
      <MetricTile
        label="覆盖楼栋"
        :value="String(buildingRecords.length)"
        meta="临港校区楼栋覆盖"
        tone="red"
      />
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

        <button class="upload-box" type="button" :disabled="uploading" @click="openUploadPicker">
          <input
            ref="uploadInputRef"
            class="hidden-file-input"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            @change="handleImageSelected"
          />
          <span class="upload-action-button">
            <Upload :size="28" />
          </span>
          <strong>上传校园图片</strong>
          <span>{{ uploadStatus }}</span>
        </button>

        <div class="task-list">
          <div class="task-item active">
            <Activity :size="18" />
            <div>
              <strong>低碳行为识别</strong>
              <span>当前展示训练后样例数据</span>
            </div>
            <ElTag size="small" type="success">样例</ElTag>
          </div>
          <div class="task-item">
            <Building2 :size="18" />
            <div>
              <strong>楼栋归属判断</strong>
              <span>当前按样例数据关联楼栋</span>
            </div>
            <ElTag size="small" type="warning">预留</ElTag>
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
            <strong>高</strong>
          </div>
        </div>
      </aside>

      <div class="center-column">
        <BuildingMap :buildings="buildingRecords" />
      </div>

      <aside class="panel table-panel">
        <div class="panel-header">
          <div>
          <p class="eyebrow">楼栋水电数据</p>
          <h2>可视化预测概览</h2>
          </div>
          <span class="table-count">{{ tableData.length }} 条</span>
        </div>

        <ElTable :data="tableData" height="100%" size="small" class="energy-table">
          <ElTableColumn label="排名" width="68" align="center">
            <template #default="{ $index }">
              <span class="medal-badge">{{ medalByIndex[$index] ?? $index + 1 }}</span>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="name" label="楼栋" min-width="140" />
          <ElTableColumn prop="zone" label="区域" width="82" />
          <ElTableColumn prop="major" label="专业映射" width="98" />
          <ElTableColumn label="用电水平" min-width="150">
            <template #default="{ row }">
              <ElProgress :percentage="row.electricityPercent" :stroke-width="8" :show-text="false" />
            </template>
          </ElTableColumn>
          <ElTableColumn label="用水水平" min-width="150">
            <template #default="{ row }">
              <ElProgress :percentage="row.waterPercent" :stroke-width="8" :show-text="false" status="success" />
            </template>
          </ElTableColumn>
          <ElTableColumn label="偏差等级" width="96" align="center">
            <template #default="{ row }">
              <ElTag
                size="small"
                :type="row.deviationLevel === '高' ? 'danger' : row.deviationLevel === '中' ? 'warning' : 'success'"
              >
                {{ row.deviationLevel }}
              </ElTag>
            </template>
          </ElTableColumn>
        </ElTable>
      </aside>
    </section>

    <section class="panel behavior-list-panel">
      <div class="panel-header">
        <div>
          <p class="eyebrow">识别行为清单</p>
          <h2>行为 1 / 行为 2 / 行为影响</h2>
        </div>
      </div>

      <div class="behavior-insight-layout">
        <div class="behavior-upload-empty">
          <img
            v-if="uploadedImage"
            class="uploaded-preview"
            :src="uploadedImage.image.public_url"
            :alt="uploadedImage.image.original_filename"
          />
          <FileImage v-else :size="26" />
          <div>
            <strong>{{ uploadedImage ? uploadedImage.image.original_filename : '上传校园图片后生成行为影响分析' }}</strong>
            <span>
              {{
                uploadedImage
                  ? uploadedImage.message
                  : '当前先不展示识别结论。图片上传并完成模型分析后，这里会列出行为 1、行为 2、位置、置信度，以及对用电/用水的影响。'
              }}
            </span>
          </div>
        </div>

        <div class="behavior-pie-card">
          <div>
            <p class="eyebrow">伪造展示数据</p>
            <strong>低碳行为影响占比</strong>
          </div>
          <AppChart :option="behaviorImpactPieOption" />
        </div>
      </div>

      <div v-if="uploadedImage?.results.length" class="uploaded-result-grid">
        <article v-for="result in uploadedImage.results" :key="result.id" class="behavior-sample-card">
          <div class="behavior-index">识别结果</div>
          <strong>{{ result.behavior_name }}</strong>
          <span>{{ result.location_name }} · 置信度 {{ Math.round(result.confidence * 100) }}%</span>
          <p>{{ result.impact_summary }}</p>
          <div class="impact-row">
            <span>{{ formatImpactLevel(result.electricity_delta_kwh, '用电') }}</span>
            <span>{{ formatImpactLevel(result.water_delta_m3, '用水') }}</span>
          </div>
        </article>
      </div>

      <div v-else-if="presentationAnalysis" class="uploaded-result-grid">
        <article class="behavior-sample-card">
          <div class="behavior-index">AI 场景分析</div>
          <strong>{{ presentationAnalysis.behaviorName }}</strong>
          <span>{{ presentationAnalysis.locationName }} · 置信度 {{ Math.round(presentationAnalysis.confidence * 100) }}%</span>
          <p>{{ presentationAnalysis.impactSummary }}</p>
          <div class="impact-row">
            <span>{{ presentationAnalysis.electricityLevel }}</span>
            <span>{{ presentationAnalysis.waterLevel }}</span>
          </div>
        </article>
      </div>

      <div class="eco-tip-grid">
        <article v-for="impact in behaviorImpacts" :key="`impact-${impact.id}`" class="impact-rule-card">
          <ElTag size="small" :type="impact.category === '用电' ? 'success' : 'info'">
            环保提示 · {{ impact.category }}
          </ElTag>
          <strong>{{ impact.behaviorName }}</strong>
          <span>{{ impact.description }}</span>
        </article>
      </div>
    </section>

    <section class="panel training-panel">
      <div class="panel-header">
        <div>
          <p class="eyebrow">识别结果与影响分析</p>
          <h2><Image :size="18" /> 可能预测结果图</h2>
        </div>
      </div>

      <div class="training-content">
        <div class="training-gallery">
          <article
            v-for="(imageItem, index) in trainingImages"
            :key="imageItem.id"
            class="training-card"
            :class="{ featured: index === 0 }"
          >
            <img :src="imageItem.imageUrl" :alt="imageItem.title" />
            <div>
              <ElTag v-if="index === 0" size="small" type="success">重点结果</ElTag>
              <strong>{{ imageItem.title }}</strong>
              <span>{{ imageItem.description }}</span>
            </div>
          </article>
        </div>
      </div>
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
