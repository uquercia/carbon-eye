import axios from 'axios'

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

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 8000,
})

export async function fetchDashboard() {
  const response = await apiClient.get<DashboardApiResponse>('/api/dashboard')
  return response.data
}
