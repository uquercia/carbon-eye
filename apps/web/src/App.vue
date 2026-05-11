<script setup lang="ts">
 // App.vue 是根组件。
 // 当前项目比较简单，根组件只负责加载驾驶舱页面组件。
 import DashboardView from './features/dashboard/DashboardView.vue'
</script>

<template>
   <!-- 根组件当前直接渲染唯一主页面 -->
  <DashboardView />
</template>
