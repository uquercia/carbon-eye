// 普通数字格式化：用于表格等需要完整数字的场景
export function formatNumber(value: number) {
  return new Intl.NumberFormat('zh-CN', {
    maximumFractionDigits: 0,
  }).format(value)
}

// 紧凑格式化：用于卡片、地图圆点等空间较小的展示场景
// 例如会把较大的数字格式成更短的显示形式
export function formatCompact(value: number) {
  return new Intl.NumberFormat('zh-CN', {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}
