<script setup lang="ts">
</script>

<template>
  <div class="flex min-h-svh flex-col items-center justify-center p-6 md:p-10">
    <div class="w-full max-w-sm md:max-w-3xl">
      <ECard class="overflow-hidden p-0">
        <div class="-mx-6 grid md:grid-cols-2">
          <!-- Left: form -->
          <div class="p-6 md:p-8">
            <div class="grid gap-6">
              <!-- Header -->
              <div class="flex flex-col items-center text-center">
                <h1 class="text-2xl font-bold">欢迎回来</h1>
                <p class="text-balance text-muted-foreground">
                  登录您的丹微元科技账号
                </p>
              </div>

              <!-- Form fields -->
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

              <!-- Social login buttons -->
              <div class="grid grid-cols-3 gap-4">
                <!-- Apple -->
                <EButton variant="outline" class="w-full">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-4">
                    <path
                      d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"
                      fill="currentColor"
                    />
                  </svg>
                  <span class="sr-only">Apple</span>
                </EButton>
                <!-- Google -->
                <EButton variant="outline" class="w-full">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-4">
                    <path
                      d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"
                      fill="currentColor"
                    />
                  </svg>
                  <span class="sr-only">Google</span>
                </EButton>
                <!-- Meta -->
                <EButton variant="outline" class="w-full">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-4">
                    <path
                      d="M6.915 4.03c-1.968 0-3.683 1.28-4.871 3.113C.704 9.208 0 11.883 0 14.449c0 .706.07 1.369.21 1.973a6.624 6.624 0 0 0 .265.86 5.297 5.297 0 0 0 .371.761c.696 1.159 1.818 1.927 3.593 1.927 1.497 0 2.633-.671 3.965-2.444.76-1.012 1.144-1.626 2.663-4.32l.756-1.339.186-.325c.061.1.121.196.18.288l.096.148a28.556 28.556 0 0 0 .774 1.122l.116.163c.94 1.32 1.727 2.373 2.373 3.14 1.228 1.46 2.236 2.14 3.578 2.14 1.72 0 2.84-.756 3.534-1.916.347-.58.56-1.222.681-1.9A9.27 9.27 0 0 0 24 14.449c0-2.547-.702-5.2-2.034-7.294C20.762 5.304 19.05 4.03 17.08 4.03c-1.573 0-2.762.755-3.986 2.346-.782 1.017-1.378 1.997-2.076 3.262l-.214.39-.146.263c-.06-.105-.12-.21-.18-.31a31.342 31.342 0 0 0-.573-.89 28.413 28.413 0 0 0-.252-.37l-.073-.103c-.96-1.345-1.76-2.378-2.407-3.08C6.126 4.7 5.156 4.03 3.985 4.03H3.98l.005-.001h.074l-.03.001H6.915zm-.256 2.047c.2 0 .494.142.94.6.453.466 1 1.199 1.706 2.25l.192.283c-.253.427-.494.84-.723 1.234l-.186.325-.336.583c-1.3 2.254-1.74 2.95-2.315 3.715-.828 1.1-1.39 1.455-2.052 1.455-.704 0-1.162-.258-1.544-.784a2.966 2.966 0 0 1-.217-.399 4.187 4.187 0 0 1-.17-.56A6.374 6.374 0 0 1 2 14.449c0-2.236.596-4.6 1.612-6.313.59-.993 1.28-1.627 1.94-1.913.33-.143.636-.196.902-.189l.205.043zm10.421 0c.2 0 .494.142.94.6.453.466 1 1.199 1.706 2.25a29.484 29.484 0 0 1 .433.671l-.062.105c-.166.282-.334.576-.506.886l-.37.654c-1.253 2.18-1.726 2.95-2.315 3.715-.828 1.1-1.39 1.455-2.052 1.455-.704 0-1.162-.258-1.544-.784a2.966 2.966 0 0 1-.217-.399 4.187 4.187 0 0 1-.17-.56A6.374 6.374 0 0 1 12 14.449c0-2.236.596-4.6 1.612-6.313.59-.993 1.28-1.627 1.94-1.913a2.12 2.12 0 0 1 .902-.189l.205.043h-.579z"
                      fill="currentColor"
                    />
                  </svg>
                  <span class="sr-only">Meta</span>
                </EButton>
              </div>

              <!-- Terms -->
              <div class="text-balance text-center text-xs text-muted-foreground">
                点击登录即表示您同意我们的
                <a href="#" class="underline underline-offset-4 hover:text-primary">服务条款</a>
                和
                <a href="#" class="underline underline-offset-4 hover:text-primary">隐私政策</a>
              </div>
            </div>
          </div>

          <!-- Right: image placeholder -->
          <div class="relative hidden bg-muted md:block">
            <div class="absolute inset-0 flex items-center justify-center">
              <span class="text-2xl font-semibold text-muted-foreground/40">Image</span>
            </div>
          </div>
        </div>
      </ECard>
    </div>
  </div>
</template>
