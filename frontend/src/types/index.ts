// 类型定义 - Type definitions for the Chinese AI Video Creation System

// 基础响应类型 / Base response types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta?: {
    timestamp: string;
    version: string;
    request_id: string;
    pagination?: PaginationInfo;
  };
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// 用户相关类型 / User-related types
export interface User {
  id: string;
  username: string;
  email: string;
  phone?: string;
  avatar?: string;
  role: UserRole;
  organization_id?: string;
  subscription_id?: string;
  preferences: UserPreferences;
  user_metadata: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type UserRole = 'admin' | 'creator' | 'reviewer' | 'client';

export interface UserPreferences {
  language: string;
  timezone: string;
  notifications: {
    email: boolean;
    sms: boolean;
    wechat: boolean;
  };
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
}

// 项目相关类型 / Project-related types
export interface Project {
  id: string;
  title: string;
  slug: string;
  description?: string;
  status: ProjectStatus;
  priority: string;
  project_type: string;
  business_input: BusinessInput;
  technical_specs: TechnicalSpecs;
  progress: ProjectProgress;
  project_metadata: Record<string, any>;
  creator_id: string;
  organization_id?: string;
  workflow_id?: string;
  parent_project_id?: string;
  deadline?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export type ProjectStatus =
  | 'draft'
  | 'concept'
  | 'scripting'
  | 'storyboard'
  | 'production'
  | 'post_production'
  | 'review'
  | 'published'
  | 'archived';

export interface BusinessInput {
  target_audience: string;
  cultural_context: string;
  key_message?: string;
  call_to_action?: string;
  brand_guidelines?: string;
  competitor_analysis?: string;
}

export interface TechnicalSpecs {
  duration?: number;
  resolution?: string;
  aspect_ratio?: string;
  frame_rate?: number;
  video_codec?: string;
  audio_codec?: string;
  file_format?: string;
  max_file_size?: number;
}

export interface ProjectProgress {
  [key: string]: any;
  completion_percentage?: number;
  current_stage?: string;
  estimated_completion?: string;
}

// AI服务相关类型 / AI Service-related types
export interface AIConcept {
  id: string;
  title: string;
  description: string;
  key_elements: string[];
  visual_style: string;
  narrative_arc: string;
  estimated_engagement: string;
  cultural_relevance: string;
  platform_optimization: Record<string, PlatformOptimization>;
}

export interface PlatformOptimization {
  hashtags: string[];
  posting_time?: string;
  content_format?: string;
  optimal_length?: number;
  engagement_tips?: string[];
}

export interface AIScript {
  id: string;
  title: string;
  scenes: ScriptScene[];
  total_duration: number;
  voiceover_text?: string;
  subtitles?: string[];
  music_suggestions?: string[];
  sound_effects?: string[];
}

export interface ScriptScene {
  id: string;
  title: string;
  description: string;
  duration: number;
  visual_directions: string;
  audio_directions: string;
  transition?: string;
  notes?: string;
}

export interface AIStoryboard {
  id: string;
  images: StoryboardImage[];
  total_scenes: number;
  style: string;
  generation_time: number;
  cost_estimate: number;
}

export interface StoryboardImage {
  scene_index: number;
  scene_data: ScriptScene;
  image_url: string;
  thumbnail_url?: string;
  alt_text?: string;
  technical_details?: {
    resolution: string;
    format: string;
    size: number;
  };
}

export interface AIVideo {
  id: string;
  video_url: string;
  thumbnail_url?: string;
  duration: number;
  resolution: string;
  frame_rate: number;
  file_size: number;
  format: string;
  generation_time: number;
  cost_estimate: number;
}

export interface ContentOptimization {
  original_content: string;
  optimized_content: string;
  optimization_type: string;
  platform: string;
  improvements: string[];
  metrics_prediction?: {
    engagement_rate?: number;
    view_count?: number;
    share_count?: number;
  };
}

// 媒体资源类型 / Media Asset types
export interface MediaAsset {
  id: string;
  name: string;
  type: AssetType;
  url: string;
  thumbnail_url?: string;
  file_size: number;
  mime_type: string;
  technical_specs: TechnicalSpecs;
  project_id?: string;
  created_at: string;
  updated_at: string;
}

export type AssetType = 'image' | 'video' | 'audio' | 'document' | 'other';

// 平台目标类型 / Platform target types
export type PlatformTarget =
  | 'douyin'
  | 'wechat'
  | 'weibo'
  | 'xiaohongshu'
  | 'bilibili'
  | 'youtube';

// AI模型类型 / AI Model types
export interface AIModel {
  id: string;
  name: string;
  provider: string;
  model_type: 'text' | 'image' | 'video' | 'audio';
  model_id: string;
  version: string;
  endpoint: string;
  config: Record<string, any>;
  pricing: Record<string, any>;
  performance: Record<string, any>;
  status: string;
  rate_limit: Record<string, any>;
  region: string;
  compliance: string[];
  created_at: string;
  updated_at: string;
}

// 工作流类型 / Workflow types
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  steps: WorkflowStep[];
  status: 'active' | 'inactive';
  created_at: string;
  updated_at: string;
}

export interface WorkflowStep {
  id: string;
  name: string;
  type: string;
  config: Record<string, any>;
  dependencies: string[];
  timeout?: number;
  retry_count?: number;
}

// 任务类型 / Task types
export interface Task {
  id: string;
  task_type: TaskType;
  project_id: string;
  parameters: Record<string, any>;
  status: TaskStatus;
  result?: Record<string, any>;
  error?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export type TaskType =
  | 'concept_generation'
  | 'script_writing'
  | 'storyboard_creation'
  | 'video_generation'
  | 'content_optimization'
  | 'quality_review';

export type TaskStatus =
  | 'pending'
  | 'in_progress'
  | 'completed'
  | 'failed'
  | 'cancelled';

// 表单类型 / Form types
export interface FormValidation {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => boolean | string;
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'file';
  placeholder?: string;
  options?: { value: string; label: string }[];
  validation?: FormValidation;
  defaultValue?: any;
  disabled?: boolean;
  hidden?: boolean;
}

// 主题类型 / Theme types
export interface Theme {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: {
    primary: string;
    secondary: string;
    disabled: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  typography: {
    fontFamily: string;
    fontSize: {
      xs: string;
      sm: string;
      md: string;
      lg: string;
      xl: string;
    };
  };
}

// 错误类型 / Error types
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp?: string;
  path?: string;
  method?: string;
}

// 加载状态类型 / Loading state types
export interface LoadingState {
  isLoading: boolean;
  error: AppError | null;
  progress?: number;
}

// 分页参数类型 / Pagination parameter types
export interface PaginationParams {
  page: number;
  limit: number;
  sort?: string;
  order?: 'asc' | 'desc';
  search?: string;
  filters?: Record<string, any>;
}

// 统计类型 / Statistics types
export interface UsageStats {
  total_projects: number;
  total_videos_generated: number;
  total_ai_calls: number;
  average_generation_time: number;
  total_cost: number;
  popular_platforms: Array<{ platform: PlatformTarget; count: number }>;
  popular_content_types: Array<{ type: string; count: number }>;
}

// 通知类型 / Notification types
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  duration?: number;
  persistent?: boolean;
  created_at: string;
}

// 设置类型 / Settings types
export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  language: 'zh-CN' | 'en-US';
  notifications: {
    email: boolean;
    push: boolean;
    in_app: boolean;
  };
  privacy: {
    share_analytics: boolean;
    allow_tracking: boolean;
  };
  ai_preferences: {
    default_temperature: number;
    preferred_model: string;
    auto_save: boolean;
  };
}

// 导出所有类型 / Export all types
export type {
  User,
  UserRole,
  UserPreferences,
  AuthTokens,
  Project,
  ProjectStatus,
  BusinessInput,
  TechnicalSpecs,
  ProjectProgress,
  AIConcept,
  PlatformOptimization,
  AIScript,
  ScriptScene,
  AIStoryboard,
  StoryboardImage,
  AIVideo,
  ContentOptimization,
  MediaAsset,
  AssetType,
  PlatformTarget,
  AIModel,
  Workflow,
  WorkflowStep,
  Task,
  TaskType,
  TaskStatus,
  FormValidation,
  FormField,
  Theme,
  AppError,
  LoadingState,
  PaginationParams,
  UsageStats,
  Notification,
  UserSettings,
};

export type {
  ApiResponse,
  ApiError,
  PaginationInfo,
};