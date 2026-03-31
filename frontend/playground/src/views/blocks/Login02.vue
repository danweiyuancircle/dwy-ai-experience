<script setup lang="ts">
import { GalleryVerticalEnd } from 'lucide-vue-next'
</script>

<template>
  <div class="grid min-h-svh lg:grid-cols-2">
    <!-- Left: form area -->
    <div class="flex flex-col gap-4 p-6 md:p-10">
      <!-- Logo -->
      <div class="flex justify-center gap-2 md:justify-start">
        <a href="#" class="flex items-center gap-2 font-medium">
          <div class="flex size-6 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <GalleryVerticalEnd class="size-4" />
          </div>
          丹微元科技
        </a>
      </div>

      <!-- Centered form -->
      <div class="flex flex-1 items-center justify-center">
        <div class="w-full max-w-xs">
          <div class="grid gap-6">
            <!-- Header -->
            <div class="flex flex-col items-center gap-2 text-center">
              <h1 class="text-2xl font-bold">登录账号</h1>
              <p class="text-balance text-sm text-muted-foreground">
                输入您的邮箱和密码登录系统
              </p>
            </div>

            <!-- Form -->
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
                      class="ml-auto text-sm underline-offset-4 hover:underline"
                    >
                      忘记密码?
                    </a>
                  </div>
                  <EInput id="password" type="password" />
                </div>
              </div>

              <EButton class="w-full">登录</EButton>

              <!-- Separator -->
              <div class="relative text-center text-sm">
                <span class="absolute inset-0 flex items-center">
                  <ESeparator />
                </span>
                <span class="relative bg-background px-2 text-muted-foreground">
                  或者使用以下方式
                </span>
              </div>

              <EButton variant="outline" class="w-full">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-4">
                  <path
                    d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
                    fill="currentColor"
                  />
                </svg>
                使用 GitHub 账号登录
              </EButton>
            </div>

            <!-- Sign up link -->
            <div class="text-center text-sm">
              没有账号?
              <a href="#" class="underline underline-offset-4">注册</a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right: image placeholder -->
    <div class="relative hidden bg-muted lg:block">
      <div class="absolute inset-0 flex items-center justify-center">
        <span class="text-4xl font-semibold text-muted-foreground/40">Image</span>
      </div>
    </div>
  </div>
</template>
