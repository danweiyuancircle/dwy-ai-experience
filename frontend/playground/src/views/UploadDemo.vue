<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const files1 = ref<any[]>([])
const files2 = ref<any[]>([])
const filesCard = ref<any[]>([])
const filesDrag = ref<any[]>([])
const filesValidated = ref<any[]>([])
const filesMaxSize = ref<any[]>([])

function beforeUpload(file: File) {
  const isImage = file.type.startsWith('image/')
  return isImage
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'text', label: '文件列表' },
  { id: 'picture', label: '图片列表' },
  { id: 'picture-card', label: '图片卡片' },
  { id: 'drag', label: '拖拽上传' },
  { id: 'limit', label: '数量限制' },
  { id: 'max-size', label: '文件大小限制' },
  { id: 'before-upload', label: '上传前校验' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: 'UploadFile[]', description: '已上传文件列表' },
  { name: 'action', type: 'string', description: '上传接口地址' },
  { name: 'accept', type: 'string', description: '接受的文件类型，如 "image/*"' },
  { name: 'multiple', type: 'boolean', default: 'false', description: '是否允许多选文件' },
  { name: 'limit', type: 'number', description: '最多可上传文件数' },
  { name: 'maxSize', type: 'number', description: '单个文件最大大小（MB），超出自动拦截并提示' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'listType', type: "'text' | 'picture' | 'picture-card'", default: "'text'", description: '文件列表展示模式' },
  { name: 'drag', type: 'boolean', default: 'false', description: '是否启用拖拽上传' },
  { name: 'beforeUpload', type: '(file: File) => boolean | Promise<boolean>', description: '上传前校验函数，返回 false 阻止上传' },
  { name: 'autoUpload', type: 'boolean', default: 'true', description: '是否自动上传（选择文件后立即上传）' },
  { name: 'headers', type: 'Record<string, string>', description: '上传请求自定义 headers' },
  { name: 'withCredentials', type: 'boolean', default: 'false', description: '是否携带 cookie 凭证' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(files: UploadFile[])', description: '文件列表变化时触发（用于 v-model）' },
  { name: 'change', params: '(files: UploadFile[])', description: '文件列表变化时触发' },
  { name: 'exceed', params: '(files: File[])', description: '超出 limit 限制时触发' },
  { name: 'remove', params: '(file: UploadFile)', description: '移除文件时触发' },
  { name: 'preview', params: '(file: UploadFile)', description: '点击文件预览时触发' },
]

const slotsData = [
  { name: 'default', description: '触发上传的内容（按钮、拖拽区域等）' },
  { name: 'tip', description: '上传提示文字区域' },
]
</script>

<template>
  <ComponentDoc
    title="Upload 上传"
    description="文件上传组件，支持文本列表、图片预览、拖拽上传等展示模式。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要用户上传文件的场景，如头像上传、文档附件、图片批量上传等。文本列表模式适合普通文件上传，图片卡片模式适合图库管理，拖拽模式适合批量文件上传。通过 beforeUpload 可对文件类型和大小进行校验。</p>
    </section>

    <section id="text">
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
    </section>

    <section id="picture">
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
    </section>

    <section id="picture-card">
      <DemoBlock
        title="图片卡片上传（picture-card）"
        description="listType='picture-card' 以网格卡片显示图片"
        code='<EUpload v-model="files" list-type="picture-card" accept="image/*" :multiple="true" />'
      >
        <EUpload v-model="filesCard" list-type="picture-card" accept="image/*" :multiple="true" />
      </DemoBlock>
    </section>

    <section id="drag">
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
    </section>

    <section id="limit">
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
    </section>

    <section id="max-size">
      <DemoBlock
        title="文件大小限制"
        description="设置 maxSize 限制单个文件大小（MB），超出自动拦截并显示提示"
        code='<EUpload v-model="files" :max-size="2" :multiple="true">
  <EButton>上传文件（单个不超过 2MB）</EButton>
</EUpload>'
      >
        <EUpload v-model="filesMaxSize" :max-size="2" :multiple="true">
          <EButton variant="outline">上传文件（单个不超过 2MB）</EButton>
        </EUpload>
      </DemoBlock>
    </section>

    <section id="before-upload">
      <DemoBlock
        title="上传前校验"
        description="通过 beforeUpload 自定义校验逻辑，返回 false 拒绝上传并自动提示"
        code='<EUpload v-model="files" :before-upload="beforeUpload">
  <EButton>仅允许图片</EButton>
</EUpload>

function beforeUpload(file: File) {
  return file.type.startsWith("image/")
}'
      >
        <EUpload v-model="filesValidated" :before-upload="beforeUpload">
          <EButton variant="outline">仅允许图片文件</EButton>
        </EUpload>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
