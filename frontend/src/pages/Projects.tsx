import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FiPlus,
  FiSearch,
  FiFilter,
  FiMoreVertical,
  FiFolder,
  FiClock,
  FiCheckCircle,
  FiPlayCircle,
  FiEdit,
  FiTrash2,
  FiShare2,
  FiZap
} from 'react-icons/fi';

const Projects: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPlatform, setFilterPlatform] = useState('all');

  // 模拟项目数据
  const projects = [
    {
      id: '1',
      name: '母婴品牌春季推广',
      description: '为知名母婴品牌创作春季新品推广短视频，目标受众为年轻妈妈群体',
      status: 'in_progress',
      platform: 'douyin',
      target_audience: '25-35岁年轻妈妈',
      cultural_context: '春季育儿，关注宝宝健康成长',
      created_at: '2024-01-15',
      updated_at: '2024-01-16',
      progress: 75,
      ai_tasks_count: 8,
      completed_tasks_count: 6
    },
    {
      id: '2',
      name: '科技产品发布会',
      description: '智能手机新品发布会宣传视频制作',
      status: 'completed',
      platform: 'wechat',
      target_audience: '科技爱好者',
      cultural_context: '中国科技创新，国产品牌自信',
      created_at: '2024-01-14',
      updated_at: '2024-01-15',
      progress: 100,
      ai_tasks_count: 12,
      completed_tasks_count: 12
    },
    {
      id: '3',
      name: '美妆教程系列',
      description: '日常妆容教程系列短视频',
      status: 'pending',
      platform: 'xiaohongshu',
      target_audience: '18-28岁女性',
      cultural_context: '自然美，东方美学',
      created_at: '2024-01-13',
      updated_at: '2024-01-13',
      progress: 25,
      ai_tasks_count: 5,
      completed_tasks_count: 1
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

  const getPlatformColor = (platform: string) => {
    const colors: { [key: string]: string } = {
      'douyin': 'bg-black text-white',
      'wechat': 'bg-green-500 text-white',
      'xiaohongshu': 'bg-red-500 text-white',
      'weibo': 'bg-orange-500 text-white',
      'bilibili': 'bg-pink-500 text-white'
    };
    return colors[platform] || 'bg-gray-500 text-white';
  };

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || project.status === filterStatus;
    const matchesPlatform = filterPlatform === 'all' || project.platform === filterPlatform;

    return matchesSearch && matchesStatus && matchesPlatform;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">项目管理</h1>
          <p className="text-gray-600 mt-1">管理和跟踪您的AI短视频创作项目</p>
        </div>
        <Link
          to="/projects/new"
          className="btn btn-primary"
        >
          <FiPlus className="w-4 h-4 mr-2" />
          创建项目
        </Link>
      </div>

      {/* 搜索和筛选 */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="搜索项目名称或描述..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-input pl-10"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="form-input"
            >
              <option value="all">所有状态</option>
              <option value="pending">待开始</option>
              <option value="in_progress">进行中</option>
              <option value="completed">已完成</option>
            </select>
            <select
              value={filterPlatform}
              onChange={(e) => setFilterPlatform(e.target.value)}
              className="form-input"
            >
              <option value="all">所有平台</option>
              <option value="douyin">抖音</option>
              <option value="wechat">微信视频号</option>
              <option value="xiaohongshu">小红书</option>
              <option value="weibo">微博</option>
              <option value="bilibili">B站</option>
            </select>
          </div>
        </div>
      </div>

      {/* 项目列表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredProjects.map((project) => (
          <div key={project.id} className="card overflow-hidden">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">
                    {project.name}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                    {project.description}
                  </p>
                </div>
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                  <FiMoreVertical className="w-4 h-4" />
                </button>
              </div>

              <div className="flex items-center space-x-2 mb-4">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                  {getStatusText(project.status)}
                </span>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPlatformColor(project.platform)}`}>
                  {getPlatformText(project.platform)}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm text-gray-600">
                  <span className="font-medium mr-2">目标受众:</span>
                  <span>{project.target_audience}</span>
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="font-medium mr-2">文化背景:</span>
                  <span className="truncate">{project.cultural_context}</span>
                </div>
              </div>

              <div className="mb-4">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-gray-600">进度</span>
                  <span className="font-medium">{project.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${project.progress}%` }}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    <FiZap className="w-4 h-4 mr-1" />
                    <span>{project.ai_tasks_count} 任务</span>
                  </div>
                  <div className="flex items-center">
                    <FiCheckCircle className="w-4 h-4 mr-1" />
                    <span>{project.completed_tasks_count} 完成</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-500">
                  创建于 {project.created_at}
                </div>
                <div className="flex space-x-2">
                  <Link
                    to={`/projects/${project.id}`}
                    className="btn btn-primary text-sm"
                  >
                    查看详情
                  </Link>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredProjects.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FiFolder className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">没有找到项目</h3>
          <p className="text-gray-600 mb-4">尝试调整搜索条件或创建新项目</p>
          <Link
            to="/projects/new"
            className="btn btn-primary"
          >
            创建项目
          </Link>
        </div>
      )}
    </div>
  );
};

export default Projects;