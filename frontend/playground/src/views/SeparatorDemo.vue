<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'orientation', label: '方向' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'orientation', type: "'horizontal' | 'vertical'", default: "'horizontal'", description: '分隔线方向' },
  { name: 'decorative', type: 'boolean', default: 'true', description: '是否为装饰性元素（true 时无障碍隐藏）' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名，通过 cn() 合并' },
]
</script>

<template>
  <ComponentDoc
    title="Separator 分隔线"
    description="水平或垂直方向的分隔线，用于在视觉上分隔内容区域。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于列表项之间、内容区域之间、导航栏元素之间的视觉分隔。支持水平和垂直两种方向，decorative 模式下对屏幕阅读器不可见。</p>
    </section>

    <section id="orientation">
      <DemoBlock
        title="方向"
        description="水平或垂直方向的分隔线"
        code='<ESeparator />
<ESeparator orientation="vertical" />'
      >
        <div class="space-y-4">
          <!-- 水平 -->
          <div>
            <p class="text-sm mb-2">水平分隔线</p>
            <div>文字内容上方</div>
            <ESeparator class="my-3" />
            <div>文字内容下方</div>
          </div>
          <!-- 垂直 -->
          <div>
            <p class="text-sm mb-2">垂直分隔线</p>
            <div class="flex items-center gap-4 h-8">
              <span>左侧内容</span>
              <ESeparator orientation="vertical" />
              <span>右侧内容</span>
              <ESeparator orientation="vertical" />
              <span>更多内容</span>
            </div>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <h2 class="text-lg font-semibold mb-3">Slots</h2>
      <p class="text-sm text-muted-foreground">该组件无自定义插槽。</p>
    </section>
  </ComponentDoc>
</template>
