<script setup lang="ts">
</script>

<template>
  <div class="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
    <div class="w-full max-w-sm">
      <ECard title="登录账号" description="输入您的邮箱和密码登录系统">
        <div class="grid gap-6">
          <div class="grid gap-4">
            <div class="grid gap-2">
              <ELabel for="email">邮箱</ELabel>
              <EInput id="email" type="email" placeholder="name@example.com" />
            </div>
            <div class="grid gap-2">
              <div class="flex items-center">
                <ELabel for="password">密码</ELabel>
                <a
                  href="#"
                  class="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                >
                  忘记密码?
                </a>
              </div>
              <EInput id="password" type="password" />
            </div>
          </div>
          <div class="grid gap-4">
            <EButton class="w-full">登录</EButton>
            <EButton variant="outline" class="w-full">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-4">
                <path
                  d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"
                  fill="currentColor"
                />
              </svg>
              使用 Google 账号登录
            </EButton>
          </div>
        </div>

        <template #footer>
          <div class="w-full text-center text-sm">
            没有账号?
            <a href="#" class="underline underline-offset-4">注册</a>
          </div>
        </template>
      </ECard>
    </div>
  </div>
</template>
