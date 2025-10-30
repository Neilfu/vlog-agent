import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  FiUpload,
  FiImage,
  FiVideo,
  FiFileText,
  FiDownload,
  FiTrash2,
  FiEye,
  FiSearch,
  FiFilter,
  FiFolder,
  FiClock,
  FiMoreVertical
} from 'react-icons/fi';

const Assets: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // 模拟素材数据
  const assets = [
    {
      id: '1',
      name: '春季花朵背景.jpg',
      type: 'image',
      size: '2.5 MB',
      format: 'jpg',
      dimensions: '1920x1080',
      created_at: '2024-01-15T10:30:00Z',
      thumbnail_url: 'https://picsum.photos/300/200?random=1',
      url: 'https://picsum.photos/1920/1080?random=1',
      tags: ['春季', '花朵', '背景', '自然'],
      ai_generated: false
    },
    {
      id: '2',
      name: '宝宝护肤场景1.jpg',
      type: 'image',
      size: '3.1 MB',
      format: 'jpg',
      dimensions: '1024x1024',
      created_at: '2024-01-15T11:30:00Z',
      thumbnail_url: 'https://picsum.photos/300/200?random=2',
      url: 'https://picsum.photos/1024/1024?random=2',
      tags: ['宝宝', '护肤', '温馨', '生活'],
      ai_generated: true,
      ai_model: 'jimeng-4.0'
    },
    {
      id: '3',
      name: '产品展示视频.mp4',
      type: 'video',
      size: '15.7 MB',
      format: 'mp4',
      duration: '0:30',
      dimensions: '1080x1920',
      created_at: '2024-01-14T14:20:00Z',
      thumbnail_url: 'https://picsum.photos/300/200?random=3',
      url: 'https://picsum.photos/1080/1920?random=3',
      tags: ['产品', '展示', '竖屏', '商业'],
      ai_generated: true,
      ai_model: 'jimeng-video-3.0'
    },
    {
      id: '4',
      name: '品牌文案.txt',
      type: 'document',
      size: '12.3 KB',
      format: 'txt',
      created_at: '2024-01-13T09:15:00Z',
      thumbnail_url: 'https://picsum.photos/300/200?random=4',
      url: '#',
      tags: ['文案', '品牌', '文字'],
      ai_generated: true,
      ai_model: 'deepseek-chat'
    },
    {
      id: '5',
      name: '温馨家庭场景.jpg',
      type: 'image',
      size: '4.2 MB',
      format: 'jpg',
      dimensions: '1536x1024',
      created_at: '2024-01-12T16:45:00Z',
      thumbnail_url: 'https://picsum.photos/300/200?random=5',
      url: 'https://picsum.photos/1536/1024?random=5',
      tags: ['家庭', '温馨', '生活', '情感'],
      ai_generated: true,
      ai_model: 'jimeng-4.0'
    },
    {
      id: '6',
      name: '教程演示视频.mp4',
      type: 'video',
      size: '28.9 MB',
      format: 'mp4',
      duration: '1:15',
      dimensions: '1920x1080',
      created_at: '2024-01-11T11:20:00Z',
      thumbnail_url: 'https://picsum.photos/300/200?random=6',
      url: 'https://picsum.photos/1920/1080?random=6',
      tags: ['教程', '演示', '教育', '横屏'],
      ai_generated: false
    }
  ];

  const onDrop = (acceptedFiles: File[]) => {
    console.log('上传文件:', acceptedFiles);
    // 这里实现文件上传逻辑
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
      'video/*': ['.mp4', '.mov', '.avi', '.mkv'],
      'text/*': ['.txt', '.md', '.doc', '.docx']
    }
  });

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'image':
        return <FiImage className="w-8 h-8" />;
      case 'video':
        return <FiVideo className="w-8 h-8" />;
      case 'document':
        return <FiFileText className="w-8 h-8" />;
      default:
        return <FiFolder className="w-8 h-8" />;
    }
  };

  const getFileColor = (type: string) => {
    switch (type) {
      case 'image':
        return 'text-blue-600 bg-blue-50';
      case 'video':
        return 'text-green-600 bg-green-50';
      case 'document':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-purple-600 bg-purple-50';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         asset.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = filterType === 'all' || asset.type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">素材库</h1>
          <p className="text-gray-600 mt-1">管理和组织您的图片、视频和文档素材</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            className="btn btn-secondary"
          >
            {viewMode === 'grid' ? '列表视图' : '网格视图'}
          </button>
        </div>
      </div>

      {/* 上传区域 */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center space-y-4">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
            <FiUpload className="w-8 h-8 text-gray-400" />
          </div>
          <div>
            <p className="text-lg font-medium text-gray-900">
              {isDragActive ? '释放文件以上传' : '拖拽文件到此处上传'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              支持图片、视频和文档文件，或点击选择文件
            </p>
          </div>
          <button type="button" className="btn btn-primary">
            选择文件
          </button>
        </div>
      </div>

      {/* 搜索和筛选 */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="搜索素材名称或标签..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-input pl-10"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="form-input"
          >
            <option value="all">所有类型</option>
            <option value="image">图片</option>
            <option value="video">视频</option>
            <option value="document">文档</option>
          </select>
        </div>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-gray-900">{filteredAssets.length}</div>
          <div className="text-sm text-gray-600 mt-1">总素材数</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">{filteredAssets.filter(a => a.type === 'image').length}</div>
          <div className="text-sm text-gray-600 mt-1">图片素材</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-green-600">{filteredAssets.filter(a => a.type === 'video').length}</div>
          <div className="text-sm text-gray-600 mt-1">视频素材</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">{filteredAssets.filter(a => a.ai_generated).length}</div>
          <div className="text-sm text-gray-600 mt-1">AI生成素材</div>
        </div>
      </div>

      {/* 素材列表 */}
      <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' : 'space-y-4'}>
        {filteredAssets.map((asset) => (
          <div key={asset.id} className={`card overflow-hidden ${viewMode === 'list' ? 'flex' : ''}`}>
            {viewMode === 'grid' ? (
              <>
                <img
                  src={asset.thumbnail_url}
                  alt={asset.name}
                  className="w-full h-48 object-cover"
                />
                <div className="p-4">
                  <h3 className="font-medium text-gray-900 mb-2 truncate">{asset.name}</h3>
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                    <span>{asset.size}</span>
                    <span>{asset.format.toUpperCase()}</span>
                  </div>
                  {asset.ai_generated && (
                    <div className="mb-3">
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded-full">
                        AI生成 - {asset.ai_model}
                      </span>
                    </div>
                  )}
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
              </>
            ) : (
              <>
                <img
                  src={asset.thumbnail_url}
                  alt={asset.name}
                  className="w-24 h-24 object-cover flex-shrink-0"
                />
                <div className="flex-1 p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">{asset.name}</h3>
                      <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                        <span>{asset.size}</span>
                        {asset.dimensions && <span>{asset.dimensions}</span>}
                        {asset.duration && <span>{asset.duration}</span>}
                        <span>{asset.format.toUpperCase()}</span>
                      </div>
                      <div className="flex items-center space-x-2 mt-2">
                        {asset.ai_generated && <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded-full">AI生成</span>}
                        <span className="text-xs text-gray-400">{formatDate(asset.created_at)}</span>
                      </div>
                      {asset.tags.length > 0 && <div className="flex flex-wrap gap-1 mt-2">
                        {asset.tags.slice(0, 3).map((tag, index) => (
                          <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                            {tag}
                          </span>
                        ))}
                        {asset.tags.length > 3 && <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{asset.tags.length - 3}
                        </span>}
                      </div>}
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                        <FiEye className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                        <FiDownload className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                        <FiTrash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        ))}
      </div>

      {filteredAssets.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FiImage className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">没有找到素材</h3>
          <p className="text-gray-600 mb-4">尝试调整搜索条件或上传新素材</p>
          <button className="btn btn-primary">
            上传素材
          </button>
        </div>
      )}
    </div>
  );
};

export default Assets;