// 这里是当前页面使用的静态示例数据。
// 现在项目还没有真正接后端 API，所以页面里的表格、图表、楼栋地图都先从这里读取。
export type BuildingRecord = {
  id: string
  name: string
  zone: string
  major: string
  electricityActual: number
  electricityPredicted: number
  waterActual: number
  waterPredicted: number
  electricityError: number
  waterError: number
  // x / y 不是数据库字段意义上的坐标系统，而是页面示意图里的百分比坐标。
  // 例如 x: 24 表示按钮放在地图容器左侧 24% 的位置。
  x: number
  y: number
}

// 不同专业的低碳行为评分数据，用于底部柱状图
export type BehaviorScore = {
  major: string
  score: number
}

// 趋势图数据：每个 step 可以理解为一个时间步/一个采样点
export type TrendPoint = {
  step: string
  electricityActual: number
  electricityPredicted: number
  waterActual: number
  waterPredicted: number
}

// 楼栋基础数据：
// - 右侧表格会直接使用这些字段
// - 中间地图会使用 name、electricityActual、x、y
// - 顶部卡片和左侧排行会对这些数据做汇总/排序
export const buildingRecords: BuildingRecord[] = [
  {
    id: 'greenhouse',
    name: '(温室)园艺系',
    zone: '北区',
    major: '理工科',
    electricityActual: 28375,
    electricityPredicted: 50225,
    waterActual: 73798,
    waterPredicted: 72837,
    electricityError: 21850,
    waterError: 961,
    x: 24,
    y: 18,
  },
  {
    id: 'humanities',
    name: '人文大楼',
    zone: '西区',
    major: '文科',
    electricityActual: 42596,
    electricityPredicted: 56503,
    waterActual: 37484,
    waterPredicted: 57572,
    electricityError: 13907,
    waterError: 20088,
    x: 16,
    y: 44,
  },
  {
    id: 'veterinary',
    name: '动物医学研究中心',
    zone: '东北区',
    major: '医学/生物',
    electricityActual: 32429,
    electricityPredicted: 54988,
    waterActual: 27109,
    waterPredicted: 51937,
    electricityError: 22559,
    waterError: 24829,
    x: 58,
    y: 18,
  },
  {
    id: 'animal-science',
    name: '动科大楼',
    zone: '东北区',
    major: '医学/生物',
    electricityActual: 77755,
    electricityPredicted: 69631,
    waterActual: 49204,
    waterPredicted: 60124,
    electricityError: 8124,
    waterError: 10919,
    x: 74,
    y: 30,
  },
  {
    id: 'chemistry',
    name: '化学大楼',
    zone: '中区',
    major: '理工科',
    electricityActual: 234561,
    electricityPredicted: 229255,
    waterActual: 84557,
    waterPredicted: 69018,
    electricityError: 5306,
    waterError: 15539,
    x: 42,
    y: 42,
  },
  {
    id: 'student-center',
    name: '学生活动中心',
    zone: '生活区',
    major: '其他',
    electricityActual: 16461,
    electricityPredicted: 53163,
    waterActual: 24035,
    waterPredicted: 44596,
    electricityError: 36702,
    waterError: 20562,
    x: 58,
    y: 58,
  },
  {
    id: 'applied-science',
    name: '应科大楼',
    zone: '中区',
    major: '理工科',
    electricityActual: 305513,
    electricityPredicted: 270174,
    waterActual: 65344,
    waterPredicted: 67937,
    electricityError: 35339,
    waterError: 2593,
    x: 34,
    y: 66,
  },
  {
    id: 'mechanical',
    name: '机械馆',
    zone: '东区',
    major: '理工科',
    electricityActual: 25980,
    electricityPredicted: 50759,
    waterActual: 24035,
    waterPredicted: 59974,
    electricityError: 24779,
    waterError: 35939,
    x: 78,
    y: 56,
  },
  {
    id: 'concrete',
    name: '混凝土中心大楼',
    zone: '东区',
    major: '理工科',
    electricityActual: 11756,
    electricityPredicted: 44410,
    waterActual: 42480,
    waterPredicted: 63688,
    electricityError: 32654,
    waterError: 21208,
    x: 86,
    y: 74,
  },
  {
    id: 'pool',
    name: '游泳池',
    zone: '体育区',
    major: '其他',
    electricityActual: 345,
    electricityPredicted: 48350,
    waterActual: 54584,
    waterPredicted: 64333,
    electricityError: 48005,
    waterError: 9749,
    x: 50,
    y: 82,
  },
  {
    id: 'biology',
    name: '生科大楼',
    zone: '北区',
    major: '医学/生物',
    electricityActual: 349714,
    electricityPredicted: 323152,
    waterActual: 213480,
    waterPredicted: 175406,
    electricityError: 26562,
    waterError: 38074,
    x: 36,
    y: 24,
  },
  {
    id: 'admin',
    name: '行政大楼',
    zone: '南区',
    major: '其他',
    electricityActual: 58097,
    electricityPredicted: 78675,
    waterActual: 29222,
    waterPredicted: 48130,
    electricityError: 20578,
    waterError: 18908,
    x: 20,
    y: 78,
  },
  {
    id: 'diagnosis',
    name: '诊断中心',
    zone: '东北区',
    major: '医学/生物',
    electricityActual: 50235,
    electricityPredicted: 61525,
    waterActual: 28838,
    waterPredicted: 53018,
    electricityError: 11290,
    waterError: 24180,
    x: 68,
    y: 46,
  },
  {
    id: 'agriculture',
    name: '农环大楼',
    zone: '北区',
    major: '理工科',
    electricityActual: 333807,
    electricityPredicted: 268429,
    waterActual: 393511,
    waterPredicted: 360355,
    electricityError: 65378,
    waterError: 33157,
    x: 48,
    y: 12,
  },
  {
    id: 'gym',
    name: '体育馆',
    zone: '体育区',
    major: '其他',
    electricityActual: 17612,
    electricityPredicted: 50562,
    waterActual: 36139,
    waterPredicted: 52850,
    electricityError: 32950,
    waterError: 16711,
    x: 66,
    y: 86,
  },
]

// 不同专业问卷聚合后的行为分数
export const behaviorScores: BehaviorScore[] = [
  { major: '理工科', score: 3.23 },
  { major: '文科', score: 4.0 },
  { major: '商科/管理', score: 3.6 },
  { major: '艺术/设计', score: 3.78 },
  { major: '医学/生物', score: 3.86 },
  { major: '其他', score: 3.49 },
]

// 用电/用水趋势数据：供底部 2 个趋势图直接使用
export const trendData: TrendPoint[] = [
  {
    step: '41',
    electricityActual: 1067743,
    electricityPredicted: 1057889,
    waterActual: 1161845,
    waterPredicted: 1169783,
  },
  {
    step: '42',
    electricityActual: 1046638,
    electricityPredicted: 1051090,
    waterActual: 1043369,
    waterPredicted: 1070212,
  },
  {
    step: '43',
    electricityActual: 1115205,
    electricityPredicted: 1088450,
    waterActual: 1187258,
    waterPredicted: 1142030,
  },
  {
    step: '44',
    electricityActual: 1019370,
    electricityPredicted: 1035024,
    waterActual: 997405,
    waterPredicted: 1026940,
  },
  {
    step: '45',
    electricityActual: 943820,
    electricityPredicted: 972310,
    waterActual: 934170,
    waterPredicted: 952640,
  },
  {
    step: '46',
    electricityActual: 892460,
    electricityPredicted: 916780,
    waterActual: 875920,
    waterPredicted: 891400,
  },
]
