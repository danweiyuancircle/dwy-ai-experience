<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const username = ref('')
const password = ref('')

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础登录页' },
  { id: 'background', label: '自定义背景' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'title', type: 'string', description: '登录页标题，显示在 Logo 下方' },
  { name: 'logo', type: 'string', description: 'Logo 图片地址' },
  { name: 'background', type: 'string', description: '自定义背景 CSS（如渐变色、图片等）' },
]

const slotsData = [
  { name: 'default', description: '表单内容区域（卡片内部）' },
  { name: 'logo', description: '自定义 Logo 区域（替代默认 img + title）' },
  { name: 'footer', description: '卡片下方的底部区域' },
]
</script>

<template>
  <ComponentDoc
    title="LoginLayout 登录页布局"
    description="开箱即用的登录页布局组件，提供居中卡片、Logo/标题展示和自定义背景，适配各种登录表单。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">用于搭建应用的登录页面。组件提供居中布局、Logo 标题区域和表单卡片容器，开发者只需在默认插槽中放入表单控件即可完成一个美观的登录页。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础登录页"
        description="包含标题、用户名密码输入框和登录按钮"
        code='<ELoginLayout title="欢迎登录">
  <form class="space-y-4">
    <EInput v-model="username" placeholder="用户名" />
    <EInput v-model="password" type="password" placeholder="密码" />
    <EButton class="w-full">登 录</EButton>
  </form>
  <template #footer>
    <p>还没有账号？<a href="#" class="underline">注册</a></p>
  </template>
</ELoginLayout>'
      >
        <div class="h-[500px] rounded-lg border overflow-hidden">
          <ELoginLayout title="欢迎登录">
            <form class="space-y-4" @submit.prevent>
              <div class="space-y-2">
                <ELabel>用户名</ELabel>
                <EInput v-model="username" placeholder="请输入用户名" />
              </div>
              <div class="space-y-2">
                <ELabel>密码</ELabel>
                <EInput v-model="password" type="password" placeholder="请输入密码" />
              </div>
              <EButton class="w-full">登 录</EButton>
            </form>
            <template #footer>
              <p>还没有账号？<a href="#" class="text-primary underline">立即注册</a></p>
            </template>
          </ELoginLayout>
        </div>
      </DemoBlock>
    </section>

    <section id="background">
      <DemoBlock
        title="自定义背景"
        description="通过 background 属性设置渐变背景"
        code='<ELoginLayout
  title="系统登录"
  background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
>
  ...
</ELoginLayout>'
      >
        <div class="h-[500px] rounded-lg border overflow-hidden">
          <ELoginLayout
            title="系统登录"
            background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
          >
            <form class="space-y-4" @submit.prevent>
              <div class="space-y-2">
                <ELabel>邮箱</ELabel>
                <EInput placeholder="name@example.com" />
              </div>
              <div class="space-y-2">
                <ELabel>密码</ELabel>
                <EInput type="password" placeholder="请输入密码" />
              </div>
              <div class="flex items-center gap-2">
                <ECheckbox id="remember" />
                <ELabel for="remember" class="text-sm font-normal">记住我</ELabel>
              </div>
              <EButton class="w-full">登 录</EButton>
            </form>
            <template #footer>
              <p class="text-white/80">忘记密码？<a href="#" class="text-white underline">找回密码</a></p>
            </template>
          </ELoginLayout>
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
