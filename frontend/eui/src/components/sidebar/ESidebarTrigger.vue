<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { PanelLeft } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { EButton } from '@/components/button'
import { useSidebar } from './utils'

const props = defineProps<{ class?: HTMLAttributes['class'] }>()
const { toggleSidebar } = useSidebar()
</script>

<template>
  <EButton
    data-sidebar="trigger"
    data-slot="sidebar-trigger"
    variant="ghost"
    size="icon"
    :class="cn('h-7 w-7', props.class)"
    @click="toggleSidebar"
  >
    <PanelLeft />
    <span class="sr-only">Toggle Sidebar</span>
  </EButton>
</template>
