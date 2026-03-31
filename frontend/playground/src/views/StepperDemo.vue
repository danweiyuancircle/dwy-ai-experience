<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'

const step1 = ref(1)
const step2 = ref(2)
const stepVertical = ref(1)

const orderSteps = [
  { title: '提交订单', description: '确认商品信息' },
  { title: '付款', description: '选择支付方式' },
  { title: '商家发货', description: '等待商家处理' },
  { title: '确认收货', description: '完成交易' },
]

const registrationSteps = [
  { title: '填写基本信息' },
  { title: '验证邮箱' },
  { title: '设置密码' },
  { title: '完成注册' },
]

const verticalSteps = [
  { title: '需求分析', description: '收集用户需求，制定开发计划' },
  { title: '设计阶段', description: 'UI/UX 设计，技术架构设计' },
  { title: '开发实现', description: '前端后端并行开发' },
  { title: '测试上线', description: '功能测试，性能优化，部署上线' },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'horizontal', label: '水平步骤条' },
  { id: 'simple', label: '简洁步骤条' },
  { id: 'vertical', label: '垂直步骤条' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue', type: 'number', default: '-', description: '当前步骤（从 1 开始），支持 v-model' },
  { name: 'items', type: 'StepperItem[]', default: '[]', description: '步骤项数组，每项包含 title 和可选 description' },
  { name: 'direction', type: "'horizontal' | 'vertical'", default: "'horizontal'", description: '步骤条方向' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: number)', description: '当前步骤变更时触发' },
]
</script>

<template>
  <ComponentDoc
    title="Stepper 步骤条"
    description="步骤指示组件，用于引导用户完成分步骤的任务流程。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要分步骤完成的任务流程，如订单提交、注册向导、项目进度展示等。通过可视化的步骤指示让用户清楚当前所处阶段和剩余步骤。支持水平和垂直两种方向。</p>
    </section>

    <section id="horizontal">
      <DemoBlock
        title="水平步骤条"
        description="默认水平方向的步骤条，可通过按钮切换当前步骤"
        code='<EStepper v-model="step" :items="steps" />'
      >
        <div class="space-y-4">
          <EStepper v-model="step1" :items="orderSteps" />
          <div class="flex items-center gap-3">
            <EButton
              variant="outline"
              size="sm"
              :disabled="step1 <= 1"
              @click="step1--"
            >
              上一步
            </EButton>
            <EButton
              size="sm"
              :disabled="step1 >= orderSteps.length"
              @click="step1++"
            >
              下一步
            </EButton>
            <span class="text-sm text-muted-foreground">第 {{ step1 }} / {{ orderSteps.length }} 步</span>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="simple">
      <DemoBlock
        title="简洁步骤条"
        description="items 不含 description 时显示简洁样式"
      >
        <div class="space-y-4">
          <EStepper v-model="step2" :items="registrationSteps" />
          <div class="flex gap-2">
            <EButton variant="outline" size="sm" :disabled="step2 <= 1" @click="step2--">上一步</EButton>
            <EButton size="sm" :disabled="step2 >= registrationSteps.length" @click="step2++">下一步</EButton>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="vertical">
      <DemoBlock
        title="垂直步骤条"
        description="设置 direction='vertical' 垂直方向排列"
        code='<EStepper v-model="step" :items="steps" direction="vertical" />'
      >
        <div class="flex gap-8">
          <EStepper v-model="stepVertical" :items="verticalSteps" direction="vertical" class="w-64" />
          <div class="space-y-3">
            <div class="p-3 bg-muted/30 rounded-md">
              <p class="text-sm font-medium">{{ verticalSteps[stepVertical - 1]?.title }}</p>
              <p class="text-xs text-muted-foreground mt-1">{{ verticalSteps[stepVertical - 1]?.description }}</p>
            </div>
            <div class="flex gap-2">
              <EButton variant="outline" size="sm" :disabled="stepVertical <= 1" @click="stepVertical--">上一步</EButton>
              <EButton size="sm" :disabled="stepVertical >= verticalSteps.length" @click="stepVertical++">下一步</EButton>
            </div>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>
  </ComponentDoc>
</template>
