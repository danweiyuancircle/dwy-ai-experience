<script setup lang="ts">
const modules = [
  { name: 'config', title: 'Config', desc: 'Pydantic Settings + environment（dev/prod）', path: '/eapi/config' },
  { name: 'database', title: 'Database', desc: '异步 SQLAlchemy 引擎、会话、模型基类', path: '/eapi/database' },
  { name: 'security', title: 'Security', desc: 'JWT 签发/解码 + bcrypt 密码哈希', path: '/eapi/security' },
  { name: 'exceptions', title: 'Exceptions', desc: '统一异常体系，自动映射 HTTP 状态码', path: '/eapi/exceptions' },
  { name: 'response', title: 'Response', desc: 'ApiResponse.ok / page 统一信封', path: '/eapi/response' },
  { name: 'pagination', title: 'Pagination', desc: '分页参数解析与 offset/limit 转换', path: '/eapi/pagination' },
  { name: 'cache', title: 'Cache', desc: '异步 Redis 连接管理', path: '/eapi/cache' },
  { name: 'dependencies', title: 'Dependencies', desc: 'FastAPI 依赖注入工厂', path: '/eapi/dependencies' },
  { name: 'logger', title: 'Logger', desc: 'loguru 全局日志 + 轮转', path: '/eapi/logger' },
  { name: 'health', title: 'Health', desc: '只探活健康检查路由工厂', path: '/eapi/health' },
  { name: 'masking', title: 'Masking', desc: 'PII 数据脱敏工具', path: '/eapi/masking' },
  { name: 'dt', title: 'dt', desc: 'Asia/Shanghai 时间工具唯一入口', path: '/eapi/dt' },
  { name: 'tasks', title: 'Tasks', desc: 'ARQ 异步任务（需 [tasks] extra）', path: '/eapi/tasks' },
  { name: 'email', title: 'Email', desc: '邮件验证码 Provider（需 email extra）', path: '/eapi/email' },
]
</script>

<template>
  <div class="max-w-4xl">
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">dwyeapi</h1>
      <p class="text-muted-foreground text-lg">
        FastAPI 基础设施包，Python 3.11+，全异步。核心模块 + tasks / providers 可选扩展。
      </p>
    </div>

    <!-- Install -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">安装</h2>
      <ECard>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>pip install dwyeapi
# 可选
pip install "dwyeapi[tasks]"
pip install "dwyeapi[email]"
# 或
uv add dwyeapi</code></pre>
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
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>from dwyeapi import ApiResponse, PageData, BaseSettings, is_dev, logger, health
from dwyeapi.database import Base, TimestampMixin, create_async_engine_factory, create_session_factory
from dwyeapi.security import hash_password, verify_password, create_token, decode_token
from dwyeapi.exceptions import NotFoundError, BusinessError, register_exception_handlers
from dwyeapi.pagination import PaginationParams, paginate
from dwyeapi.cache import configure as configure_redis, get_redis, close_redis
from dwyeapi.dependencies import create_get_db
from dwyeapi import dt, masking</code></pre>
      </ECard>
    </div>
  </div>
</template>
