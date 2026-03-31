<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const confirmOpen = ref(false)
const confirmWarningOpen = ref(false)
const confirmErrorOpen = ref(false)
const confirmResult = ref('')
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">EConfirmDialog 确认对话框</h1>
    <p class="text-muted-foreground mb-6">支持 info / warning / error 三种危险等级。</p>

    <DemoBlock
      title="EConfirmDialog 确认对话框"
      description="支持 info / warning / error 三种危险等级"
      code='<EConfirmDialog
  v-model:open="open"
  type="warning"
  title="确认删除"
  message="此操作不可逆，确定要删除吗？"
  @confirm="handleConfirm"
/>'
    >
      <div class="flex flex-wrap gap-3">
        <EButton variant="outline" @click="confirmOpen = true">信息确认</EButton>
        <EButton variant="secondary" @click="confirmWarningOpen = true">警告确认</EButton>
        <EButton variant="destructive" @click="confirmErrorOpen = true">危险确认</EButton>
      </div>
      <p v-if="confirmResult" class="text-sm mt-2 text-muted-foreground">操作结果：{{ confirmResult }}</p>

      <EConfirmDialog
        v-model:open="confirmOpen"
        type="info"
        title="确认操作"
        message="您确定要执行此操作吗？这将影响所有相关数据。"
        @confirm="() => { confirmResult = '点击了确认（info）'; confirmOpen = false }"
        @cancel="() => { confirmResult = '点击了取消'; confirmOpen = false }"
      />
      <EConfirmDialog
        v-model:open="confirmWarningOpen"
        type="warning"
        title="注意"
        message="此操作将清空所有缓存数据，确定继续吗？"
        confirm-text="继续"
        @confirm="() => { confirmResult = '点击了继续（warning）'; confirmWarningOpen = false }"
        @cancel="() => { confirmResult = '点击了取消'; confirmWarningOpen = false }"
      />
      <EConfirmDialog
        v-model:open="confirmErrorOpen"
        type="error"
        title="危险操作"
        message="此操作将永久删除所有数据，无法恢复。请确认您已知晓此风险。"
        confirm-text="我已知晓，继续删除"
        cancel-text="取消"
        @confirm="() => { confirmResult = '点击了删除（error）'; confirmErrorOpen = false }"
        @cancel="() => { confirmResult = '点击了取消'; confirmErrorOpen = false }"
      />
    </DemoBlock>
  </div>
</template>
