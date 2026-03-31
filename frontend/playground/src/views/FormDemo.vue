<script setup lang="ts">
import { ref, reactive } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

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

// Simple rules without Zod for demo
const rules = {
  username: { required: true, min: 3, message: '用户名至少 3 个字符' },
  email: { required: true, type: 'email', message: '请输入有效的邮箱地址' },
  password: { required: true, min: 8, message: '密码至少 8 个字符' },
  role: { required: true, message: '请选择角色' },
}
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Form 表单</h1>
    <p class="text-muted-foreground mb-6">完整表单组件，支持多种布局、字段验证和提交处理。</p>

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
  </div>
</template>
