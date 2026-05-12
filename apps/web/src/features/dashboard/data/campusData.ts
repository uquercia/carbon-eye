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
  x: number
  y: number
}

export type BehaviorScore = {
  major: string
  score: number
}

export type TrendPoint = {
  step: string
  electricityActual: number
  electricityPredicted: number
  waterActual: number
  waterPredicted: number
}

export type RecognitionSample = {
  id: number
  behaviorName: string
  locationName: string
  buildingId: string
  confidence: number
  impactLevel: string
  impactSummary: string
  electricityDeltaKwh: number
  waterDeltaM3: number
  imageUrl: string
}

export type BehaviorImpact = {
  id: number
  behaviorName: string
  category: string
  description: string
  electricityFactor: number
  waterFactor: number
}

export type TrainingImage = {
  id: number
  title: string
  imageUrl: string
  description: string
}

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

export const behaviorScores: BehaviorScore[] = [
  { major: '理工科', score: 3.23 },
  { major: '文科', score: 4.0 },
  { major: '商科/管理', score: 3.6 },
  { major: '艺术/设计', score: 3.78 },
  { major: '医学/生物', score: 3.86 },
  { major: '其他', score: 3.49 },
]

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

export const recognitionSamples: RecognitionSample[] = [
  {
    id: 1,
    behaviorName: '随手关灯关空调',
    locationName: '教学楼教室',
    buildingId: 'building_05',
    confidence: 0.93,
    impactLevel: '正向',
    impactSummary: '识别到离开教室后关闭电器，预计降低教学楼夜间空载用电。',
    electricityDeltaKwh: -18.5,
    waterDeltaM3: 0,
    imageUrl: '/training/electricity_prediction.png',
  },
  {
    id: 2,
    behaviorName: '及时关闭水龙头',
    locationName: '公共洗手区',
    buildingId: 'building_10',
    confidence: 0.89,
    impactLevel: '正向',
    impactSummary: '识别到用水后关闭水龙头，预计减少公共区域用水浪费。',
    electricityDeltaKwh: 0,
    waterDeltaM3: -6.8,
    imageUrl: '/training/water_prediction.png',
  },
]

export const behaviorImpacts: BehaviorImpact[] = [
  {
    id: 1,
    behaviorName: '随手关灯关空调',
    category: '用电',
    description: '离开教室后关闭照明和空调，可直接降低空载用电。',
    electricityFactor: -0.12,
    waterFactor: 0,
  },
  {
    id: 2,
    behaviorName: '拔掉闲置充电器',
    category: '用电',
    description: '减少待机功耗，对宿舍和活动中心的小负荷有持续影响。',
    electricityFactor: -0.04,
    waterFactor: 0,
  },
  {
    id: 3,
    behaviorName: '白天优先自然采光',
    category: '用电',
    description: '白天减少照明开启时长，适合教学楼和办公楼。',
    electricityFactor: -0.08,
    waterFactor: 0,
  },
  {
    id: 4,
    behaviorName: '拔插头断电',
    category: '用电',
    description: '离开宿舍、实验室或办公室前关闭插排并拔掉插头，可减少电脑、显示器和外设待机耗电。',
    electricityFactor: -0.07,
    waterFactor: 0,
  },
  {
    id: 5,
    behaviorName: '及时关闭水龙头',
    category: '用水',
    description: '洗手、清洁后关闭水龙头，可降低公共区域用水浪费。',
    electricityFactor: 0,
    waterFactor: -0.1,
  },
  {
    id: 6,
    behaviorName: '缩短淋浴时间',
    category: '用水',
    description: '降低宿舍和体育区生活热水/冷水消耗。',
    electricityFactor: -0.02,
    waterFactor: -0.16,
  },
  {
    id: 7,
    behaviorName: '集中洗涤衣物',
    category: '用水',
    description: '减少洗衣机低负载运行次数，同时降低水电消耗。',
    electricityFactor: -0.06,
    waterFactor: -0.12,
  },
  {
    id: 8,
    behaviorName: '主动报修漏水漏电',
    category: '综合',
    description: '通过报修异常设备减少持续浪费，是高价值干预行为。',
    electricityFactor: -0.1,
    waterFactor: -0.14,
  },
]

export const trainingImages: TrainingImage[] = [
  {
    id: 1,
    title: '用电预测训练结果',
    imageUrl: '/training/electricity_prediction.png',
    description: '展示模型对各楼栋用电量的实际/预测对比。',
  },
  {
    id: 2,
    title: '训练损失曲线',
    imageUrl: '/training/training_loss.png',
    description: '用于观察模型训练收敛情况。',
  },
]
