<script setup lang="ts">
import { computed, ref } from 'vue'
import { Upload, X, File, CheckCircle, AlertCircle, LoaderCircle } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { EUploadProps, EUploadEmits, UploadFile } from './types'

const props = withDefaults(defineProps<EUploadProps>(), {
  modelValue: () => [],
  multiple: false,
  disabled: false,
  listType: 'text',
  drag: false,
})

const emit = defineEmits<EUploadEmits>()

const inputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

const files = computed(() => props.modelValue ?? [])

function generateUid(): string {
  return `upload-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

function openFilePicker() {
  if (props.disabled) return
  inputRef.value?.click()
}

function handleFiles(rawFiles: File[]) {
  if (props.disabled) return

  if (props.limit && files.value.length + rawFiles.length > props.limit) {
    emit('exceed', rawFiles)
    return
  }

  const newFiles: UploadFile[] = rawFiles.map((raw) => ({
    uid: generateUid(),
    name: raw.name,
    status: 'ready' as const,
    raw,
    url: raw.type.startsWith('image/') ? URL.createObjectURL(raw) : undefined,
    progress: 0,
  }))

  const updated = [...files.value, ...newFiles]
  emit('update:modelValue', updated)
  emit('change', updated)

  if (props.action) {
    for (const file of newFiles) {
      uploadFile(file)
    }
  }
}

async function uploadFile(file: UploadFile) {
  if (!props.action || !file.raw) return

  file.status = 'uploading'
  file.progress = 0
  emitFileListUpdate()

  const formData = new FormData()
  formData.append('file', file.raw)

  try {
    const xhr = new XMLHttpRequest()

    await new Promise<void>((resolve, reject) => {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          file.progress = Math.round((e.loaded / e.total) * 100)
          emitFileListUpdate()
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          file.status = 'success'
          file.progress = 100
          emitFileListUpdate()
          resolve()
        } else {
          file.status = 'error'
          emitFileListUpdate()
          reject(new Error(`Upload failed with status ${xhr.status}`))
        }
      })

      xhr.addEventListener('error', () => {
        file.status = 'error'
        emitFileListUpdate()
        reject(new Error('Upload failed'))
      })

      xhr.open('POST', props.action!)
      xhr.send(formData)
    })
  } catch {
    file.status = 'error'
    emitFileListUpdate()
  }
}

function emitFileListUpdate() {
  const updated = [...files.value]
  emit('update:modelValue', updated)
  emit('change', updated)
}

function onInputChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files) return
  handleFiles(Array.from(input.files))
  input.value = ''
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  isDragging.value = true
}

function onDragLeave() {
  isDragging.value = false
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  isDragging.value = false
  if (!e.dataTransfer) return
  handleFiles(Array.from(e.dataTransfer.files))
}

function removeFile(file: UploadFile) {
  const updated = files.value.filter((f) => f.uid !== file.uid)
  emit('update:modelValue', updated)
  emit('change', updated)
  emit('remove', file)
}

function getStatusIcon(status: UploadFile['status']) {
  return {
    ready: File,
    uploading: LoaderCircle,
    success: CheckCircle,
    error: AlertCircle,
  }[status]
}

function getStatusColor(status: UploadFile['status']) {
  return {
    ready: 'text-muted-foreground',
    uploading: 'text-blue-500 animate-spin',
    success: 'text-green-500',
    error: 'text-destructive',
  }[status]
}
</script>

<template>
  <div data-slot="upload" :class="cn('flex flex-col gap-2', props.class)">
    <!-- Hidden file input -->
    <input
      ref="inputRef"
      type="file"
      class="hidden"
      :accept="accept"
      :multiple="multiple"
      @change="onInputChange"
    />

    <!-- Picture-card grid -->
    <div v-if="listType === 'picture-card'" class="flex flex-wrap gap-2">
      <div
        v-for="file in files"
        :key="file.uid"
        class="relative size-24 overflow-hidden rounded-md border bg-muted"
      >
        <img
          v-if="file.url"
          :src="file.url"
          :alt="file.name"
          class="h-full w-full object-cover"
        />
        <div
          v-else
          class="flex h-full items-center justify-center"
        >
          <component :is="getStatusIcon(file.status)" :class="cn('size-6', getStatusColor(file.status))" />
        </div>
        <button
          class="absolute right-1 top-1 flex size-4 items-center justify-center rounded-full bg-black/50 text-white hover:bg-black/80"
          @click="removeFile(file)"
        >
          <X class="size-3" />
        </button>
      </div>

      <!-- Add card -->
      <button
        v-if="!limit || files.length < limit"
        :disabled="disabled"
        :class="cn(
          'flex size-24 flex-col items-center justify-center gap-1 rounded-md border border-dashed text-muted-foreground transition-colors',
          'hover:border-primary hover:text-primary',
          'disabled:cursor-not-allowed disabled:opacity-50',
          isDragging && 'border-primary text-primary bg-primary/5',
        )"
        @click="openFilePicker"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
        @drop="onDrop"
      >
        <Upload class="size-5" />
        <span class="text-xs">Upload</span>
      </button>
    </div>

    <!-- Drag / click trigger for text and picture list types -->
    <div
      v-else
      :class="cn(
        'relative rounded-md border transition-colors',
        drag
          ? [
              'border-dashed p-8 text-center',
              isDragging ? 'border-primary bg-primary/5 text-primary' : 'border-input hover:border-primary',
            ]
          : 'border-input',
        disabled && 'cursor-not-allowed opacity-50',
      )"
      @click="!drag ? openFilePicker() : undefined"
      @dragover="drag ? onDragOver($event) : undefined"
      @dragleave="drag ? onDragLeave() : undefined"
      @drop="drag ? onDrop($event) : undefined"
    >
      <div v-if="drag" class="flex flex-col items-center gap-2 text-muted-foreground">
        <Upload class="size-8" />
        <p class="text-sm">
          Drag files here or
          <button
            class="text-primary underline"
            @click.stop="openFilePicker"
          >click to upload</button>
        </p>
        <p v-if="accept" class="text-xs opacity-70">{{ accept }}</p>
      </div>
      <button
        v-else
        :disabled="disabled"
        :class="cn(
          'flex w-full items-center gap-2 px-4 py-2 text-sm text-muted-foreground',
          'hover:text-foreground',
          'disabled:cursor-not-allowed',
        )"
      >
        <Upload class="size-4" />
        <span>Click to upload</span>
      </button>
    </div>

    <!-- File list (text / picture modes) -->
    <ul v-if="listType !== 'picture-card' && files.length > 0" class="flex flex-col gap-1">
      <li
        v-for="file in files"
        :key="file.uid"
        class="flex items-center gap-2 rounded-md px-2 py-1 text-sm hover:bg-accent/50"
      >
        <!-- Thumbnail for picture mode -->
        <img
          v-if="listType === 'picture' && file.url"
          :src="file.url"
          :alt="file.name"
          class="size-8 rounded object-cover"
        />
        <component
          :is="getStatusIcon(file.status)"
          :class="cn('size-4 shrink-0', getStatusColor(file.status))"
        />
        <span class="flex-1 truncate">{{ file.name }}</span>
        <button
          class="shrink-0 text-muted-foreground hover:text-destructive"
          @click="removeFile(file)"
        >
          <X class="size-4" />
        </button>
      </li>
    </ul>
  </div>
</template>
