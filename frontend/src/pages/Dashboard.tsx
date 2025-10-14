import React from 'react';
import { Link } from 'react-router-dom';
import {
  FiFolder,
  FiZap,
  FiTrendingUp,
  FiClock,
  FiCheckCircle,
  FiPlayCircle,
  FiImage
} from 'react-icons/fi';

const Dashboard: React.FC = () => {
  // 模拟数据 - 实际应该从API获取
  const stats = [
    { name: '总项目数', value: '12', icon: FiFolder, change: '+2', changeType: 'increase' },
    { name: 'AI生成任务', value: '48', icon: FiZap, change: '+12', changeType: 'increase' },
    { name: '完成率', value: '85%', icon: FiTrendingUp, change: '+5%', changeType: 'increase' },
    { name: '进行中', value: '3', icon: FiClock, change: '-1', changeType: 'decrease' },
  ];

  const recentProjects = [
    {
      id: '1',
      name: '母婴品牌春季推广',
      status: 'in_progress',
      platform: 'douyin',
      created_at: '2024-01-15',
      progress: 75
    },
    {
      id: '2',
      name: '科技产品发布会',
      status: 'completed',
      platform: 'wechat',
      created_at: '2024-01-14',
      progress: 100
    },
    {
      id: '3',
      name: '美妆教程系列',
      status: 'pending',
      platform: 'xiaohongshu',
      created_at: '2024-01-13',
      progress: 25
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'in_progress':
        return '进行中';
      case 'pending':
        return '待开始';
      default:
        return '未知';
    }
  };

  const getPlatformText = (platform: string) => {
    const platforms: { [key: string]: string } = {
      'douyin': '抖音',
      'wechat': '微信视频号',
      'xiaohongshu': '小红书',
      'weibo': '微博',
      'bilibili': 'B站'
    };
    return platforms[platform] || platform;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">仪表板</h1>
          <p className="text-gray-600 mt-1">欢迎回来，查看您的创作进展</p>
        </div>
        <Link
          to="/projects/new"
          className="btn btn-primary"
        >
          创建新项目
        </Link>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <Icon className="w-5 h-5 text-blue-600" />
                  </div>
                  <span className={`text-xs font-medium ${
                    stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stat.change}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 最近项目 */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">最近项目</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {recentProjects.map((project) => (
            <div key={project.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    {project.status === 'completed' ? (
                      <FiCheckCircle className="w-5 h-5 text-green-500" />
                    ) : project.status === 'in_progress' ? (
                      <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <div className="w-5 h-5 bg-gray-300 rounded-full" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {project.name}
                    </p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-xs text-gray-500">{getPlatformText(project.platform)}</span>
                      <span className="text-gray-400">•</span>
                      <span className="text-xs text-gray-500">{project.created_at}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                    {getStatusText(project.status)}
                  </span>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${project.progress}%` }}
                    />
                  </div>
                  <Link
                    to={`/projects/${project.id}`}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    查看
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 快速操作 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="card p-6 text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <FiZap className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">AI 创意生成</h3>
          <p className="text-gray-600 text-sm mb-4">基于DeepSeek大模型，快速生成适合中国市场的创意概念</p>
          <Link
            to="/ai-generation"
            className="btn btn-primary w-full"
          >
            开始创作
          </Link>
        </div>

        <div className="card p-6 text-center">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <FiPlayCircle className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">视频制作</h3>
          <p className="text-gray-600 text-sm mb-4">使用即梦大模型，将分镜图像转化为高质量短视频</p>
          <Link
            to="/projects"
            className="btn btn-success w-full"
          >
            查看项目
          </Link>
        </div>

        <div className="card p-6 text-center">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <FiImage className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">素材管理</h3>
          <p className="text-gray-600 text-sm mb-4">管理您的图片、视频素材，支持批量上传和智能分类</p>
          <Link
            to="/assets"
            className="btn btn-secondary w-full"
          >
            管理素材
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;