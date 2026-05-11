<script setup lang="ts">
import type { BuildingRecord } from '../data/campusData'
import { formatNumber } from '../utils/format'

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
        <span class="node-level">强度气泡</span>
        <span class="node-tooltip">
          <strong>{{ building.name }}</strong>
          <i>区域：{{ building.zone }}</i>
          <i>专业映射：{{ building.major }}</i>
          <i>用电：{{ formatNumber(building.electricityActual) }} kWh</i>
          <i>预测用电：{{ formatNumber(building.electricityPredicted) }} kWh</i>
          <i>用水：{{ formatNumber(building.waterActual) }} m³</i>
          <i>预测用水：{{ formatNumber(building.waterPredicted) }} m³</i>
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
  min-height: 520px;
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
  min-height: 390px;
  margin-top: 18px;
  overflow: hidden;
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
  border: 2px solid rgba(20, 83, 45, 0.18);
  border-radius: 50%;
  color: var(--text-strong);
  box-shadow: 0 10px 24px rgba(21, 70, 52, 0.15);
  cursor: pointer;
  transition:
    transform 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.building-node:hover {
  z-index: 4;
  transform: translate(-50%, -50%) scale(1.08);
  border-color: var(--green);
  box-shadow: 0 16px 32px rgba(21, 70, 52, 0.2);
}

.bubble-low {
  background: rgba(47, 128, 237, 0.12);
}

.bubble-medium {
  background: rgba(245, 158, 11, 0.18);
}

.bubble-high {
  background: rgba(31, 157, 85, 0.2);
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

.node-level {
  color: var(--text-muted);
  font-size: 10px;
  line-height: 1;
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
