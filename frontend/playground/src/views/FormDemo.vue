<script setup lang="ts">
import { ref, reactive } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const formRef = ref<any>(null)
const submitResult = ref('')

const model = reactive({
  username: '',
  email: '',
  password: '',
  role: '',
  active: true,
  bio: '',
})

const roleOptions = [
  { label: '管理员', value: 'admin' },
  { label: '编辑员', value: 'editor' },
  { label: '访客', value: 'guest' },
]

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate()
  if (valid) {
    submitResult.value = JSON.stringify(model, null, 2)
  }
}

function handleReset() {
  if (formRef.value) {
    formRef.value.resetFields()
    submitResult.value = ''
  }
}

const inlineModel = reactive({ keyword: '', status: '' })

const statusOptions = [
  { label: '全部', value: '' },
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' },
]

// Simple rules without Zod for demo
const rules = {
  username: { required: true, min: 3, message: '用户名至少 3 个字符' },
  email: { required: true, type: 'email', message: '请输入有效的邮箱地址' },
  password: { required: true, min: 8, message: '密码至少 8 个字符' },
  role: { required: true, message: '请选择角色' },
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'complete', label: '完整表单' },
  { id: 'top-label', label: '顶部标签' },
  { id: 'inline', label: '行内表单' },
  { id: 'form-props', label: 'Form Props' },
  { id: 'form-events', label: 'Form Events' },
  { id: 'form-expose', label: 'Form Expose' },
  { id: 'form-item-props', label: 'FormItem Props' },
  { id: 'slots', label: 'Slots' },
]

const formPropsData = [
  { name: 'model', type: 'Record<string, any>', description: '表单数据对象' },
  { name: 'rules', type: 'ZodType | Record<string, FormRule | FormRule[]>', description: '验证规则，支持 Zod schema 或自定义规则对象' },
  { name: 'labelWidth', type: 'string', description: '标签宽度，如 "80px"' },
  { name: 'labelPosition', type: "'left' | 'right' | 'top'", default: "'right'", description: '标签对齐方式' },
  { name: 'size', type: "'sm' | 'default' | 'lg'", default: "'default'", description: '表单内组件尺寸' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用整个表单' },
  { name: 'inline', type: 'boolean', default: 'false', description: '是否行内布局' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const formEventsData = [
  { name: 'submit', params: '(values: Record<string, any>)', description: '表单提交时触发' },
]

const formExposeData = [
  { name: 'validate', type: '() => Promise<boolean>', description: '验证所有字段，返回是否通过' },
  { name: 'validateField', type: '(name: string) => Promise<boolean>', description: '验证指定字段' },
  { name: 'resetFields', type: '() => void', description: '重置所有字段到初始值并清除验证' },
  { name: 'clearValidate', type: '() => void', description: '清除所有验证状态' },
]

const formItemPropsData = [
  { name: 'label', type: 'string', description: '标签文本' },
  { name: 'prop', type: 'string', description: '对应 model 中的字段名（用于验证）' },
  { name: 'required', type: 'boolean', default: 'false', description: '是否显示必填星号' },
  { name: 'labelWidth', type: 'string', description: '单独设置标签宽度，覆盖 Form 的值' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: 'Form: 表单项内容 / FormItem: 表单控件内容' },
]
</script>

<template>
  <ComponentDoc
    title="Form 表单"
    description="完整表单组件，支持多种布局、字段验证和提交处理。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要收集用户信息并进行验证的场景，如用户注册/登录表单、数据编辑页面、搜索筛选栏等。通过 EForm + EFormItem 组合使用，配合 rules 实现字段级验证，支持 Zod schema 和自定义规则两种验证方式。</p>
    </section>

    <section id="complete">
      <DemoBlock
        title="完整表单示例"
        description="使用 EForm + EFormItem 构建带验证的表单"
        code='<EForm ref="formRef" :model="model" :rules="rules">
  <EFormItem label="用户名" prop="username">
    <EInput v-model="model.username" placeholder="请输入用户名" />
  </EFormItem>
  <EFormItem label="邮箱" prop="email">
    <EInput v-model="model.email" placeholder="请输入邮箱" />
  </EFormItem>
  <EFormItem label="密码" prop="password">
    <EInput v-model="model.password" type="password" showPassword />
  </EFormItem>
  <EFormItem label="角色" prop="role">
    <ESelect v-model="model.role" :options="roleOptions" placeholder="请选择角色" />
  </EFormItem>
  <EFormItem label="状态">
    <ESwitch v-model="model.active" label="启用账号" />
  </EFormItem>
  <EFormItem>
    <EButton @click="handleSubmit">提交</EButton>
    <EButton variant="outline" @click="handleReset">重置</EButton>
  </EFormItem>
</EForm>'
      >
        <EForm ref="formRef" :model="model" :rules="rules" label-width="80px">
          <EFormItem label="用户名" prop="username">
            <EInput v-model="model.username" placeholder="请输入用户名（至少 3 字符）" />
          </EFormItem>
          <EFormItem label="邮箱" prop="email">
            <EInput v-model="model.email" placeholder="请输入邮箱地址" />
          </EFormItem>
          <EFormItem label="密码" prop="password">
            <EInput v-model="model.password" type="password" :showPassword="true" placeholder="请输入密码（至少 8 位）" />
          </EFormItem>
          <EFormItem label="角色" prop="role">
            <ESelect v-model="model.role" :options="roleOptions" placeholder="请选择角色" class="w-full" />
          </EFormItem>
          <EFormItem label="状态">
            <ESwitch v-model="model.active" label="启用账号" />
          </EFormItem>
          <EFormItem label="简介">
            <ETextarea v-model="model.bio" placeholder="请输入个人简介（可选）" />
          </EFormItem>
          <EFormItem>
            <div class="flex gap-2">
              <EButton @click="handleSubmit">提交验证</EButton>
              <EButton variant="outline" @click="handleReset">重置表单</EButton>
            </div>
          </EFormItem>
        </EForm>

        <div v-if="submitResult" class="mt-4 p-3 bg-muted rounded-md">
          <p class="text-sm font-medium mb-1">提交数据：</p>
          <pre class="text-xs text-muted-foreground">{{ submitResult }}</pre>
        </div>
      </DemoBlock>
    </section>

    <section id="top-label">
      <DemoBlock
        title="顶部标签布局"
        description="设置 labelPosition='top' 将标签显示在输入框上方"
        code='<EForm label-position="top" :model="model">
  <EFormItem label="用户名" prop="username">
    <EInput v-model="model.username" />
  </EFormItem>
</EForm>'
      >
        <EForm label-position="top" :model="{ name: '', city: '' }">
          <EFormItem label="姓名">
            <EInput placeholder="请输入姓名" />
          </EFormItem>
          <EFormItem label="城市">
            <EInput placeholder="请输入城市" />
          </EFormItem>
          <EFormItem>
            <EButton>提交</EButton>
          </EFormItem>
        </EForm>
      </DemoBlock>
    </section>

    <section id="inline">
      <DemoBlock
        title="行内表单"
        description="设置 inline 使表单项水平排列，适合搜索/筛选场景"
        code='<EForm inline :model="model">
  <EFormItem label="关键词">
    <EInput v-model="model.keyword" placeholder="请输入关键词" />
  </EFormItem>
  <EFormItem label="状态">
    <ESelect v-model="model.status" :options="statusOptions" placeholder="请选择" />
  </EFormItem>
  <EFormItem>
    <EButton>搜索</EButton>
  </EFormItem>
</EForm>'
      >
        <EForm inline :model="inlineModel">
          <EFormItem label="关键词">
            <EInput v-model="inlineModel.keyword" placeholder="请输入关键词" />
          </EFormItem>
          <EFormItem label="状态">
            <ESelect v-model="inlineModel.status" :options="statusOptions" placeholder="请选择" class="w-32" />
          </EFormItem>
          <EFormItem>
            <EButton>搜索</EButton>
          </EFormItem>
        </EForm>
      </DemoBlock>
    </section>

    <section id="form-props">
      <PropsTable :data="formPropsData" />
    </section>

    <section id="form-events">
      <EventsTable :data="formEventsData" />
    </section>

    <section id="form-expose">
      <h2 class="text-lg font-semibold mb-3">Form Expose</h2>
      <div class="border rounded-lg overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b bg-muted/50">
              <th class="text-left font-medium px-4 py-2.5 w-[180px]">方法名</th>
              <th class="text-left font-medium px-4 py-2.5 w-[280px]">类型</th>
              <th class="text-left font-medium px-4 py-2.5">说明</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in formExposeData" :key="item.name" class="border-b last:border-b-0">
              <td class="px-4 py-2.5"><code class="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">{{ item.name }}</code></td>
              <td class="px-4 py-2.5 text-muted-foreground"><code class="text-xs font-mono">{{ item.type }}</code></td>
              <td class="px-4 py-2.5">{{ item.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section id="form-item-props">
      <h2 class="text-lg font-semibold mb-3">FormItem Props</h2>
      <PropsTable :data="formItemPropsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
