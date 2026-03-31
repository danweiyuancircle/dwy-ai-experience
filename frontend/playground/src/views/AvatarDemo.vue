<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Avatar 头像</h1>
    <p class="text-muted-foreground mb-6">用户头像组件，支持图片显示、文字 fallback 和多种尺寸。</p>

    <DemoBlock
      title="图片头像"
      description="通过 src 设置头像图片"
      code='<EAvatar src="https://github.com/shadcn.png" alt="用户头像" />'
    >
      <div class="flex items-center gap-4">
        <EAvatar src="https://i.pravatar.cc/150?img=1" alt="用户 1" />
        <EAvatar src="https://i.pravatar.cc/150?img=5" alt="用户 2" />
        <EAvatar src="https://i.pravatar.cc/150?img=10" alt="用户 3" />
        <EAvatar src="https://i.pravatar.cc/150?img=15" alt="用户 4" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="文字 Fallback"
      description="图片加载失败时显示 fallback 文字（通常为姓名首字母）"
      code='<EAvatar fallback="张三" alt="张三" />
<EAvatar fallback="李" alt="李四" />'
    >
      <div class="flex items-center gap-4">
        <EAvatar fallback="张" alt="张三" />
        <EAvatar fallback="李四" alt="李四" />
        <EAvatar fallback="王" alt="王五" />
        <EAvatar src="/invalid-url.jpg" fallback="陈" alt="陈六" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="尺寸变体"
      description="支持 sm / default / lg 三种尺寸"
      code='<EAvatar size="sm" fallback="小" />
<EAvatar fallback="默" />
<EAvatar size="lg" fallback="大" />'
    >
      <div class="flex items-end gap-4">
        <div class="flex flex-col items-center gap-1">
          <EAvatar size="sm" src="https://i.pravatar.cc/150?img=3" alt="小" />
          <span class="text-xs text-muted-foreground">sm</span>
        </div>
        <div class="flex flex-col items-center gap-1">
          <EAvatar src="https://i.pravatar.cc/150?img=3" alt="默认" />
          <span class="text-xs text-muted-foreground">default</span>
        </div>
        <div class="flex flex-col items-center gap-1">
          <EAvatar size="lg" src="https://i.pravatar.cc/150?img=3" alt="大" />
          <span class="text-xs text-muted-foreground">lg</span>
        </div>
      </div>
    </DemoBlock>

    <DemoBlock
      title="头像组合（常见场景）"
      description="头像与用户信息组合显示"
    >
      <div class="space-y-3">
        <div v-for="user in [
          { name: '张三', role: '管理员', img: 'https://i.pravatar.cc/150?img=1' },
          { name: '李四', role: '编辑员', img: 'https://i.pravatar.cc/150?img=5' },
          { name: '王五', role: '访客', fallback: '王' },
        ]" :key="user.name" class="flex items-center gap-3 p-3 border rounded-md">
          <EAvatar :src="user.img" :fallback="user.fallback || user.name[0]" :alt="user.name" />
          <div>
            <p class="text-sm font-medium">{{ user.name }}</p>
            <p class="text-xs text-muted-foreground">{{ user.role }}</p>
          </div>
        </div>
      </div>
    </DemoBlock>
  </div>
</template>
