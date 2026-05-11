<script setup lang="ts">
import type { BuildingRecord } from '../data/campusData'
import { formatCompact } from '../utils/format'

// 这个组件只负责中间“楼栋关系图”这块区域。
// 父组件会把所有楼栋数据通过 props 传进来。
defineProps<{
  buildings: BuildingRecord[]
}>()

// 根据楼栋用电量决定圆点大小。
// 用电越高，圆越大；同时限制最小和最大尺寸，避免太小或太夸张。
const getMarkerSize = (value: number) => {
  const size = 28 + Math.sqrt(value) / 32
  return `${Math.min(Math.max(size, 30), 58)}px`
}
</script>

<template>
  <!-- 外层 panel 复用了全局面板样式，内部再补地图专属内容 -->
  <section class="panel campus-map-panel">
    <div class="panel-header">
      <div>
        <p class="eyebrow">临港校区楼栋关系</p>
        <h2>能耗与行为关联图</h2>
      </div>
      <span class="map-status">15 栋建筑</span>
    </div>

    <!-- 这块不是精确地图，而是“示意图”：
         用 x / y 百分比坐标把楼栋按钮摆在容器里的某个位置 -->
    <div class="campus-map" aria-label="上海电机学院临港校区楼栋能耗示意图">
      <!-- 这几条 route 是背景参考线，用来增强“校区道路/关系图”的视觉感觉 -->
      <div class="route route-a" />
      <div class="route route-b" />
      <div class="route route-c" />
      <button
        v-for="building in buildings"
        :key="building.id"
        class="building-node"
        :style="{
          left: `${building.x}%`,
          top: `${building.y}%`,
          width: getMarkerSize(building.electricityActual),
          height: getMarkerSize(building.electricityActual),
        }"
        type="button"
      >
        <!-- 楼栋名和数值都来自 buildingRecords 数据文件 -->
        <span class="node-name">{{ building.name }}</span>
        <span class="node-value">{{ formatCompact(building.electricityActual) }}</span>
      </button>
    </div>

    <!-- 底部图例：解释颜色点代表的专业/区域分类 -->
    <div class="legend-row">
      <span><i class="legend-dot science" />理工科</span>
      <span><i class="legend-dot medical" />医学/生物</span>
      <span><i class="legend-dot life" />公共/生活区</span>
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
  border: 1px solid rgba(20, 83, 45, 0.24);
  border-radius: 50%;
  background: #ffffff;
  color: var(--text-strong);
  box-shadow: 0 8px 20px rgba(21, 70, 52, 0.12);
  cursor: pointer;
  transition:
    transform 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.building-node:hover {
  z-index: 2;
  transform: translate(-50%, -50%) scale(1.08);
  border-color: var(--green);
  box-shadow: 0 12px 26px rgba(21, 70, 52, 0.18);
}

.node-name {
  max-width: 72px;
  overflow: hidden;
  color: var(--text-strong);
  font-size: 11px;
  line-height: 1.15;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-value {
  color: var(--text-muted);
  font-size: 10px;
  line-height: 1;
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
  background: var(--green);
}

.medical {
  background: var(--blue);
}

.life {
  background: var(--amber);
}
</style>
