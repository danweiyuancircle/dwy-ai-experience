<script setup lang="ts">
import { ref } from 'vue'

const otpCode = ref('')
</script>

<template>
  <div class="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
    <div class="w-full max-w-xs">
      <ECard title="输入验证码" description="我们已将 6 位验证码发送到您的邮箱">
        <form class="flex flex-col gap-6" @submit.prevent>
          <div class="flex flex-col gap-3">
            <ELabel for="otp">验证码</ELabel>
            <EInputOTP id="otp" v-model="otpCode" :length="6" />
            <p class="text-sm text-muted-foreground">
              请输入发送到您邮箱的 6 位验证码
            </p>
          </div>
          <EButton type="submit" class="w-full">
            验证
          </EButton>
          <p class="text-center text-sm text-muted-foreground">
            没有收到验证码？<a href="#" class="underline underline-offset-4 hover:text-primary">重新发送</a>
          </p>
        </form>
      </ECard>
    </div>
  </div>
</template>
