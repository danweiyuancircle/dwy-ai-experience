<!-- 仅管理员 Cookie 登录；Google 应用用户不经过此组件。 -->
<script setup lang="ts">
import { ref } from 'vue'
import { EAlert, EButton, ECard, EInput } from '@dwydev/eui'
import { ShieldCheck } from 'lucide-vue-next'
import { validateCredentials } from './api'
import type { AdminIdentity, AdminLoginProps } from './types'

const props = defineProps<AdminLoginProps>()
const emit = defineEmits<{
  /** 服务端登录成功后通知宿主导航；path 已校验为站内路径。 */
  authenticated: [identity: AdminIdentity, path: string]
}>()
const username = ref('admin')
const password = ref('')
const busy = ref(false)
const error = ref(props.initialError ?? '')

function destination(): string {
  const path = props.redirect
  // 路由器、浏览器与代理对转义分隔符的解释不同，拒绝歧义输入。
  if (!path || !/^\/(?!\/)/.test(path) || /[\\\u0000-\u0020\u007f]|%2f|%5c|%0[0-9a-f]|%1[0-9a-f]|%7f/i.test(path)) return props.homePath
  const pathname = path.split(/[?#]/)[0]
  if (pathname === props.loginPath || pathname.startsWith(`${props.loginPath}/`)) return props.homePath
  return path
}

async function login() {
  if (busy.value) return
  error.value = ''
  busy.value = true
  try {
    validateCredentials(username.value, password.value)
    const identity = await props.auth.login(username.value.trim(), password.value)
    password.value = ''
    emit('authenticated', identity, destination())
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : '登录失败，请重试'
  } finally { busy.value = false }
}
</script>
<template>
  <main class="flex min-h-dvh items-center justify-center bg-muted/30 px-4 py-12">
    <div class="flex w-full max-w-sm flex-col gap-6">
      <div class="flex items-center justify-center gap-2 text-lg font-semibold"><ShieldCheck class="size-5 text-primary" />{{ brand }}</div>
      <ECard title="登录管理后台" description="使用管理员账户继续">
        <form class="flex flex-col gap-5" @submit.prevent="login">
          <label class="flex flex-col gap-2 text-sm font-medium"><span>用户名</span><EInput v-model="username" name="username" autocomplete="username" :maxlength="64" placeholder="输入管理员用户名" :disabled="busy" /></label>
          <label class="flex flex-col gap-2 text-sm font-medium"><span>密码</span><EInput v-model="password" name="password" type="password" autocomplete="current-password" :maxlength="256" placeholder="输入管理员密码" :disabled="busy" /></label>
          <EAlert v-if="error" variant="destructive" :title="error" />
          <EButton type="submit" class="w-full" :loading="busy" :disabled="busy || !username.trim() || !password">登录</EButton>
        </form>
      </ECard>
      <p class="text-center text-xs text-muted-foreground">管理账户与应用用户账户独立</p>
    </div>
  </main>
</template>
