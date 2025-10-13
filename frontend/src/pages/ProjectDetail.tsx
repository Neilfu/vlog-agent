import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  FiArrowLeft,
  FiEdit,
  FiTrash2,
  FiShare2,
  FiZap,
  FiImage,
  FiPlayCircle,
  FiCheckCircle,
  FiClock,
  FiMoreVertical,
  FiDownload,
  FiEye
} from 'react-icons/fi';

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState('overview');

  // 模拟项目数据
  const project = {
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
    completed_tasks_count: 6,
    total_duration: 180, // 总时长（秒）
    estimated_cost: 150, // 预估成本（元）
    actual_cost: 120, // 实际成本（元）
  };

  // 模拟AI任务数据
  const aiTasks = [
    {
      id: 'task-1',
      type: 'concept_generation',
      name: '创意概念生成',
      status: 'completed',
      created_at: '2024-01-15T10:00:00Z',
      completed_at: '2024-01-15T10:05:00Z',
      result: {
        concept: '春季母婴护肤新理念',
        theme: '温柔呵护，健康成长'
      }
    },
    {
      id: 'task-2',
      type: 'script_writing',
      name: '剧本创作',
      status: 'completed',
      created_at: '2024-01-15T10:10:00Z',
      completed_at: '2024-01-15T10:20:00Z',
      result: {
        scenes: 6,
        duration: 60,
        tone: '温馨感人'
      }
    },
    {
      id: 'task-3',
      type: 'storyboard_creation',
      name: '分镜图像生成',
      status: 'in_progress',
      created_at: '2024-01-15T10:30:00Z',
      progress: 66.7,
      result: {
        images_generated: 4,
        total_images: 6
      }
    },
    {
      id: 'task-4',
      type: 'video_generation',
      name: '视频合成',
      status: 'pending',
      created_at: null,
      result: null
    }
  ];

  // 模拟素材数据
  const assets = [
    {
      id: 'asset-1',
      name: '春季花朵背景',
      type: 'image',
      url: 'https://example.com/flower-bg.jpg',
      thumbnail_url: 'https://example.com/flower-bg-thumb.jpg',
      size: '2.5MB',
      format: 'jpg',
      created_at: '2024-01-15T11:00:00Z'
    },
    {
      id: 'asset-2',
      name: '宝宝护肤场景1',
      type: 'image',
      url: 'https://example.com/baby-scene1.jpg',
      thumbnail_url: 'https://example.com/baby-scene1-thumb.jpg',
      size: '3.1MB',
      format: 'jpg',
      created_at: '2024-01-15T11:30:00Z'
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

  const getTaskTypeText = (type: string) => {
    const types: { [key: string]: string } = {
      'concept_generation': '创意概念生成',
      'script_writing': '剧本创作',
      'storyboard_creation': '分镜图像生成',
      'video_generation': '视频合成',
      'content_optimization': '内容优化'
    };
    return types[type] || type;
  };

  const getTaskTypeIcon = (type: string) => {
    switch (type) {
      case 'concept_generation':
        return <FiZap className="w-4 h-4" />;
      case 'script_writing':
        return <div className="w-4 h-4 flex items-center justify-center text-xs font-bold">文</div>;
      case 'storyboard_creation':
        return <FiImage className="w-4 h-4" />;
      case 'video_generation':
        return <FiPlayCircle className="w-4 h-4" />;
      default:
        return <FiZap className="w-4 h-4" />;
    }
  };

  const handleDeleteProject = () => {
    if (window.confirm('确定要删除这个项目吗？此操作不可恢复。')) {
      // 删除项目逻辑
      console.log('删除项目:', id);
    }
  };

  const handleShareProject = () => {
    // 分享项目逻辑
    console.log('分享项目:', id);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面标题和导航 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/projects"
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            <FiArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
            <p className="text-gray-600 mt-1">{project.description}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleShareProject}
            className="btn btn-secondary"
          >
            <FiShare2 className="w-4 h-4 mr-2" />
            分享
          </button>
          <Link
            to={`/projects/${id}/edit`}
            className="btn btn-secondary"
          >
            <FiEdit className="w-4 h-4 mr-2" />
            编辑
          </Link>
          <button
            onClick={handleDeleteProject}
            className="btn btn-danger"
          >
            <FiTrash2 className="w-4 h-4 mr-2" />
            删除
          </button>
        </div>
      </div>

      {/* 项目信息卡片 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">项目概览</h2>
            <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(project.status)}`}>
              {getStatusText(project.status)}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">目标平台</label>
              <p className="text-sm text-gray-900">{getPlatformText(project.platform)}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">目标受众</label>
              <p className="text-sm text-gray-900">{project.target_audience}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">文化背景</label>
              <p className="text-sm text-gray-900">{project.cultural_context}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">项目进度</label>
              <div className="flex items-center space-x-3">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${project.progress}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-gray-700">{project.progress}%</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">{project.ai_tasks_count}</p>
                <p className="text-xs text-gray-600">AI任务总数</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{project.completed_tasks_count}</p>
                <p className="text-xs text-gray-600">已完成任务</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">{project.total_duration}s</p>
                <p className="text-xs text-gray-600">预计总时长</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">¥{project.actual_cost}</p>
                <p className="text-xs text-gray-600">实际成本</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">项目时间线</h2>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">项目创建</p>
                <p className="text-xs text-gray-500">{project.created_at}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">最后更新</p>
                <p className="text-xs text-gray-500">{project.updated_at}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 标签页导航 */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: '概览' },
            { id: 'ai-tasks', name: 'AI任务' },
            { id: 'assets', name: '素材库' },
            { id: 'analytics', name: '分析' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* 标签页内容 */}
      <div className="mt-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">创作指导</h2>
              <div className="space-y-3 text-sm text-gray-600">
                <p>• 确保内容符合目标平台算法偏好</p>
                <p>• 融入中国文化元素，贴近用户生活</p>
                <p>• 开头3秒抓住用户注意力</p>
                <p>• 保持内容原创性和正能量</p>
              </div>
            </div>

            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">成本分析</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">预估成本</span>
                  <span className="text-sm font-medium">¥{project.estimated_cost}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">实际成本</span>
                  <span className="text-sm font-medium text-green-600">¥{project.actual_cost}</span>
                </div>
                <div className="flex justify-between items-center pt-2 border-t border-gray-200">
                  <span className="text-sm font-medium">节省成本</span>
                  <span className="text-sm font-bold text-green-600">¥{project.estimated_cost - project.actual_cost}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ai-tasks' && (
          <div className="space-y-4">
            {aiTasks.map((task) => (
              <div key={task.id} className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-50 rounded-lg">
                      {getTaskTypeIcon(task.type)}
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{getTaskTypeText(task.type)}</h3>
                      <p className="text-sm text-gray-500">{task.id}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(task.status)}`}>
                    {getStatusText(task.status)}
                  </span>
                </div>

                {task.status === 'in_progress' && task.progress && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-gray-600">进度</span>
                      <span className="font-medium">{task.progress.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                  </div>
                )}

                {task.result && (
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">任务结果</h4>
                    <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                      {JSON.stringify(task.result, null, 2)}
                    </pre>
                  </div>
                )}

                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div>
                    创建时间: {task.created_at ? new Date(task.created_at).toLocaleString('zh-CN') : '-'}
                  </div>
                  {task.completed_at && (
                    <div>
                      完成时间: {new Date(task.completed_at).toLocaleString('zh-CN')}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'assets' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {assets.map((asset) => (
              <div key={asset.id} className="card overflow-hidden">
                <img
                  src={asset.thumbnail_url}
                  alt={asset.name}
                  className="w-full h-48 object-cover"
                />
                <div className="p-4">
                  <h3 className="font-medium text-gray-900 mb-2">{asset.name}</h3>
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                    <span>{asset.size}</span>
                    <span>{asset.format.toUpperCase()}</span>
                  </div>
                  <div className="flex space-x-2">
                    <button className="btn btn-secondary text-sm flex-1">
                      <FiEye className="w-4 h-4 mr-1" />
                      预览
                    </button>
                    <button className="btn btn-primary text-sm flex-1">
                      <FiDownload className="w-4 h-4 mr-1" />
                      下载
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">AI使用统计</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">DeepSeek调用次数</span>
                  <span className="text-sm font-medium">12次</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">即梦大模型调用次数</span>
                  <span className="text-sm font-medium">8次</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">总生成内容量</span>
                  <span className="text-sm font-medium">2,340 tokens</span>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">成本分析</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">文本生成成本</span>
                  <span className="text-sm font-medium">¥45.60</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">图像生成成本</span>
                  <span className="text-sm font-medium">¥74.40</span>
                </div>
                <div className="flex justify-between items-center pt-2 border-t border-gray-200">
                  <span className="text-sm font-medium">总成本</span>
                  <span className="text-sm font-bold">¥120.00</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectDetail;