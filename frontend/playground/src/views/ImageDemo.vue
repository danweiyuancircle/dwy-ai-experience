<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'fit', label: '填充模式' },
  { id: 'fallback', label: '加载失败' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'src', type: 'string', description: '图片地址' },
  { name: 'alt', type: 'string', description: '图片替代文本' },
  { name: 'fit', type: "'contain' | 'cover' | 'fill' | 'none' | 'scale-down'", default: "'cover'", description: '图片填充模式，对应 CSS object-fit' },
  { name: 'lazy', type: 'boolean', default: 'false', description: '是否懒加载，进入视口后才加载图片' },
  { name: 'fallback', type: 'string', description: '加载失败时的回退图片地址' },
  { name: 'preview', type: 'boolean', default: 'false', description: '是否支持点击预览大图' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '默认内容（组件内部使用）' },
]

const sampleImage = 'https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=800&dpr=2&q=80'
const fallbackImage = 'https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=800&dpr=2&q=80'

const fitModes = ['contain', 'cover', 'fill', 'none', 'scale-down'] as const
</script>

<template>
  <ComponentDoc
    title="Image 图片"
    description="增强的图片组件，支持懒加载、加载失败回退、多种填充模式和点击预览大图。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要图片加载优化的场景，如商品列表懒加载、用户上传图片预览、图库浏览等。提供加载骨架屏、失败回退和预览放大等开箱即用的能力。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="基础图片展示，支持点击预览大图"
        code='<EImage
  :src="imageUrl"
  alt="示例图片"
  preview
  class="w-60 h-40 rounded-lg"
/>'
      >
        <EImage
          :src="sampleImage"
          alt="示例图片"
          preview
          class="w-60 h-40 rounded-lg"
        />
      </DemoBlock>
    </section>

    <section id="fit">
      <DemoBlock
        title="填充模式"
        description="5 种 object-fit 模式：contain、cover、fill、none、scale-down"
        code='<EImage :src="imageUrl" fit="contain" class="w-40 h-40" />'
      >
        <div class="flex flex-wrap gap-4">
          <div v-for="mode in fitModes" :key="mode" class="text-center space-y-2">
            <EImage
              :src="sampleImage"
              :alt="`${mode} 模式`"
              :fit="mode"
              class="w-32 h-32 rounded-lg border"
            />
            <p class="text-xs text-muted-foreground font-mono">{{ mode }}</p>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="fallback">
      <DemoBlock
        title="加载失败"
        description="图片加载失败时显示回退图片或默认占位符"
        code='<EImage src="invalid-url.jpg" :fallback="fallbackUrl" class="w-40 h-40" />'
      >
        <div class="flex flex-wrap gap-4">
          <div class="text-center space-y-2">
            <EImage
              src="https://invalid-url-that-will-fail.jpg"
              alt="无回退图"
              class="w-32 h-32 rounded-lg border"
            />
            <p class="text-xs text-muted-foreground">无回退（默认占位）</p>
          </div>
          <div class="text-center space-y-2">
            <EImage
              src="https://invalid-url-that-will-fail.jpg"
              alt="有回退图"
              :fallback="fallbackImage"
              class="w-32 h-32 rounded-lg border"
            />
            <p class="text-xs text-muted-foreground">有回退图片</p>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
