<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import { useMessage } from '@dwydev/eui'

const message = useMessage()

function showSuccess() {
  message.success('操作成功')
}

function showError() {
  message.error('操作失败')
}

function showWarning() {
  message.warning('注意：此操作不可逆')
}

function showInfo() {
  message.info('您有 3 条未读消息')
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'types', label: '消息类型' },
]
</script>

<template>
  <ComponentDoc
    title="Message 轻提示"
    description="命令式顶部轻提示。走 useMessage，不要用已删除的 useToast。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">
        操作后的全局反馈：提交成功、请求失败、警告。不阻断操作。命令式调用，不必在页面挂容器。
      </p>
    </section>

    <section id="types">
      <DemoBlock
        title="消息类型"
        description="success / error / warning / info"
        code='import { useMessage } from "@dwydev/eui"

const message = useMessage()
message.success("操作成功")
message.error("操作失败")
message.warning("注意")
message.info("提示")'
      >
        <div class="flex flex-wrap gap-3">
          <EButton @click="showSuccess">成功 Success</EButton>
          <EButton variant="destructive" @click="showError">错误 Error</EButton>
          <EButton variant="secondary" @click="showWarning">警告 Warning</EButton>
          <EButton variant="outline" @click="showInfo">信息 Info</EButton>
        </div>
      </DemoBlock>
    </section>
  </ComponentDoc>
</template>
