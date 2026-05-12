<script setup lang="ts">
defineProps<{
  label: string
  value: string
  meta: string
  tone?: 'green' | 'blue' | 'amber' | 'red'
}>()
</script>

<template>
  <div class="metric-tile" :class="tone ?? 'green'">
    <span class="metric-label">{{ label }}</span>
    <strong>{{ value }}</strong>
    <span class="metric-meta">{{ meta }}</span>
  </div>
</template>

<style scoped>
.metric-tile {
  position: relative;
  display: grid;
  gap: 6px;
  min-width: 0;
  overflow: hidden;
  padding: 16px 18px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 252, 250, 0.96)),
    var(--surface);
  box-shadow: var(--shadow-soft);
}

.metric-tile::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: var(--tile-color);
}

.metric-tile::after {
  content: '';
  position: absolute;
  right: 16px;
  top: 16px;
  width: 34px;
  height: 6px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--tile-color) 18%, transparent);
}

.metric-label,
.metric-meta {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.35;
}

strong {
  color: var(--text-strong);
  font-size: 25px;
  line-height: 1.1;
  letter-spacing: 0;
}

.green {
  --tile-color: var(--green);
}

.blue {
  --tile-color: var(--blue);
}

.amber {
  --tile-color: var(--amber);
}

.red {
  --tile-color: var(--red);
}
</style>
