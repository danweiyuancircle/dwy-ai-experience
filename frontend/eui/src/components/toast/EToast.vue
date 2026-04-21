<!--
  EToast 全局消息通知容器
  基于 vue-sonner 封装，需在 App 根节点放置一次；实际调用通过 useToast composable 触发
  自定义了五种语义图标以及关闭图标，使用 lucide 保持与 EUI 视觉统一
-->
<script setup lang="ts">
import {
  CircleCheck,
  Info,
  LoaderCircle,
  OctagonX,
  TriangleAlert,
  X,
} from 'lucide-vue-next'
import { Toaster as Sonner } from 'vue-sonner'
import 'vue-sonner/style.css'
import { reactiveOmit } from '@vueuse/core'
import { cn } from '@/utils/cn'
import type { EToastProps } from './types'

const props = defineProps<EToastProps>()
const delegatedProps = reactiveOmit(props, 'class')
</script>

<template>
  <Sonner
    :class="cn('toaster group', props.class)"
    :style="{
      '--normal-bg': 'var(--popover)',
      '--normal-text': 'var(--popover-foreground)',
      '--normal-border': 'var(--border)',
      '--border-radius': 'var(--radius)',
    }"
    v-bind="delegatedProps"
  >
    <template #success-icon>
      <CircleCheck class="size-4" />
    </template>
    <template #info-icon>
      <Info class="size-4" />
    </template>
    <template #warning-icon>
      <TriangleAlert class="size-4" />
    </template>
    <template #error-icon>
      <OctagonX class="size-4" />
    </template>
    <template #loading-icon>
      <div>
        <LoaderCircle class="size-4 animate-spin" />
      </div>
    </template>
    <template #close-icon>
      <X class="size-4" />
    </template>
  </Sonner>
</template>
