import type { EChartsOption } from 'echarts'

// 给 ECharts 的原始类型起一个本项目内部更直观的名字，
// 这样在页面组件里看到 ChartOption 更容易理解用途。
export type ChartOption = EChartsOption
