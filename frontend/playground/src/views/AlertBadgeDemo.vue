<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const showDefault = ref(true)
const showDestructive = ref(true)
const showClosable = ref(true)
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Alert & Badge</h1>
    <p class="text-muted-foreground mb-6">Alert 用于展示重要信息，Badge 用于状态标记和数量显示。</p>

    <DemoBlock
      title="Alert 变体"
      description="支持 default 和 destructive 两种样式变体"
      code='<EAlert title="提示" description="这是一条普通提示信息。" />
<EAlert variant="destructive" title="错误" description="操作失败，请检查数据。" />'
    >
      <div class="space-y-3">
        <EAlert title="操作提示" description="您的数据已自动保存，最近保存时间：2 分钟前。" />
        <EAlert variant="destructive" title="操作失败" description="无法连接到服务器，请检查网络连接后重试。" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="可关闭 Alert"
      description="设置 closable 显示关闭按钮"
      code='<EAlert title="提示" description="点击右上角关闭" closable @close="visible = false" />'
    >
      <div class="space-y-3">
        <EAlert
          v-if="showDefault"
          title="信息提示"
          description="这是可以关闭的提示，点击右侧 × 关闭。"
          :closable="true"
          @close="showDefault = false"
        />
        <EAlert
          v-if="showDestructive"
          variant="destructive"
          title="警告信息"
          description="这是可以关闭的错误提示。"
          :closable="true"
          @close="showDestructive = false"
        />
        <div v-if="!showDefault && !showDestructive" class="space-y-2">
          <p class="text-sm text-muted-foreground">所有提示已关闭</p>
          <EButton size="sm" variant="outline" @click="() => { showDefault = true; showDestructive = true }">重新显示</EButton>
        </div>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Badge 变体"
      description="4 种徽标样式：default、secondary、destructive、outline"
      code='<EBadge>默认</EBadge>
<EBadge variant="secondary">次要</EBadge>
<EBadge variant="destructive">危险</EBadge>
<EBadge variant="outline">描边</EBadge>'
    >
      <div class="flex flex-wrap gap-3">
        <EBadge>默认</EBadge>
        <EBadge variant="secondary">次要</EBadge>
        <EBadge variant="destructive">危险</EBadge>
        <EBadge variant="outline">描边</EBadge>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Badge 使用场景"
      description="常见的徽标应用场景"
    >
      <div class="space-y-4">
        <!-- 状态标签 -->
        <div class="flex flex-wrap gap-2">
          <EBadge>在职</EBadge>
          <EBadge variant="secondary">休假</EBadge>
          <EBadge variant="outline">兼职</EBadge>
          <EBadge variant="destructive">离职</EBadge>
        </div>
        <!-- 版本标签 -->
        <div class="flex flex-wrap gap-2">
          <EBadge variant="outline">v1.0.0</EBadge>
          <EBadge variant="secondary">Beta</EBadge>
          <EBadge variant="destructive">弃用</EBadge>
        </div>
        <!-- 与文字组合 -->
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium">未读消息</span>
          <EBadge variant="destructive">12</EBadge>
        </div>
      </div>
    </DemoBlock>
  </div>
</template>
