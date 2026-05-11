<script setup lang="ts">
// 这是顶部指标卡片组件。
// 它本身不计算数据，只负责接收父组件传来的文字并展示出来。
defineProps<{
  label: string // 指标卡片的标签
  value: string // 指标卡片的值
  meta: string // 指标卡片的元数据
  tone?: 'green' | 'blue' | 'amber' | 'red' // 指标卡片的颜色调
}>()
</script>

<template>
  <!-- tone 会附加一个颜色类名，用来控制左侧高亮色 -->
  <div class="metric-tile" :class="tone ?? 'green'">
    <span class="metric-label">{{ label }}</span>
    <strong>{{ value }}</strong>
    <span class="metric-meta">{{ meta }}</span>
  </div>
</template>

<style scoped>
.metric-tile {
  display: grid;
  gap: 6px;
  min-width: 0;
  padding: 14px 16px;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  background: var(--surface);
}

.metric-label,
.metric-meta {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.35;
}

strong {
  color: var(--text-strong);
  font-size: 24px;
  line-height: 1.1;
  letter-spacing: 0;
}

.green {
  box-shadow: inset 3px 0 0 var(--green);
}

.blue {
  box-shadow: inset 3px 0 0 var(--blue);
}

.amber {
  box-shadow: inset 3px 0 0 var(--amber);
}

.red {
  box-shadow: inset 3px 0 0 var(--red);
}
</style>
