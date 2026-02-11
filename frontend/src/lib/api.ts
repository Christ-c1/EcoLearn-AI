import { authService, User } from './auth';

const API_URL = import.meta.env.VITE_API_URL || '';

export type { User };

export interface LearningPath {
  id: number;
  user_id: string;
  title: string;
  description: string;
  topic: string;
  difficulty: string;
  content: string;
  progress: number;
  total_sessions: number;
  completed_sessions: number;
  created_at: string;
  updated_at: string;
}

export interface CarbonMetric {
  id: number;
  user_id: string;
  learning_path_id: number;
  session_duration: number;
  carbon_footprint: number;
  device_type: string;
  energy_consumed: number;
  trees_contribution: number;
  session_date: string;
  created_at: string;
}

export interface TreePlantation {
  id: number;
  user_id: string;
  trees_planted: number;
  carbon_offset: number;
  location: string;
  tree_species: string;
  plantation_date: string;
  certificate_id: string;
  created_at: string;
}

export interface UserStats {
  id: number;
  user_id: string;
  total_learning_time: number;
  total_carbon_footprint: number;
  total_trees_planted: number;
  total_carbon_offset: number;
  paths_completed: number;
  current_streak: number;
  longest_streak: number;
  level: number;
  experience_points: number;
  updated_at: string;
}

// Helper function for API calls
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...authService.getAuthHeaders(),
    ...(options.headers as Record<string, string> || {}),
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erreur réseau' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  getUser(): User | null {
    return authService.getUser();
  },

  async verifyAuth(): Promise<User | null> {
    const result = await authService.verifyToken();
    return result?.user || null;
  },

  async login(email: string, password: string) {
    return authService.login(email, password);
  },

  async register(email: string, password: string, name?: string) {
    return authService.register(email, password, name);
  },

  async logout() {
    await authService.logout();
  },

  isAuthenticated(): boolean {
    return authService.isAuthenticated();
  },

  // Learning Paths - using /api/v1/entities/ prefix
  async getLearningPaths() {
    return apiCall<{ items: LearningPath[]; total: number }>('/api/v1/entities/learning_paths');
  },

  async getLearningPath(id: number) {
    return apiCall<LearningPath>(`/api/v1/entities/learning_paths/${id}`);
  },

  async generateLearningPath(topic: string, difficulty: string) {
    return apiCall<{ success: boolean; learning_path_id: number; content: object }>(
      '/api/v1/learning/generate-path',
      {
        method: 'POST',
        body: JSON.stringify({ topic, difficulty }),
      }
    );
  },

  async updateLearningPath(id: number, data: Partial<LearningPath>) {
    return apiCall<LearningPath>(`/api/v1/entities/learning_paths/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Carbon Metrics - using /api/v1/entities/ prefix
  async getCarbonMetrics() {
    return apiCall<{ items: CarbonMetric[]; total: number }>('/api/v1/entities/carbon_metrics');
  },

  async recordSession(learningPathId: number, durationMinutes: number, deviceType: string) {
    return apiCall<{ success: boolean; carbon_metrics: object; message: string }>(
      '/api/v1/learning/record-session',
      {
        method: 'POST',
        body: JSON.stringify({
          learning_path_id: learningPathId,
          duration_minutes: durationMinutes,
          device_type: deviceType,
        }),
      }
    );
  },

  async getCarbonStats() {
    return apiCall<{
      total_carbon_kg: number;
      total_trees_planted: number;
      carbon_offset_kg: number;
      net_carbon_kg: number;
      is_carbon_positive: boolean;
    }>('/api/v1/learning/carbon-stats');
  },

  // Tree Plantations - using /api/v1/entities/ prefix
  async getTreePlantations() {
    return apiCall<{ items: TreePlantation[]; total: number }>('/api/v1/entities/tree_plantations');
  },

  async plantTree() {
    return apiCall<{ success: boolean; message: string }>('/api/v1/learning/plant-tree', {
      method: 'POST',
    });
  },

  // User Stats - using /api/v1/entities/ prefix
  async getUserStats() {
    return apiCall<{ items: UserStats[]; total: number }>('/api/v1/entities/user_stats');
  },
};