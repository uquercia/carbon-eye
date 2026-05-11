import axios from 'axios'

// 下面这些 type 和后端接口返回字段一一对应。
// 后端 Python 常用 snake_case，比如 electricity_actual；
// 前端页面内部更常用 camelCase，所以 DashboardView.vue 里会再转换一次。
export type DashboardApiBuilding = {
  id: string
  name: string
  zone: string
  major: string
  electricity_actual: number
  electricity_predicted: number
  water_actual: number
  water_predicted: number
  electricity_error: number
  water_error: number
  map_x: number
  map_y: number
}

export type DashboardApiTrend = {
  time_step: number
  electricity_actual: number
  electricity_predicted: number
  water_actual: number
  water_predicted: number
}

export type DashboardApiBehaviorScore = {
  major_name: string
  total_score: number
}

export type DashboardApiRecognitionSample = {
  id: number
  behavior_name: string
  location_name: string
  building_id: string
  confidence: number
  impact_level: string
  impact_summary: string
  electricity_delta_kwh: number
  water_delta_m3: number
  image_url: string
}

export type DashboardApiBehaviorImpact = {
  id: number
  behavior_name: string
  category: string
  description: string
  electricity_factor: number
  water_factor: number
}

export type DashboardApiTrainingImage = {
  id: number
  title: string
  image_url: string
  description: string
}

export type DashboardApiResponse = {
  summary: {
    electricity_actual_total: number
    electricity_predicted_total: number
    water_actual_total: number
    water_predicted_total: number
    average_behavior_score: number
    building_count: number
    recognition_count: number
  }
  buildings: DashboardApiBuilding[]
  behavior_scores: DashboardApiBehaviorScore[]
  trends: DashboardApiTrend[]
  recognition_samples: DashboardApiRecognitionSample[]
  behavior_impacts: DashboardApiBehaviorImpact[]
  training_images: DashboardApiTrainingImage[]
}

export type UploadImageResponse = {
  image: {
    id: number
    original_filename: string
    public_url: string
    content_type: string
    file_size: number
  }
  task: {
    id: number
    status: string
    model_provider: string
    model_name: string
    error_message: string
  }
  results: Array<{
    id: number
    behavior_name: string
    location_name: string
    confidence: number
    impact_summary: string
    electricity_delta_kwh: number
    water_delta_m3: number
  }>
  message: string
}

// axios 实例。baseURL 是后端服务地址。
// 后续如果后端部署到服务器，只需要把这里改成服务器 API 地址，
// 或者改成从 .env 读取。
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000',
  timeout: 8000,
})

// 获取首页驾驶舱数据。
// 这个函数只负责“请求接口并返回数据”，不负责页面展示。
export async function fetchDashboard() {
  const response = await apiClient.get<DashboardApiResponse>('/api/dashboard')
  return response.data
}

export async function uploadCampusImage(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await apiClient.post<UploadImageResponse>('/api/uploads/images', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}
