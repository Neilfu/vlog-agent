#!/usr/bin/env python3
"""
权限系统初始化脚本
Permission System Initialization Script

用于初始化权限系统，创建默认权限和角色
Used to initialize the permission system, create default permissions and roles
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import init_db, get_db
from app.services.permissions import init_permissions_system
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger


async def main():
    """主函数 - 初始化权限系统"""
    try:
        logger.info("开始初始化权限系统...")

        # 初始化数据库连接
        await init_db()
        logger.info("✅ 数据库连接初始化成功")

        # 获取数据库会话
        async for db in get_db():
            try:
                # 初始化权限系统
                await init_permissions_system(db)
                logger.info("✅ 权限系统初始化成功")
                break
            except Exception as e:
                logger.error(f"❌ 权限系统初始化失败: {str(e)}")
                raise
            finally:
                await db.close()

        logger.info("🎉 权限系统初始化完成！")

    except Exception as e:
        logger.error(f"❌ 初始化过程失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())