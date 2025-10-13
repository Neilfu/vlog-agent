import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  FiZap,
  FiImage,
  FiPlayCircle,
  FiFileText,
  FiSend,
  FiClock,
  FiCheckCircle,
  FiXCircle,
  FiRefreshCw,
  FiEye
} from 'react-icons/fi';
import { toast } from 'react-hot-toast';

// API 服务函数
const generateConcept = async (data: any) => {
  const response = await fetch('http://localhost:8000/api/v1/ai/generate/concept', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('生成失败');
  return response.json();
};

const generateScript = async (data: any) => {
  const response = await fetch('http://localhost:8000/api/v1/ai/generate/script', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('生成失败');
  return response.json();
};

const generateStoryboard = async (data: any) => {
  const response = await fetch('http://localhost:8000/api/v1/ai/generate/storyboard', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('生成失败');
  return response.json();
};

const generateVideo = async (data: any) => {
  const response = await fetch('http://localhost:8000/api/v1/ai/generate/video', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('生成失败');
  return response.json();
};

const getTaskStatus = async (taskId: string) => {
  const response = await fetch(`http://localhost:8000/api/v1/ai/tasks/${taskId}/status`);
  if (!response.ok) throw new Error('获取状态失败');
  return response.json();
};

const AIGeneration: React.FC = () => {
  const [activeTab, setActiveTab] = useState('concept');
  const [projectId, setProjectId] = useState('demo-project');
  const [taskResults, setTaskResults] = useState<{[key: string]: any}>({});

  // 表单状态
  const [conceptForm, setConceptForm] = useState({
    prompt: '',
    cultural_context: '',
    platform_target: 'douyin',
    temperature: 0.7,
    max_tokens: 1000
  });

  const [scriptForm, setScriptForm] = useState({
    concept_id: '',
    tone: 'casual',
    target_age_group: '',
    cultural_references: '',
    ai_model: 'deepseek-chat'
  });

  const [storyboardForm, setStoryboardForm] = useState({
    script_scene_ids: '',
    resolution: '1024x1024',
    style: '现代简约',
    color_palette: '',
    ai_model: 'jimeng-4.0'
  });

  const [videoForm, setVideoForm] = useState({
    storyboard_ids: '',
    duration: 6,
    resolution: '1080p',
    frame_rate: 24,
    ai_model: 'jimeng-video-3.0'
  });

  // Mutations
  const conceptMutation = useMutation({
    mutationFn: generateConcept,
    onSuccess: (data) => {
      toast.success('创意概念生成任务已启动');
      setTaskResults(prev => ({ ...prev, [data.task_id]: data }));
      pollTaskStatus(data.task_id);
    },
    onError: (error) => {
      toast.error('创意概念生成失败');
    }
  });

  const scriptMutation = useMutation({
    mutationFn: generateScript,
    onSuccess: (data) => {
      toast.success('剧本生成任务已启动');
      setTaskResults(prev => ({ ...prev, [data.task_id]: data }));
      pollTaskStatus(data.task_id);
    },
    onError: (error) => {
      toast.error('剧本生成失败');
    }
  });

  const storyboardMutation = useMutation({
    mutationFn: generateStoryboard,
    onSuccess: (data) => {
      toast.success('分镜图像生成任务已启动');
      setTaskResults(prev => ({ ...prev, [data.task_id]: data }));
      pollTaskStatus(data.task_id);
    },
    onError: (error) => {
      toast.error('分镜图像生成失败');
    }
  });

  const videoMutation = useMutation({
    mutationFn: generateVideo,
    onSuccess: (data) => {
      toast.success('视频生成任务已启动');
      setTaskResults(prev => ({ ...prev, [data.task_id]: data }));
      pollTaskStatus(data.task_id);
    },
    onError: (error) => {
      toast.error('视频生成失败');
    }
  });

  // 轮询任务状态
  const pollTaskStatus = (taskId: string) => {
    const interval = setInterval(async () => {
      try {
        const status = await getTaskStatus(taskId);
        setTaskResults(prev => ({
          ...prev,
          [taskId]: { ...prev[taskId], ...status }
        }));

        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          if (status.status === 'completed') {
            toast.success('任务完成！');
          } else {
            toast.error('任务失败');
          }
        }
      } catch (error) {
        console.error('获取任务状态失败:', error);
        clearInterval(interval);
      }
    }, 2000);
  };

  const tabs = [
    { id: 'concept', name: '创意概念', icon: FiFileText, color: 'blue' },
    { id: 'script', name: '剧本创作', icon: FiFileText, color: 'green' },
    { id: 'storyboard', name: '分镜图像', icon: FiImage, color: 'purple' },
    { id: 'video', name: '视频生成', icon: FiPlayCircle, color: 'red' },
  ];

  const handleConceptSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    conceptMutation.mutate({
      project_id: projectId,
      ...conceptForm
    });
  };

  const handleScriptSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    scriptMutation.mutate({
      project_id: projectId,
      ...scriptForm,
      cultural_references: scriptForm.cultural_references.split(',').filter(s => s.trim())
    });
  };

  const handleStoryboardSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    storyboardMutation.mutate({
      project_id: projectId,
      ...storyboardForm,
      script_scene_ids: storyboardForm.script_scene_ids.split(',').filter(s => s.trim()),
      color_palette: storyboardForm.color_palette.split(',').filter(s => s.trim())
    });
  };

  const handleVideoSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    videoMutation.mutate({
      project_id: projectId,
      ...videoForm,
      storyboard_ids: videoForm.storyboard_ids.split(',').filter(s => s.trim())
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <FiClock className="w-4 h-4" />;
      case 'in_progress':
        return <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      case 'completed':
        return <FiCheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <FiXCircle className="w-4 h-4 text-red-500" />;
      default:
        return <FiClock className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-600 bg-yellow-50';
      case 'in_progress':
        return 'text-blue-600 bg-blue-50';
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI 内容创作</h1>
          <p className="text-gray-600 mt-1">基于DeepSeek和即梦大模型的智能内容生成</p>
        </div>
      </div>

      {/* 标签页导航 */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? `border-${tab.color}-500 text-${tab.color}-600`
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 表单区域 */}
        <div className="lg:col-span-2">
          {activeTab === 'concept' && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">创意概念生成</h2>
              <form onSubmit={handleConceptSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    创作需求 *</label>
                  <textarea
                    required
                    value={conceptForm.prompt}
                    onChange={(e) => setConceptForm(prev => ({ ...prev, prompt: e.target.value }))}
                    placeholder="例如：为母婴护肤品牌创作温馨的广告创意"
                    className="form-input h-24"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    文化背景 *</label>
                  <textarea
                    required
                    value={conceptForm.cultural_context}
                    onChange={(e) => setConceptForm(prev => ({ ...prev, cultural_context: e.target.value }))}
                    placeholder="例如：中国年轻妈妈注重宝宝健康和安全"
                    className="form-input h-24"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    目标平台 *</label>
                  <select
                    required
                    value={conceptForm.platform_target}
                    onChange={(e) => setConceptForm(prev => ({ ...prev, platform_target: e.target.value }))}
                    className="form-input"
                  >
                    <option value="douyin">抖音</option>
                    <option value="wechat">微信视频号</option>
                    <option value="xiaohongshu">小红书</option>
                    <option value="weibo">微博</option>
                    <option value="bilibili">B站</option>
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      生成温度</label>
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="0.1"
                      value={conceptForm.temperature}
                      onChange={(e) => setConceptForm(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                      className="w-full"
                    />
                    <p className="text-xs text-gray-500 mt-1">{conceptForm.temperature}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      最大Token数</label>
                    <input
                      type="number"
                      min="100"
                      max="4000"
                      value={conceptForm.max_tokens}
                      onChange={(e) => setConceptForm(prev => ({ ...prev, max_tokens: parseInt(e.target.value) }))}
                      className="form-input"
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={conceptMutation.isPending}
                  className="btn btn-primary w-full"
                >
                  {conceptMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <FiZap className="w-4 h-4 mr-2" />
                      生成创意概念
                    </>
                  )}
                </button>
              </form>
            </div>
          )}

          {activeTab === 'script' && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">剧本创作</h2>
              <form onSubmit={handleScriptSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    创意概念ID *</label>
                  <input
                    required
                    type="text"
                    value={scriptForm.concept_id}
                    onChange={(e) => setScriptForm(prev => ({ ...prev, concept_id: e.target.value }))}
                    placeholder="输入创意概念的任务ID"
                    className="form-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    目标年龄群体 *</label>
                  <input
                    required
                    type="text"
                    value={scriptForm.target_age_group}
                    onChange={(e) => setScriptForm(prev => ({ ...prev, target_age_group: e.target.value }))}
                    placeholder="例如：25-35岁年轻妈妈"
                    className="form-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    语调风格</label>
                  <select
                    value={scriptForm.tone}
                    onChange={(e) => setScriptForm(prev => ({ ...prev, tone: e.target.value }))}
                    className="form-input"
                  >
                    <option value="casual">轻松随意</option>
                    <option value="professional">专业权威</option>
                    <option value="humorous">幽默风趣</option>
                    <option value="emotional">情感丰富</option>
                    <option value="trendy">时尚潮流</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    文化引用（用逗号分隔）</label>
                  <input
                    type="text"
                    value={scriptForm.cultural_references}
                    onChange={(e) => setScriptForm(prev => ({ ...prev, cultural_references: e.target.value }))}
                    placeholder="例如：春节，母爱，传统文化"
                    className="form-input"
                  />
                </div>
                <button
                  type="submit"
                  disabled={scriptMutation.isPending}
                  className="btn btn-success w-full"
                >
                  {scriptMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <FiFileText className="w-4 h-4 mr-2" />
                      生成剧本
                    </>
                  )}
                </button>
              </form>
            </div>
          )}

          {activeTab === 'storyboard' && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">分镜图像生成</h2>
              <form onSubmit={handleStoryboardSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    剧本场景ID（用逗号分隔） *</label>
                  <input
                    required
                    type="text"
                    value={storyboardForm.script_scene_ids}
                    onChange={(e) => setStoryboardForm(prev => ({ ...prev, script_scene_ids: e.target.value }))}
                    placeholder="例如：scene-1,scene-2,scene-3"
                    className="form-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    视觉风格 *</label>
                  <input
                    required
                    type="text"
                    value={storyboardForm.style}
                    onChange={(e) => setStoryboardForm(prev => ({ ...prev, style: e.target.value }))}
                    placeholder="例如：现代简约，温馨家庭风格"
                    className="form-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    色彩调色板（用逗号分隔）</label>
                  <input
                    type="text"
                    value={storyboardForm.color_palette}
                    onChange={(e) => setStoryboardForm(prev => ({ ...prev, color_palette: e.target.value }))}
                    placeholder="例如：粉色，绿色，白色"
                    className="form-input"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      分辨率</label>
                    <select
                      value={storyboardForm.resolution}
                      onChange={(e) => setStoryboardForm(prev => ({ ...prev, resolution: e.target.value }))}
                      className="form-input"
                    >
                      <option value="1024x1024">1024x1024</option>
                      <option value="1024x1536">1024x1536</option>
                      <option value="1536x1024">1536x1024</option>
                      <option value="1920x1080">1920x1080</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      模型版本</label>
                    <select
                      value={storyboardForm.ai_model}
                      onChange={(e) => setStoryboardForm(prev => ({ ...prev, ai_model: e.target.value }))}
                      className="form-input"
                    >
                      <option value="jimeng-4.0">即梦 4.0</option>
                      <option value="jimeng-3.5">即梦 3.5</option>
                    </select>
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={storyboardMutation.isPending}
                  className="btn w-full bg-purple-600 hover:bg-purple-700 text-white"
                >
                  {storyboardMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <FiImage className="w-4 h-4 mr-2" />
                      生成分镜图像
                    </>
                  )}
                </button>
              </form>
            </div>
          )}

          {activeTab === 'video' && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">视频生成</h2>
              <form onSubmit={handleVideoSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    分镜ID（用逗号分隔） *</label>
                  <input
                    required
                    type="text"
                    value={videoForm.storyboard_ids}
                    onChange={(e) => setVideoForm(prev => ({ ...prev, storyboard_ids: e.target.value }))}
                    placeholder="例如：image-1,image-2,image-3"
                    className="form-input"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      视频时长（秒）</label>
                    <input
                      type="number"
                      min="5"
                      max="30"
                      value={videoForm.duration}
                      onChange={(e) => setVideoForm(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
                      className="form-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      分辨率</label>
                    <select
                      value={videoForm.resolution}
                      onChange={(e) => setVideoForm(prev => ({ ...prev, resolution: e.target.value }))}
                      className="form-input"
                    >
                      <option value="720p">720p</option>
                      <option value="1080p">1080p</option>
                      <option value="1440p">1440p</option>
                      <option value="4K">4K</option>
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      帧率</label>
                    <input
                      type="number"
                      min="24"
                      max="60"
                      value={videoForm.frame_rate}
                      onChange={(e) => setVideoForm(prev => ({ ...prev, frame_rate: parseInt(e.target.value) }))}
                      className="form-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      模型版本</label>
                    <select
                      value={videoForm.ai_model}
                      onChange={(e) => setVideoForm(prev => ({ ...prev, ai_model: e.target.value }))}
                      className="form-input"
                    >
                      <option value="jimeng-video-3.0">即梦视频 3.0</option>
                      <option value="jimeng-video-2.5">即梦视频 2.5</option>
                    </select>
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={videoMutation.isPending}
                  className="btn w-full bg-red-600 hover:bg-red-700 text-white"
                >
                  {videoMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <FiPlayCircle className="w-4 h-4 mr-2" />
                      生成视频
                    </>
                  )}
                </button>
              </form>
            </div>
          )}
        </div>

        {/* 任务状态区域 */}
        <div className="space-y-4">
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">任务状态</h2>
            <div className="space-y-3">
              {Object.entries(taskResults).map(([taskId, task]) => (
                <div key={taskId} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(task.status)}
                      <span className="text-sm font-medium">{taskId.substring(0, 8)}...</span>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(task.status)}`}>
                      {task.status}
                    </span>
                  </div>
                  {task.status === 'in_progress' && task.progress && (
                    <div className="mb-2">
                      <div className="w-full bg-gray-200 rounded-full h-2"
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{task.progress.toFixed(1)}% 完成</p>
                    </div>
                  )}
                  {task.result && (
                    <div className="text-xs text-gray-600">
                      <pre className="whitespace-pre-wrap max-h-32 overflow-y-auto">
                        {JSON.stringify(task.result, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ))}
              {Object.keys(taskResults).length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <FiZap className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>暂无任务记录</p>
                  <p className="text-sm">提交表单后开始AI生成任务</p>
                </div>
              )}
            </div>
          </div>

          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">创作提示</h2>
            <div className="space-y-3 text-sm text-gray-600">
              <p>• 确保内容符合中国法律法规</p>
              <p>• 融入中国文化元素，贴近用户生活</p>
              <p>• 开头3秒抓住用户注意力</p>
              <p>• 保持内容原创性和正能量</p>
              <p>• 考虑目标平台的算法偏好</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIGeneration;