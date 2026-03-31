<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const files1 = ref<any[]>([])
const files2 = ref<any[]>([])
const filesCard = ref<any[]>([])
const filesDrag = ref<any[]>([])
const filesValidated = ref<any[]>([])

function beforeUpload(file: File) {
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    alert('文件大小不能超过 2MB！')
  }
  return isLt2M
}
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Upload 上传</h1>
    <p class="text-muted-foreground mb-6">文件上传组件，支持文本列表、图片预览、拖拽上传等展示模式。</p>

    <DemoBlock
      title="基础文件上传（text）"
      description="默认列表模式，显示文件名列表"
      code='<EUpload v-model="files" list-type="text">
  <EButton>选择文件</EButton>
</EUpload>'
    >
      <EUpload v-model="files1" list-type="text">
        <EButton variant="outline">选择文件</EButton>
      </EUpload>
      <p class="text-sm text-muted-foreground mt-2">已选 {{ files1.length }} 个文件</p>
    </DemoBlock>

    <DemoBlock
      title="图片列表上传（picture）"
      description="listType='picture' 显示缩略图"
      code='<EUpload v-model="files" list-type="picture" accept="image/*">
  <EButton>上传图片</EButton>
</EUpload>'
    >
      <EUpload v-model="files2" list-type="picture" accept="image/*">
        <EButton variant="outline">上传图片</EButton>
      </EUpload>
    </DemoBlock>

    <DemoBlock
      title="图片卡片上传（picture-card）"
      description="listType='picture-card' 以网格卡片显示图片"
      code='<EUpload v-model="files" list-type="picture-card" accept="image/*" :multiple="true" />'
    >
      <EUpload v-model="filesCard" list-type="picture-card" accept="image/*" :multiple="true" />
    </DemoBlock>

    <DemoBlock
      title="拖拽上传"
      description="设置 drag 启用拖拽上传区域"
      code='<EUpload v-model="files" :drag="true">
  <p>拖拽文件到此处或点击上传</p>
</EUpload>'
    >
      <EUpload v-model="filesDrag" :drag="true">
        <div class="text-center py-4">
          <p class="text-muted-foreground">拖拽文件到此处，或</p>
          <p class="text-primary text-sm mt-1">点击上传</p>
        </div>
      </EUpload>
    </DemoBlock>

    <DemoBlock
      title="限制文件数量"
      description="设置 limit 限制最多可上传文件数"
      code='<EUpload v-model="files" :limit="3" :multiple="true">
  <EButton>最多上传 3 个文件</EButton>
</EUpload>'
    >
      <EUpload v-model="files1" :limit="3" :multiple="true">
        <EButton variant="outline">最多 3 个文件</EButton>
      </EUpload>
    </DemoBlock>

    <DemoBlock
      title="上传前校验"
      description="通过 :before-upload 在上传前校验文件，超过 2MB 拒绝上传"
      code='<EUpload v-model="files" :before-upload="beforeUpload">
  <EButton>上传文件（限 2MB）</EButton>
</EUpload>

function beforeUpload(file: File) {
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) alert(&apos;文件大小不能超过 2MB！&apos;)
  return isLt2M
}'
    >
      <EUpload v-model="filesValidated" :before-upload="beforeUpload">
        <EButton variant="outline">上传文件（限 2MB）</EButton>
      </EUpload>
      <p class="text-sm text-muted-foreground mt-2">已选 {{ filesValidated.length }} 个文件（超过 2MB 的文件将被拒绝）</p>
    </DemoBlock>
  </div>
</template>
