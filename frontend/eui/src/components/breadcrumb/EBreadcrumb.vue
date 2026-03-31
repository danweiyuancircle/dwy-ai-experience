<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { EBreadcrumbProps } from './types'

const props = withDefaults(defineProps<EBreadcrumbProps>(), {
  items: () => [],
})
</script>

<template>
  <nav
    aria-label="breadcrumb"
    data-slot="breadcrumb"
    :class="props.class"
  >
    <ol
      data-slot="breadcrumb-list"
      :class="cn('text-muted-foreground flex flex-wrap items-center gap-1.5 text-sm break-words sm:gap-2.5')"
    >
      <template v-for="(item, index) in items" :key="index">
        <!-- Separator (before every item except the first) -->
        <li
          v-if="index > 0"
          data-slot="breadcrumb-separator"
          role="presentation"
          aria-hidden="true"
          :class="cn('[&>svg]:size-3.5')"
        >
          <slot name="separator">
            <ChevronRight v-if="!separator" />
            <span v-else>{{ separator }}</span>
          </slot>
        </li>

        <!-- Last item: plain text (current page) -->
        <li
          v-if="index === items.length - 1"
          data-slot="breadcrumb-item"
          :class="cn('inline-flex items-center gap-1.5')"
        >
          <component :is="item.icon" v-if="item.icon" class="size-4" />
          <span
            data-slot="breadcrumb-page"
            role="link"
            aria-disabled="true"
            aria-current="page"
            :class="cn('text-foreground font-normal')"
          >
            {{ item.label }}
          </span>
        </li>

        <!-- Non-last items: links -->
        <li
          v-else
          data-slot="breadcrumb-item"
          :class="cn('inline-flex items-center gap-1.5')"
        >
          <component :is="item.icon" v-if="item.icon" class="size-4" />
          <a
            v-if="item.href"
            data-slot="breadcrumb-link"
            :href="item.href"
            :class="cn('hover:text-foreground transition-colors')"
          >
            {{ item.label }}
          </a>
          <span
            v-else
            data-slot="breadcrumb-link"
            :class="cn('hover:text-foreground transition-colors cursor-default')"
          >
            {{ item.label }}
          </span>
        </li>
      </template>
    </ol>
  </nav>
</template>
