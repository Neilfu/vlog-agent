// 认证Hook - Authentication hook for managing user authentication

import { useState, useEffect, useCallback } from 'react';
import { authAPI } from '../services/api';
import { User, AuthTokens } from '../types';

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

interface AuthHook {
  authState: AuthState;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  clearError: () => void;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  phone?: string;
  preferences?: Record<string, any>;
}

export const useAuth = (): AuthHook => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    tokens: null,
    isLoading: false,
    error: null,
    isAuthenticated: false,
  });

  // 从localStorage初始化认证状态 / Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      const userData = localStorage.getItem('user_data');

      if (token && userData) {
        try {
          const user = JSON.parse(userData);
          setAuthState(prev => ({
            ...prev,
            user,
            tokens: { access_token: token, token_type: 'bearer', expires_in: 1440 },
            isAuthenticated: true,
          }));
        } catch (error) {
          console.error('Error parsing stored user data:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_data');
        }
      }
    };

    initializeAuth();
  }, []);

  // 登录 / Login
  const login = useCallback(async (username: string, password: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await authAPI.login({ username, password });
      const { access_token, user } = (response as any).data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user_data', JSON.stringify(user));

      setAuthState({
        user,
        tokens: { access_token, token_type: 'bearer', expires_in: 1440 },
        isLoading: false,
        error: null,
        isAuthenticated: true,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '登录失败';
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
        isAuthenticated: false,
      }));
      throw new Error(errorMessage);
    }
  }, []);

  // 注册 / Register
  const register = useCallback(async (userData: RegisterData) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await authAPI.register(userData);
      const { access_token, user } = (response as any).data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user_data', JSON.stringify(user));

      setAuthState({
        user,
        tokens: { access_token, token_type: 'bearer', expires_in: 1440 },
        isLoading: false,
        error: null,
        isAuthenticated: true,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '注册失败';
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw new Error(errorMessage);
    }
  }, []);

  // 登出 / Logout
  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_data');
      setAuthState({
        user: null,
        tokens: null,
        isLoading: false,
        error: null,
        isAuthenticated: false,
      });
    }
  }, []);

  // 刷新令牌 / Refresh token
  const refreshToken = useCallback(async () => {
    if (!authState.tokens?.access_token) return;

    try {
      // 这里应该实现真正的令牌刷新逻辑
      // This should implement real token refresh logic
      console.log('Token refresh would be implemented here');
    } catch (error) {
      console.error('Token refresh failed:', error);
      // 如果刷新失败，强制登出
      // If refresh fails, force logout
      await logout();
    }
  }, [authState.tokens, logout]);

  // 清除错误 / Clear error
  const clearError = useCallback(() => {
    setAuthState(prev => ({ ...prev, error: null }));
  }, []);

  // 自动刷新令牌（可选）/ Auto refresh token (optional)
  useEffect(() => {
    if (!authState.tokens?.expires_in) return;

    const expiresIn = authState.tokens.expires_in * 60 * 1000; // 转换为毫秒 / Convert to milliseconds
    const refreshTime = expiresIn - 5 * 60 * 1000; // 提前5分钟刷新 / Refresh 5 minutes early

    const timer = setTimeout(() => {
      refreshToken();
    }, refreshTime);

    return () => clearTimeout(timer);
  }, [authState.tokens, refreshToken]);

  return {
    authState,
    login,
    register,
    logout,
    refreshToken,
    clearError,
  };
};