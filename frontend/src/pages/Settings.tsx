import React, { useState } from 'react';
import {
  FiUser,
  FiKey,
  FiBell,
  FiShield,
  FiGlobe,
  FiDatabase,
  FiSave,
  FiRefreshCw,
  FiCheckCircle,
  FiXCircle,
  FiTrash2
} from 'react-icons/fi';

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');

  // 模拟设置数据
  const [profile, setProfile] = useState({
    name: '管理员',
    email: 'admin@example.com',
    phone: '+86 138 0000 0000',
    avatar: '',
    bio: 'AI短视频创作专家'
  });

  const [apiKeys, setApiKeys] = useState({
    deepseek: '',
    jimeng_access_key: '',
    jimeng_secret_key: '',
    wechat_app_id: '',
    wechat_app_secret: ''
  });

  const [notifications, setNotifications] = useState({
    email: true,
    sms: false,
    push: true,
    ai_completion: true,
    system_updates: true
  });

  const [security, setSecurity] = useState({
    two_factor_auth: false,
    login_alerts: true,
    session_timeout: 30,
    password_complexity: 'medium'
  });

  const tabs = [
    { id: 'profile', name: '个人资料', icon: FiUser },
    { id: 'api', name: 'API密钥', icon: FiKey },
    { id: 'notifications', name: '通知设置', icon: FiBell },
    { id: 'security', name: '安全设置', icon: FiShield },
    { id: 'system', name: '系统设置', icon: FiDatabase },
  ];

  const handleSave = async () => {
    setSaveStatus('saving');
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch (error) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 2000);
    }
  };

  const handleTestConnection = async (service: string) => {
    console.log(`测试${service}连接...`);
    // 这里实现连接测试逻辑
  };

  const handlePasswordChange = () => {
    // 这里实现密码修改逻辑
    console.log('修改密码');
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">系统设置</h1>
          <p className="text-gray-600 mt-1">管理您的账户设置和系统配置</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saveStatus === 'saving'}
          className="btn btn-primary"
        >
          {saveStatus === 'saving' ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
              保存中...
            </>
          ) : saveStatus === 'success' ? (
            <>
              <FiCheckCircle className="w-4 h-4 mr-2" />
              已保存
            </>
          ) : saveStatus === 'error' ? (
            <>
              <FiXCircle className="w-4 h-4 mr-2" />
              保存失败
            </>
          ) : (
            <>
              <FiSave className="w-4 h-4 mr-2" />
              保存设置
            </>
          )}
        </button>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* 侧边栏导航 */}
        <div className="lg:w-64">
          <nav className="card p-4 space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                      : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* 设置内容 */}
        <div className="flex-1">
          {activeTab === 'profile' && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">个人资料</h2>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">头像</label>
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
                      <FiUser className="w-8 h-8 text-gray-400" />
                    </div>
                    <button className="btn btn-secondary">
                      上传头像
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">姓名</label>
                  <input
                    type="text"
                    value={profile.name}
                    onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
                    className="form-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile(prev => ({ ...prev, email: e.target.value }))}
                    className="form-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">手机号</label>
                  <input
                    type="tel"
                    value={profile.phone}
                    onChange={(e) => setProfile(prev => ({ ...prev, phone: e.target.value }))}
                    className="form-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">个人简介</label>
                  <textarea
                    value={profile.bio}
                    onChange={(e) => setProfile(prev => ({ ...prev, bio: e.target.value }))}
                    className="form-input h-24"
                    rows={3}
                  />
                </div>
                <button
                  onClick={handlePasswordChange}
                  className="btn btn-secondary"
                >
                  修改密码
                </button>
              </div>
            </div>
          )}

          {activeTab === 'api' && (
            <div className="space-y-6">
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6">DeepSeek API</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">API密钥</label>
                    <input
                      type="password"
                      placeholder="输入DeepSeek API密钥"
                      value={apiKeys.deepseek}
                      onChange={(e) => setApiKeys(prev => ({ ...prev, deepseek: e.target.value }))}
                      className="form-input"
                    />
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => handleTestConnection('DeepSeek')}
                      className="btn btn-secondary"
                    >
                      <FiRefreshCw className="w-4 h-4 mr-2" />
                      测试连接
                    </button>
                    <a
                      href="https://platform.deepseek.com/api_keys"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      获取API密钥
                    </a>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6">即梦大模型 API</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Access Key</label>
                    <input
                      type="password"
                      placeholder="输入即梦Access Key"
                      value={apiKeys.jimeng_access_key}
                      onChange={(e) => setApiKeys(prev => ({ ...prev, jimeng_access_key: e.target.value }))}
                      className="form-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Secret Key</label>
                    <input
                      type="password"
                      placeholder="输入即梦Secret Key"
                      value={apiKeys.jimeng_secret_key}
                      onChange={(e) => setApiKeys(prev => ({ ...prev, jimeng_secret_key: e.target.value }))}
                      className="form-input"
                    />
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => handleTestConnection('即梦')}
                      className="btn btn-secondary"
                    >
                      <FiRefreshCw className="w-4 h-4 mr-2" />
                      测试连接
                    </button>
                    <a
                      href="https://www.volcengine.com/docs"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      获取API密钥
                    </a>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6">微信集成</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">App ID</label>
                    <input
                      type="text"
                      placeholder="输入微信App ID"
                      value={apiKeys.wechat_app_id}
                      onChange={(e) => setApiKeys(prev => ({ ...prev, wechat_app_id: e.target.value }))}
                      className="form-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">App Secret</label>
                    <input
                      type="password"
                      placeholder="输入微信App Secret"
                      value={apiKeys.wechat_app_secret}
                      onChange={(e) => setApiKeys(prev => ({ ...prev, wechat_app_secret: e.target.value }))}
                      className="form-input"
                    />
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => handleTestConnection('微信')}
                      className="btn btn-secondary"
                    >
                      <FiRefreshCw className="w-4 h-4 mr-2" />
                      测试连接
                    </button>
                    <a
                      href="https://mp.weixin.qq.com/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      微信开放平台
                    </a>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">通知设置</h2>
              <div className="space-y-4">
                {Object.entries(notifications).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <label className="flex items-center space-x-3 cursor-pointer flex-1">
                      <input
                        type="checkbox"
                        checked={value}
                        onChange={(e) => setNotifications(prev => ({ ...prev, [key]: e.target.checked }))}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm font-medium text-gray-700">
                        {key === 'email' && '邮件通知'}
                        {key === 'sms' && '短信通知'}
                        {key === 'push' && '推送通知'}
                        {key === 'ai_completion' && 'AI任务完成通知'}
                        {key === 'system_updates' && '系统更新通知'}
                      </span>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6">
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6">安全设置</h2>
                <div className="space-y-4">
                  {Object.entries(security).map(([key, value]) => (
                    key === 'two_factor_auth' || key === 'login_alerts' ? (
                      <div key={key} className="flex items-center justify-between">
                        <label className="flex items-center space-x-3 cursor-pointer flex-1">
                          <input
                            type="checkbox"
                            checked={value as boolean}
                            onChange={(e) => setSecurity(prev => ({ ...prev, [key]: e.target.checked }))}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="text-sm font-medium text-gray-700">
                            {key === 'two_factor_auth' && '双因素认证'}
                            {key === 'login_alerts' && '登录提醒'}
                          </span>
                        </label>
                      </div>
                    ) : null
                  ))}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">会话超时时间（分钟）</label>
                    <select
                      value={security.session_timeout}
                      onChange={(e) => setSecurity(prev => ({ ...prev, session_timeout: parseInt(e.target.value) }))}
                      className="form-input"
                    >
                      <option value={15}>15分钟</option>
                      <option value={30}>30分钟</option>
                      <option value={60}>1小时</option>
                      <option value={120}>2小时</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">密码复杂度</label>
                    <select
                      value={security.password_complexity}
                      onChange={(e) => setSecurity(prev => ({ ...prev, password_complexity: e.target.value }))}
                      className="form-input"
                    >
                      <option value="low">低</option>
                      <option value="medium">中</option>
                      <option value="high">高</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6">登录历史</h2>
                <div className="space-y-3">
                  <div className="flex items-center justify-between py-2 border-b border-gray-100">
                    <div>
                      <p className="text-sm font-medium text-gray-900">当前会话</p>
                      <p className="text-xs text-gray-500">IP: 192.168.1.1 • 浏览器: Chrome</p>
                    </div>
                    <span className="text-xs text-green-600 font-medium">在线</span>
                  </div>
                  <div className="flex items-center justify-between py-2 border-b border-gray-100">
                    <div>
                      <p className="text-sm font-medium text-gray-900">2024-01-15 14:30</p>
                      <p className="text-xs text-gray-500">IP: 192.168.1.2 • 浏览器: Safari</p>
                    </div>
                    <span className="text-xs text-gray-500">已登出</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'system' && (
            <div className="space-y-6">
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6">系统信息</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">系统版本</span>
                      <span className="text-sm font-medium">v1.0.0</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">API版本</span>
                      <span className="text-sm font-medium">v1</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">最后更新</span>
                      <span className="text-sm font-medium">2024-01-15</span>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">数据库状态</span>
                      <span className="text-sm font-medium text-green-600">正常</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Redis状态</span>
                      <span className="text-sm font-medium text-green-600">正常</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">AI服务状态</span>
                      <span className="text-sm font-medium text-green-600">正常</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6">性能监控</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">98.5%</div>
                    <div className="text-sm text-gray-600 mt-1">系统可用性</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">145ms</div>
                    <div className="text-sm text-gray-600 mt-1">平均响应时间</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">1,234</div>
                    <div className="text-sm text-gray-600 mt-1">今日API调用</div>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6">维护操作</h2>
                <div className="flex flex-wrap gap-3">
                  <button className="btn btn-secondary">
                    <FiRefreshCw className="w-4 h-4 mr-2" />
                    清除缓存
                  </button>
                  <button className="btn btn-secondary">
                    <FiDatabase className="w-4 h-4 mr-2" />
                    数据库备份
                  </button>
                  <button className="btn btn-warning">
                    <FiRefreshCw className="w-4 h-4 mr-2" />
                    重启服务
                  </button>
                  <button className="btn btn-danger">
                    <FiTrash2 className="w-4 h-4 mr-2" />
                    清除日志
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;