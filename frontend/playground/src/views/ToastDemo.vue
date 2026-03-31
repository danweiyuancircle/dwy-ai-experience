<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import { toast } from '@danweiyuan/eui'

const position = ref<'top-right' | 'top-center' | 'bottom-right' | 'bottom-center'>('top-right')

function showSuccess() {
  toast.success('操作成功！', { description: '用户数据已保存到数据库。' })
}

function showError() {
  toast.error('操作失败！', { description: '网络连接超时，请稍后重试。' })
}

function showWarning() {
  toast.warning('注意', { description: '此操作不可逆，请谨慎执行。' })
}

function showInfo() {
  toast.info('提示', { description: '您有 3 条未读消息。' })
}

function showPromise() {
  toast.promise(
    new Promise((resolve) => setTimeout(resolve, 2000)),
    {
      loading: '正在处理...',
      success: '处理完成！',
      error: '处理失败',
    },
  )
}

function showCustom() {
  toast('自定义 Toast', {
    description: '这是一个带有自定义操作的 Toast',
    action: {
      label: '撤销',
      onClick: () => toast.success('已撤销操作'),
    },
    duration: 5000,
  })
}
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Toast 轻提示</h1>
    <p class="text-muted-foreground mb-6">全局轻量提示组件，基于 vue-sonner 实现，支持 success / error / warning / info 等类型。</p>

    <!-- EToast 必须在页面中挂载 -->
    <EToast :position="position" rich-colors />

    <DemoBlock
      title="消息类型"
      description="点击按钮触发不同类型的 Toast 通知"
      code='import { toast } from "@danweiyuan/eui"

toast.success("操作成功！")
toast.error("操作失败！")
toast.warning("注意")
toast.info("提示")'
    >
      <div class="flex flex-wrap gap-3">
        <EButton @click="showSuccess">成功 Success</EButton>
        <EButton variant="destructive" @click="showError">错误 Error</EButton>
        <EButton variant="secondary" @click="showWarning">警告 Warning</EButton>
        <EButton variant="outline" @click="showInfo">信息 Info</EButton>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Promise Toast"
      description="自动处理 Promise 的 loading / success / error 状态"
      code='toast.promise(fetchData(), {
  loading: "正在处理...",
  success: "处理完成！",
  error: "处理失败",
})'
    >
      <EButton variant="outline" @click="showPromise">模拟异步操作（2 秒）</EButton>
    </DemoBlock>

    <DemoBlock
      title="带操作按钮"
      description="添加 action 属性显示可点击的操作按钮"
      code='toast("自定义 Toast", {
  action: { label: "撤销", onClick: () => console.log("撤销") },
  duration: 5000,
})'
    >
      <EButton variant="outline" @click="showCustom">带操作按钮的 Toast</EButton>
    </DemoBlock>

    <DemoBlock
      title="Toast 位置"
      description="通过 position 控制 Toast 显示位置"
    >
      <div class="space-y-3">
        <div class="flex flex-wrap gap-2">
          <EButton
            v-for="pos in ['top-right', 'top-center', 'bottom-right', 'bottom-center']"
            :key="pos"
            :variant="position === pos ? 'default' : 'outline'"
            size="sm"
            @click="position = pos as any"
          >
            {{ pos }}
          </EButton>
        </div>
        <EButton @click="showInfo">显示 Toast（当前位置：{{ position }}）</EButton>
      </div>
    </DemoBlock>
  </div>
</template>
