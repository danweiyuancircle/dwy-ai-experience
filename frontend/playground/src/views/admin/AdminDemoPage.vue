<!--
  Admin 预览占位页
  展示 meta.title / description；真实业务替换为 feature 页面。
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ECard } from '@dwydev/eui'

const route = useRoute()
const title = computed(() =>
  typeof route.meta.title === 'string' ? route.meta.title : route.path,
)
const description = computed(() =>
  typeof route.meta.description === 'string' ? route.meta.description : '',
)
</script>

<template>
  <div class="space-y-4">
    <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <ECard class="gap-2 py-4 shadow-xs">
        <div class="px-6 text-xs text-muted-foreground">
          当前路由
        </div>
        <div class="px-6 font-mono text-sm">
          {{ route.path }}
        </div>
      </ECard>
      <ECard class="gap-2 py-4 shadow-xs">
        <div class="px-6 text-xs text-muted-foreground">
          meta.title
        </div>
        <div class="px-6 text-sm font-medium">
          {{ title }}
        </div>
      </ECard>
      <ECard class="gap-2 py-4 shadow-xs">
        <div class="px-6 text-xs text-muted-foreground">
          UI 底座
        </div>
        <div class="px-6 text-sm font-medium">
          @dwydev/eui
        </div>
      </ECard>
      <ECard class="gap-2 py-4 shadow-xs">
        <div class="px-6 text-xs text-muted-foreground">
          扩展方式
        </div>
        <div class="px-6 text-sm font-medium">
          defineAdminModule
        </div>
      </ECard>
    </div>

    <ECard
      class="shadow-xs"
      :title="`${title} · 业务内容区`"
      :description="description || '此区域是 router-view。骨架只用 eui：EAdminLayout / EButton / EDropdown / EPopover / EAvatar / ECard。'"
    >
      <ul class="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
        <li>侧栏菜单来自 eui EMenu（rounded-md 菜单项）</li>
        <li>顶栏按钮来自 eui EButton（rounded-md）</li>
        <li>卡片来自 eui ECard（rounded-xl）</li>
        <li>主题 / 通知 / 用户下拉均为 eui 原语组合</li>
      </ul>
    </ECard>
  </div>
</template>
