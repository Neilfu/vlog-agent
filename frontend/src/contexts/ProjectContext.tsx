// 项目上下文 - Project context for managing project state

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { Project, AIScript, AIStoryboard, AIVideo, ContentOptimization } from '../types';
import { projectAPI, aiAPI } from '../services/api';

interface ProjectContextType {
  currentProject: Project | null;
  projects: Project[];
  isLoading: boolean;
  error: string | null;

  // 项目操作 / Project operations
  setCurrentProject: (project: Project | null) => void;
  loadProjects: (params?: any) => Promise<void>;
  createProject: (projectData: any) => Promise<Project>;
  updateProject: (projectId: string, projectData: any) => Promise<void>;
  deleteProject: (projectId: string) => Promise<void>;

  // AI生成内容 / AI generated content
  generatedScripts: AIScript[];
  generatedStoryboards: AIStoryboard[];
  generatedVideos: AIVideo[];
  contentOptimizations: ContentOptimization[];

  // AI操作 / AI operations
  generateConcept: (params: any) => Promise<any>;
  generateScript: (params: any) => Promise<AIScript>;
  generateStoryboard: (params: any) => Promise<AIStoryboard>;
  generateVideo: (params: any) => Promise<AIVideo>;
  optimizeContent: (params: any) => Promise<ContentOptimization>;

  // 工具函数 / Utility functions
  clearError: () => void;
  refreshProject: (projectId: string) => Promise<void>;
}

interface ProjectProviderProps {
  children: ReactNode;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const useProject = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error('useProject必须在ProjectProvider中使用 / useProject must be used within ProjectProvider');
  }
  return context;
};

export const ProjectProvider: React.FC<ProjectProviderProps> = ({ children }) => {
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [generatedScripts, setGeneratedScripts] = useState<AIScript[]>([]);
  const [generatedStoryboards, setGeneratedStoryboards] = useState<AIStoryboard[]>([]);
  const [generatedVideos, setGeneratedVideos] = useState<AIVideo[]>([]);
  const [contentOptimizations, setContentOptimizations] = useState<ContentOptimization[]>([]);

  // 加载项目列表 / Load project list
  const loadProjects = useCallback(async (params?: any) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await projectAPI.getProjects(params);
      const data = (response as any).data?.data || (response as any).data || [];
      setProjects(data);
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '加载项目失败';
      setError(errorMessage);
      console.error('Error loading projects:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 创建项目 / Create project
  const createProject = useCallback(async (projectData: any): Promise<Project> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await projectAPI.createProject(projectData);
      const newProject = (response as any).data;

      setProjects(prev => [newProject, ...prev]);
      setCurrentProject(newProject);

      return newProject;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '创建项目失败';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 更新项目 / Update project
  const updateProject = useCallback(async (projectId: string, projectData: any) => {
    setIsLoading(true);
    setError(null);

    try {
      await projectAPI.updateProject(projectId, projectData);

      // 更新本地状态 / Update local state
      setProjects(prev =>
        prev.map(project =>
          project.id === projectId
            ? { ...project, ...projectData, updated_at: new Date().toISOString() }
            : project
        )
      );

      if (currentProject?.id === projectId) {
        setCurrentProject(prev => prev ? { ...prev, ...projectData, updated_at: new Date().toISOString() } : null);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '更新项目失败';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [currentProject]);

  // 删除项目 / Delete project
  const deleteProject = useCallback(async (projectId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      await projectAPI.deleteProject(projectId);

      setProjects(prev => prev.filter(project => project.id !== projectId));

      if (currentProject?.id === projectId) {
        setCurrentProject(null);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '删除项目失败';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [currentProject]);

  // AI生成操作 / AI generation operations
  const generateConcept = useCallback(async (params: any) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await aiAPI.generateConcept(params);
      return (response as any).data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '生成创意失败';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const generateScript = useCallback(async (params: any): Promise<AIScript> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await aiAPI.generateScript(params);
      const script = (response as any).data;
      setGeneratedScripts(prev => [script, ...prev]);
      return script;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '生成剧本失败';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const generateStoryboard = useCallback(async (params: any): Promise<AIStoryboard> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await aiAPI.generateStoryboard(params);
      const storyboard = (response as any).data;
      setGeneratedStoryboards(prev => [storyboard, ...prev]);
      return storyboard;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '生成分镜失败';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const generateVideo = useCallback(async (params: any): Promise<AIVideo> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await aiAPI.generateVideo(params);
      const video = (response as any).data;
      setGeneratedVideos(prev => [video, ...prev]);
      return video;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '生成视频失败';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const optimizeContent = useCallback(async (params: any): Promise<ContentOptimization> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await aiAPI.optimizeContent(params);
      const optimization = (response as any).data;
      setContentOptimizations(prev => [optimization, ...prev]);
      return optimization;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '内容优化失败';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 刷新项目数据 / Refresh project data
  const refreshProject = useCallback(async (projectId: string) => {
    try {
      const response = await projectAPI.getProject(projectId);
      const updatedProject = (response as any).data;

      setProjects(prev =>
        prev.map(project =>
          project.id === projectId ? updatedProject : project
        )
      );

      if (currentProject?.id === projectId) {
        setCurrentProject(updatedProject);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '刷新项目失败';
      setError(errorMessage);
      console.error('Error refreshing project:', error);
    }
  }, [currentProject]);

  // 清除错误 / Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const contextValue: ProjectContextType = {
    currentProject,
    projects,
    isLoading,
    error,

    setCurrentProject,
    loadProjects,
    createProject,
    updateProject,
    deleteProject,

    generatedScripts,
    generatedStoryboards,
    generatedVideos,
    contentOptimizations,

    generateConcept,
    generateScript,
    generateStoryboard,
    generateVideo,
    optimizeContent,

    clearError,
    refreshProject,
  };

  return (
    <ProjectContext.Provider value={contextValue}>
      {children}
    </ProjectContext.Provider>
  );
};