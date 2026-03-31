<script setup lang="ts">
const modules = [
  { name: 'config', title: 'Config', desc: 'Pydantic Settings 配置管理，自动读取 .env', path: '/backend/config' },
  { name: 'database', title: 'Database', desc: '异步 SQLAlchemy 引擎、会话、模型基类', path: '/backend/database' },
  { name: 'security', title: 'Security', desc: 'JWT 签发/解码 + bcrypt 密码哈希', path: '/backend/security' },
  { name: 'exceptions', title: 'Exceptions', desc: '统一异常体系，自动映射 HTTP 状态码', path: '/backend/exceptions' },
  { name: 'response', title: 'Response', desc: '统一响应格式 success / fail / paginated', path: '/backend/response' },
  { name: 'pagination', title: 'Pagination', desc: '分页参数解析与 offset/limit 转换', path: '/backend/pagination' },
  { name: 'cache', title: 'Cache', desc: '异步 Redis 连接管理', path: '/backend/cache' },
  { name: 'dependencies', title: 'Dependencies', desc: 'FastAPI 依赖注入工厂', path: '/backend/dependencies' },
]
</script>

<template>
  <div class="max-w-4xl">
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">danweiyuan-base</h1>
      <p class="text-muted-foreground text-lg">
        FastAPI 基础设施包，Python 3.11+，全异步。8 个扁平模块，无子包。
      </p>
    </div>

    <!-- Install -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">安装</h2>
      <ECard>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>pip install danweiyuan-base
# 或
uv add danweiyuan-base</code></pre>
      </ECard>
    </div>

    <!-- Modules -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">模块一览</h2>
      <div class="grid grid-cols-2 gap-3">
        <router-link
          v-for="mod in modules"
          :key="mod.name"
          :to="mod.path"
        >
          <ECard class="h-full hover:bg-accent transition-colors cursor-pointer">
            <div class="font-medium mb-1">{{ mod.title }}</div>
            <div class="text-sm text-muted-foreground">{{ mod.desc }}</div>
          </ECard>
        </router-link>
      </div>
    </div>

    <!-- Quick Import -->
    <div>
      <h2 class="text-xl font-semibold mb-4">快速导入</h2>
      <ECard>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>from danweiyuan_base.config import BaseSettings
from danweiyuan_base.database import Base, TimestampMixin, create_async_engine_factory, create_session_factory
from danweiyuan_base.security import hash_password, verify_password, create_token, decode_token
from danweiyuan_base.exceptions import NotFoundError, BusinessError, register_exception_handlers
from danweiyuan_base.response import success, fail, paginated
from danweiyuan_base.pagination import PaginationParams, paginate
from danweiyuan_base.cache import configure as configure_redis, get_redis, close_redis
from danweiyuan_base.dependencies import create_get_db</code></pre>
      </ECard>
    </div>
  </div>
</template>
