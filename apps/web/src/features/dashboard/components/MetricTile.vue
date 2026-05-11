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
