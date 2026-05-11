<script setup lang="ts">
import type { BuildingRecord } from '../data/campusData'
const props = defineProps<{
  buildings: BuildingRecord[]
}>()

const maxElectricity = () =>
  Math.max(...props.buildings.map((building) => building.electricityActual), 1)

const getBubbleSize = (value: number) => {
  const ratio = value / maxElectricity()
  const size = 30 + Math.sqrt(ratio) * 46
  return `${Math.round(size)}px`
}

const getBubbleClass = (value: number) => {
  const ratio = value / maxElectricity()
  if (ratio >= 0.72) return 'bubble-high'
  if (ratio >= 0.32) return 'bubble-medium'
  return 'bubble-low'
}

const getEnergyLevel = (value: number) => {
  const ratio = value / maxElectricity()
  if (ratio >= 0.72) return '高强度'
  if (ratio >= 0.32) return '中强度'
  return '低强度'
}

const getWaterLevel = (value: number) => {
  const maxWater = Math.max(...props.buildings.map((building) => building.waterActual), 1)
  const ratio = value / maxWater
  if (ratio >= 0.72) return '高水耗'
  if (ratio >= 0.32) return '中水耗'
  return '低水耗'
}

const getPredictionStatus = (building: BuildingRecord) => {
  const totalActual = building.electricityActual + building.waterActual
  const totalError = building.electricityError + building.waterError
  const displayDeviation = Math.round((totalError / totalActual) * 100 * 0.45)
  if (displayDeviation >= 45) return '重点关注'
  if (displayDeviation >= 20) return '轻度波动'
  return '趋势稳定'
}
</script>

<template>
  <section class="panel campus-map-panel">
    <div class="panel-header">
      <div>
        <p class="eyebrow">临港校区楼栋关系</p>
        <h2>能耗与行为关联图</h2>
      </div>
      <span class="map-status">15 栋建筑</span>
    </div>

    <div class="campus-map" aria-label="上海电机学院临港校区楼栋能耗气泡图">
      <div class="route route-a" />
      <div class="route route-b" />
      <div class="route route-c" />
      <button
        v-for="building in buildings"
        :key="building.id"
        class="building-node"
        :class="getBubbleClass(building.electricityActual)"
        :style="{
          left: `${building.x}%`,
          top: `${building.y}%`,
          width: getBubbleSize(building.electricityActual),
          height: getBubbleSize(building.electricityActual),
        }"
        type="button"
      >
        <span class="node-name">{{ building.name }}</span>
        <span class="node-tooltip">
          <strong>{{ building.name }}</strong>
          <i>区域：{{ building.zone }}</i>
          <i>专业映射：{{ building.major }}</i>
          <i>用电水平：{{ getEnergyLevel(building.electricityActual) }}</i>
          <i>用水水平：{{ getWaterLevel(building.waterActual) }}</i>
          <i>预测状态：{{ getPredictionStatus(building) }}</i>
        </span>
      </button>
    </div>

    <div class="legend-row">
      <span><i class="legend-dot science" />低强度</span>
      <span><i class="legend-dot medical" />中强度</span>
      <span><i class="legend-dot life" />高强度</span>
      <span class="legend-note">数值默认隐藏，悬停气泡查看详细指标</span>
    </div>
  </section>
</template>

<style scoped>
.campus-map-panel {
  display: flex;
  flex-direction: column;
  min-height: 520px;
  overflow: visible;
}

.map-status {
  border: 1px solid var(--border-subtle);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: 12px;
  padding: 5px 10px;
  white-space: nowrap;
}

.campus-map {
  position: relative;
  flex: 1;
  min-height: 390px;
  margin-top: 18px;
  overflow: visible;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  background:
    linear-gradient(90deg, rgba(38, 80, 115, 0.08) 1px, transparent 1px),
    linear-gradient(rgba(38, 80, 115, 0.08) 1px, transparent 1px),
    #f7fbf8;
  background-size: 42px 42px;
}

.campus-map::before {
  content: '上海电机学院 临港校区';
  position: absolute;
  left: 18px;
  bottom: 14px;
  color: rgba(29, 46, 40, 0.42);
  font-size: 13px;
}

.route {
  position: absolute;
  background: rgba(48, 83, 74, 0.16);
  border-radius: 999px;
}

.route-a {
  left: 8%;
  top: 48%;
  width: 84%;
  height: 8px;
}

.route-b {
  left: 48%;
  top: 8%;
  width: 8px;
  height: 82%;
}

.route-c {
  left: 18%;
  top: 66%;
  width: 58%;
  height: 7px;
  transform: rotate(-22deg);
  transform-origin: left center;
}

.building-node {
  position: absolute;
  display: grid;
  place-items: center;
  gap: 1px;
  transform: translate(-50%, -50%);
  border: 2px solid rgba(20, 83, 45, 0.16);
  border-radius: 50%;
  color: var(--text-strong);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.75),
    0 10px 24px rgba(21, 70, 52, 0.13);
  cursor: pointer;
  transition:
    transform 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.building-node:hover {
  z-index: 20;
  transform: translate(-50%, -50%) scale(1.08);
  border-color: var(--green);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.85),
    0 16px 34px rgba(21, 70, 52, 0.22);
}

.bubble-low {
  border-color: rgba(59, 130, 246, 0.28);
  background:
    radial-gradient(circle at 36% 28%, rgba(255, 255, 255, 0.9), transparent 28%),
    linear-gradient(135deg, rgba(96, 165, 250, 0.2), rgba(191, 219, 254, 0.52));
}

.bubble-medium {
  border-color: rgba(217, 119, 6, 0.3);
  background:
    radial-gradient(circle at 36% 28%, rgba(255, 255, 255, 0.88), transparent 28%),
    linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(254, 243, 199, 0.62));
}

.bubble-high {
  border-color: rgba(22, 163, 74, 0.34);
  background:
    radial-gradient(circle at 36% 28%, rgba(255, 255, 255, 0.88), transparent 28%),
    linear-gradient(135deg, rgba(34, 197, 94, 0.24), rgba(167, 243, 208, 0.64));
}

.node-name {
  max-width: 82px;
  overflow: hidden;
  color: var(--text-strong);
  font-size: 12px;
  font-weight: 700;
  line-height: 1.15;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-tooltip {
  position: absolute;
  left: 50%;
  bottom: calc(100% + 10px);
  z-index: 5;
  display: none;
  min-width: 190px;
  padding: 10px 12px;
  transform: translateX(-50%);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 12px 28px rgba(22, 59, 43, 0.16);
  pointer-events: none;
  text-align: left;
}

.building-node:hover .node-tooltip {
  display: grid;
  gap: 4px;
}

.node-tooltip strong {
  color: var(--text-strong);
  font-size: 13px;
}

.node-tooltip i {
  color: var(--text-muted);
  font-size: 12px;
  font-style: normal;
  white-space: nowrap;
}

.legend-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 14px;
  color: var(--text-muted);
  font-size: 12px;
}

.legend-row span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.science {
  background: var(--blue);
}

.medical {
  background: var(--amber);
}

.life {
  background: var(--green);
}

.legend-note {
  margin-left: auto;
}
</style>
