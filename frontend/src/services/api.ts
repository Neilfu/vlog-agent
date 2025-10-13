// API服务 - 处理所有后端API调用
// API Service - Handles all backend API calls

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API配置 / API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// 创建axios实例 / Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30秒超时 / 30 second timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// 请求拦截器 / Request interceptor
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 添加认证令牌 / Add authentication token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers = {
        ...config.headers,
        'Authorization': `Bearer ${token}`,
      };
    }

    // 添加请求ID用于跟踪 / Add request ID for tracking
    config.headers['X-Request-ID'] = Math.random().toString(36).substring(7);

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 / Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 处理成功响应 / Handle successful response
    return response;
  },
  (error) => {
    // 处理错误响应 / Handle error response
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 401:
          // 未授权 - 清除令牌并重定向到登录 / Unauthorized - clear token and redirect to login
          localStorage.removeItem('access_token');
          window.location.href = '/login';
          break;
        case 403:
          // 权限不足 / Insufficient permissions
          console.error('权限不足 / Insufficient permissions');
          break;
        case 404:
          // 资源未找到 / Resource not found
          console.error('请求的资源不存在 / Requested resource does not exist');
          break;
        case 429:
          // 速率限制 / Rate limit
          console.error('请求过于频繁，请稍后重试 / Too many requests, please try again later');
          break;
        case 500:
          // 服务器错误 / Server error
          console.error('服务器内部错误 / Internal server error');
          break;
        default:
          console.error(`未知错误: ${status} / Unknown error: ${status}`);
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应 / Request was sent but no response was received
      console.error('网络连接错误 / Network connection error');
    } else {
      // 设置请求时发生错误 / Error occurred while setting up the request
      console.error('请求配置错误 / Request configuration error');
    }

    return Promise.reject(error);
  }
);

// API响应类型 / API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta?: {
    timestamp: string;
    version: string;
    request_id: string;
    pagination?: {
      page: number;
      limit: number;
      total: number;
      pages: number;
      has_next: boolean;
      has_prev: boolean;
    };
  };
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: string;
  path: string;
  method: string;
}

// 认证相关API / Authentication APIs
export const authAPI = {
  // 用户登录 / User login
  login: async (credentials: { username: string; password: string }) => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  // 用户注册 / User registration
  register: async (userData: {
    username: string;
    email: string;
    password: string;
    phone?: string;
    preferences?: Record<string, any>;
  }) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  // 刷新令牌 / Refresh token
  refreshToken: async (refreshToken: string) => {
    const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },

  // 登出 / Logout
  logout: async () => {
    const response = await apiClient.post('/auth/logout');
    localStorage.removeItem('access_token');
    return response.data;
  },
};

// 用户相关API / User APIs
export const userAPI = {
  // 获取用户资料 / Get user profile
  getProfile: async () => {
    const response = await apiClient.get('/users/profile');
    return response.data;
  },

  // 更新用户资料 / Update user profile
  updateProfile: async (profileData: any) => {
    const response = await apiClient.put('/users/profile', profileData);
    return response.data;
  },

  // 获取用户项目 / Get user projects
  getProjects: async (params?: { page?: number; limit?: number; status?: string }) => {
    const response = await apiClient.get('/users/projects', { params });
    return response.data;
  },
};

// 项目相关API / Project APIs
export const projectAPI = {
  // 获取项目列表 / Get project list
  getProjects: async (params?: {
    page?: number;
    limit?: number;
    status?: string;
    search?: string;
  }) => {
    const response = await apiClient.get('/projects', { params });
    return response.data;
  },

  // 获取项目详情 / Get project details
  getProject: async (projectId: string) => {
    const response = await apiClient.get(`/projects/${projectId}`);
    return response.data;
  },

  // 创建项目 / Create project
  createProject: async (projectData: any) => {
    const response = await apiClient.post('/projects', projectData);
    return response.data;
  },

  // 更新项目 / Update project
  updateProject: async (projectId: string, projectData: any) => {
    const response = await apiClient.put(`/projects/${projectId}`, projectData);
    return response.data;
  },

  // 删除项目 / Delete project
  deleteProject: async (projectId: string) => {
    const response = await apiClient.delete(`/projects/${projectId}`);
    return response.data;
  },
};

// AI服务相关API / AI Service APIs
export const aiAPI = {
  // 生成创意概念 / Generate creative concept
  generateConcept: async (params: {
    prompt: string;
    cultural_context: string;
    platform_target: string;
    target_age_group?: string;
    tone?: string;
    duration?: number;
    temperature?: number;
  }) => {
    const response = await apiClient.post('/ai/generate-concept', params);
    return response.data;
  },

  // 生成剧本 / Generate script
  generateScript: async (params: {
    concept: string;
    cultural_context: string;
    target_platform: string;
    duration?: number;
    tone?: string;
    target_audience?: string;
  }) => {
    const response = await apiClient.post('/ai/generate-script', params);
    return response.data;
  },

  // 生成分镜 / Generate storyboard
  generateStoryboard: async (params: {
    scenes: Array<{
      description: string;
      emotional_tone?: string;
      visual_style?: string;
    }>;
    style?: string;
    resolution?: string;
    color_palette?: string[];
  }) => {
    const response = await apiClient.post('/ai/generate-storyboard', params);
    return response.data;
  },

  // 生成视频 / Generate video
  generateVideo: async (params: {
    image_urls: string[];
    duration?: number;
    resolution?: string;
    frame_rate?: number;
    transition_style?: string;
    music_style?: string;
    voiceover_text?: string;
  }) => {
    const response = await apiClient.post('/ai/generate-video', params);
    return response.data;
  },

  // 优化内容 / Optimize content
  optimizeContent: async (params: {
    content: string;
    optimization_type: string;
    platform: string;
    target_metrics?: string[];
  }) => {
    const response = await apiClient.post('/ai/optimize-content', params);
    return response.data;
  },
};

// 媒体资源相关API / Media Asset APIs
export const assetAPI = {
  // 上传文件 / Upload file
  uploadFile: async (formData: FormData) => {
    const response = await apiClient.post('/assets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // 获取资源列表 / Get asset list
  getAssets: async (params?: { type?: string; project_id?: string }) => {
    const response = await apiClient.get('/assets', { params });
    return response.data;
  },

  // 获取资源详情 / Get asset details
  getAsset: async (assetId: string) => {
    const response = await apiClient.get(`/assets/${assetId}`);
    return response.data;
  },

  // 删除资源 / Delete asset
  deleteAsset: async (assetId: string) => {
    const response = await apiClient.delete(`/assets/${assetId}`);
    return response.data;
  },
};

// 健康检查 / Health Check
export const healthAPI = {
  // 检查系统健康状态 / Check system health
  checkHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // 检查API状态 / Check API status
  checkAPIStatus: async () => {
    const response = await apiClient.get('/health/api');
    return response.data;
  },
};

// 工具函数 / Utility Functions
export const apiUtils = {
  // 构建查询字符串 / Build query string
  buildQueryString: (params: Record<string, any>) => {
    const query = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null) {
        query.append(key, params[key]);
      }
    });
    return query.toString();
  },

  // 格式化错误消息 / Format error message
  formatErrorMessage: (error: any) => {
    if (error.response?.data?.error?.message) {
      return error.response.data.error.message;
    } else if (error.message) {
      return error.message;
    } else {
      return '未知错误 / Unknown error';
    }
  },

  // 检查网络连接 / Check network connection
  checkNetwork: async () => {
    try {
      await healthAPI.checkHealth();
      return true;
    } catch (error) {
      return false;
    }
  },
};

export default apiClient;