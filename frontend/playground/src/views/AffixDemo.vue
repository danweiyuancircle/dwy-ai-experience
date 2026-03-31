<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'top', label: '固定到顶部' },
  { id: 'bottom', label: '固定到底部' },
  { id: 'offset', label: '偏移量' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'offset', type: 'number', default: '0', description: '触发固定的偏移距离（px）' },
  { name: 'position', type: "'top' | 'bottom'", default: "'top'", description: '固定位置：顶部或底部' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '需要固定的内容' },
]
</script>

<template>
  <ComponentDoc
    title="Affix 固钉"
    description="将元素固定在可视区域的指定位置，当滚动超出范围时自动切换为 fixed 定位。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要在页面滚动时保持可见的元素，如导航栏、操作工具栏、返回顶部按钮、悬浮客服入口等。当元素即将滚出视口时自动固定在指定位置。</p>
    </section>

    <section id="top">
      <DemoBlock
        title="固定到顶部"
        description="默认行为：当元素滚出视口顶部时固定在顶部"
        code='<EAffix :offset="0" position="top">
  <div class="bg-primary text-primary-foreground px-4 py-2 rounded">
    固定在顶部的内容
  </div>
</EAffix>'
      >
        <div class="space-y-2">
          <p class="text-sm text-muted-foreground">Affix 组件会监听页面滚动事件，当包裹的元素即将离开视口时，自动切换为 <code class="text-xs bg-muted px-1.5 py-0.5 rounded">position: fixed</code>，并在原位留下占位元素避免页面跳动。</p>
          <div class="rounded-lg border p-4 bg-muted/30">
            <EAffix :offset="80" position="top">
              <div class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm inline-block">
                滚动页面查看效果 - 固定在距顶部 80px
              </div>
            </EAffix>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="bottom">
      <DemoBlock
        title="固定到底部"
        description="position='bottom' 时固定在视口底部"
        code='<EAffix :offset="20" position="bottom">
  <EButton>固定在底部的按钮</EButton>
</EAffix>'
      >
        <p class="text-sm text-muted-foreground">将 position 设为 <code class="text-xs bg-muted px-1.5 py-0.5 rounded">bottom</code>，当元素接近视口底部时触发固定。常用于操作按钮、反馈入口等需要始终可见的底部元素。</p>
      </DemoBlock>
    </section>

    <section id="offset">
      <DemoBlock
        title="偏移量"
        description="offset 控制触发固定的距离，避免与其他固定元素重叠"
        code='<!-- 距顶部 60px 时固定 -->
<EAffix :offset="60" position="top">
  <div>导航栏下方的工具栏</div>
</EAffix>

<!-- 距底部 20px 时固定 -->
<EAffix :offset="20" position="bottom">
  <div>底部操作区</div>
</EAffix>'
      >
        <div class="space-y-3">
          <p class="text-sm text-muted-foreground">offset 值表示元素距离视口边缘的最小距离（px）。例如页面有 60px 高的固定导航栏，则工具栏应设置 <code class="text-xs bg-muted px-1.5 py-0.5 rounded">offset="60"</code> 避免重叠。</p>
          <div class="grid grid-cols-2 gap-4">
            <div class="rounded border p-3 text-center text-sm">
              <p class="font-medium mb-1">position="top"</p>
              <p class="text-muted-foreground text-xs">元素 top &le; offset 时固定</p>
            </div>
            <div class="rounded border p-3 text-center text-sm">
              <p class="font-medium mb-1">position="bottom"</p>
              <p class="text-muted-foreground text-xs">元素 bottom &ge; viewport - offset 时固定</p>
            </div>
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
