<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const customContent = ref('自定义水印')
const customFontSize = ref(16)
const customRotate = ref(-30)
const customOpacity = ref(0.15)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'multiline', label: '多行水印' },
  { id: 'custom', label: '自定义参数' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'content', type: 'string | string[]', default: "'Watermark'", description: '水印文字内容，数组时为多行' },
  { name: 'fontSize', type: 'number', default: '14', description: '字体大小（px）' },
  { name: 'rotate', type: 'number', default: '-30', description: '旋转角度（度）' },
  { name: 'gap', type: '[number, number]', default: '[100, 100]', description: '水印之间的间距 [水平, 垂直]（px）' },
  { name: 'opacity', type: 'number', default: '0.15', description: '水印透明度（0-1）' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '需要添加水印的内容区域' },
]
</script>

<template>
  <ComponentDoc
    title="Watermark 水印"
    description="在内容区域上方覆盖半透明水印文字，用于标识版权、防止截图盗用等场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于敏感信息展示页面的版权标识、文档预览的防截图水印、内部系统的操作追溯等。通过 Canvas 生成水印图片平铺，不影响内容交互。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="在内容区域上覆盖文字水印"
        code='<EWatermark content="CONFIDENTIAL">
  <div class="h-48 p-4">受保护的内容区域</div>
</EWatermark>'
      >
        <EWatermark content="CONFIDENTIAL">
          <div class="h-48 rounded-lg border p-6 flex items-center justify-center">
            <div class="text-center">
              <p class="text-lg font-semibold mb-2">受保护的内容区域</p>
              <p class="text-sm text-muted-foreground">这里是需要添加水印保护的文档或数据展示区域。水印覆盖在内容上方，不影响鼠标交互和文本选择。</p>
            </div>
          </div>
        </EWatermark>
      </DemoBlock>
    </section>

    <section id="multiline">
      <DemoBlock
        title="多行水印"
        description="content 传入数组时显示多行水印文字"
        code="<EWatermark :content=\"['丹微元科技', '内部文档']\">"
      >
        <EWatermark :content="['丹微元科技', '内部文档']">
          <div class="h-48 rounded-lg border p-6 flex items-center justify-center">
            <div class="text-center">
              <p class="text-lg font-semibold mb-2">多行水印示例</p>
              <p class="text-sm text-muted-foreground">水印文字支持多行显示，适合同时展示公司名和文档分类。</p>
            </div>
          </div>
        </EWatermark>
      </DemoBlock>
    </section>

    <section id="custom">
      <DemoBlock
        title="自定义参数"
        description="调整字体大小、旋转角度、透明度等参数"
      >
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div>
              <label class="text-xs text-muted-foreground block mb-1">水印文字</label>
              <EInput v-model="customContent" placeholder="水印文字" />
            </div>
            <div>
              <label class="text-xs text-muted-foreground block mb-1">字体大小：{{ customFontSize }}px</label>
              <input
                v-model.number="customFontSize"
                type="range"
                min="10"
                max="30"
                class="w-full"
              />
            </div>
            <div>
              <label class="text-xs text-muted-foreground block mb-1">旋转角度：{{ customRotate }}°</label>
              <input
                v-model.number="customRotate"
                type="range"
                min="-90"
                max="90"
                class="w-full"
              />
            </div>
            <div>
              <label class="text-xs text-muted-foreground block mb-1">透明度：{{ customOpacity }}</label>
              <input
                v-model.number="customOpacity"
                type="range"
                min="0.05"
                max="0.5"
                step="0.05"
                class="w-full"
              />
            </div>
          </div>
          <EWatermark
            :content="customContent"
            :font-size="customFontSize"
            :rotate="customRotate"
            :opacity="customOpacity"
          >
            <div class="h-48 rounded-lg border p-6 flex items-center justify-center">
              <p class="text-sm text-muted-foreground">拖动上方滑块调整水印参数，实时预览效果</p>
            </div>
          </EWatermark>
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
