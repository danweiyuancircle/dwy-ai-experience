<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'ratios', label: '常用比例' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'ratio', type: 'number', default: '16/9', description: '宽高比（宽 / 高），如 16/9、4/3、1' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '容器内部内容（如图片、视频、占位块等）' },
]
</script>

<template>
  <ComponentDoc
    title="AspectRatio 宽高比"
    description="保持内容固定宽高比的容器，适用于图片、视频等媒体元素。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于图片画廊、视频播放器、卡片封面等需要保持固定宽高比的场景。内部内容通过 CSS 绝对定位填满容器，配合 object-cover 等样式实现自适应裁剪。</p>
    </section>

    <section id="ratios">
      <DemoBlock
        title="常用比例"
        description="保持内容固定宽高比的容器"
        code='<EAspectRatio :ratio="16/9">
  <img src="..." class="object-cover w-full h-full" />
</EAspectRatio>'
      >
        <div class="grid grid-cols-3 gap-4">
          <div>
            <p class="text-xs text-muted-foreground mb-1">16:9</p>
            <EAspectRatio :ratio="16/9">
              <div class="bg-muted rounded-md w-full h-full flex items-center justify-center text-sm text-muted-foreground">
                16:9
              </div>
            </EAspectRatio>
          </div>
          <div>
            <p class="text-xs text-muted-foreground mb-1">4:3</p>
            <EAspectRatio :ratio="4/3">
              <div class="bg-muted rounded-md w-full h-full flex items-center justify-center text-sm text-muted-foreground">
                4:3
              </div>
            </EAspectRatio>
          </div>
          <div>
            <p class="text-xs text-muted-foreground mb-1">1:1</p>
            <EAspectRatio :ratio="1">
              <div class="bg-muted rounded-md w-full h-full flex items-center justify-center text-sm text-muted-foreground">
                1:1
              </div>
            </EAspectRatio>
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
