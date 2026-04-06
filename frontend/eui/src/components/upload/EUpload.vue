<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { Upload, X, File, CheckCircle, AlertCircle, LoaderCircle, Eye } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { EProgress } from '@/components/progress'
import { useConfigProvider } from '@/composables/useConfigProvider'
import type { EUploadProps, EUploadEmits, UploadFile } from './types'

const { locale } = useConfigProvider()

const props = withDefaults(defineProps<EUploadProps>(), {
  modelValue: () => [],
  multiple: false,
  disabled: false,
  listType: 'text',
  drag: false,
  autoUpload: true,
  withCredentials: false,
})

const emit = defineEmits<EUploadEmits>()

const inputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const tipMessage = ref('')
const previewUrl = ref('')
const previewOverlayRef = ref<HTMLElement | null>(null)

watch(previewUrl, (val) => {
  if (val) nextTick(() => previewOverlayRef.value?.focus())
})
let tipTimer: ReturnType<typeof setTimeout> | null = null

function showTip(msg: string) {
  tipMessage.value = msg
  if (tipTimer) clearTimeout(tipTimer)
  tipTimer = setTimeout(() => { tipMessage.value = '' }, 3000)
}

const files = computed(() => props.modelValue ?? [])

function generateUid(): string {
  return `upload-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

function openFilePicker() {
  if (props.disabled) return
  inputRef.value?.click()
}

async function handleFiles(rawFiles: File[]) {
  if (props.disabled) return

  if (props.limit && files.value.length + rawFiles.length > props.limit) {
    showTip(locale.value.uploadExceed.replace('{limit}', String(props.limit)))
    emit('exceed', rawFiles)
    return
  }

  const newFiles: UploadFile[] = []

  for (const raw of rawFiles) {
    // Check file size limit
    if (props.maxSize && raw.size > props.maxSize * 1024 * 1024) {
      const sizeStr = raw.size < 1024 * 1024
        ? `${(raw.size / 1024).toFixed(1)}KB`
        : `${(raw.size / 1024 / 1024).toFixed(1)}MB`
      showTip(locale.value.uploadSizeExceed.replace('{name}', raw.name).replace('{size}', sizeStr).replace('{maxSize}', String(props.maxSize)))
      continue
    }

    // Run beforeUpload validation if provided
    if (props.beforeUpload) {
      try {
        const result = await Promise.resolve(props.beforeUpload(raw))
        if (result === false) {
          showTip(locale.value.uploadValidationFailed.replace('{name}', raw.name))
          continue
        }
      } catch {
        showTip(locale.value.uploadValidationFailed.replace('{name}', raw.name))
        continue
      }
    }

    newFiles.push({
      uid: generateUid(),
      name: raw.name,
      status: 'ready' as const,
      raw,
      url: raw.type.startsWith('image/') ? URL.createObjectURL(raw) : undefined,
      percentage: 0,
      progress: 0,
    })
  }

  if (newFiles.length === 0) return

  const updated = [...files.value, ...newFiles]
  emit('update:modelValue', updated)
  emit('change', updated)

  if (props.autoUpload && props.action) {
    for (const file of newFiles) {
      uploadFile(file)
    }
  }
}

async function uploadFile(file: UploadFile) {
  if (!props.action || !file.raw) return

  file.status = 'uploading'
  file.percentage = 0
  file.progress = 0
  emitFileListUpdate()

  const formData = new FormData()
  formData.append('file', file.raw)

  try {
    const xhr = new XMLHttpRequest()

    await new Promise<void>((resolve, reject) => {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const pct = Math.round((e.loaded / e.total) * 100)
          file.percentage = pct
          file.progress = pct
          emitFileListUpdate()
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          file.status = 'success'
          file.percentage = 100
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

      // Set custom headers
      if (props.headers) {
        for (const [key, value] of Object.entries(props.headers)) {
          xhr.setRequestHeader(key, value)
        }
      }

      // Set withCredentials
      xhr.withCredentials = props.withCredentials

      xhr.send(formData)
    })
  } catch {
    file.status = 'error'
    emitFileListUpdate()
  }
}

/** Manually trigger upload for files in 'ready' status (used when autoUpload=false) */
function submit() {
  if (!props.action) return
  for (const file of files.value) {
    if (file.status === 'ready') {
      uploadFile(file)
    }
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

function onPreview(file: UploadFile) {
  if (file.url) previewUrl.value = file.url
  emit('preview', file)
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

defineExpose({ submit })
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
        class="group relative size-24 overflow-hidden rounded-md border bg-muted"
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
        <!-- Progress overlay for uploading state -->
        <div
          v-if="file.status === 'uploading'"
          class="absolute inset-0 flex items-center justify-center bg-black/40"
        >
          <div class="w-16">
            <EProgress :model-value="file.percentage ?? 0" class="h-1.5" />
          </div>
        </div>
        <!-- Hover overlay with actions -->
        <div
          class="absolute inset-0 flex items-center justify-center gap-2 bg-black/50 opacity-0 transition-opacity group-hover:opacity-100"
          :class="file.status === 'uploading' && 'hidden'"
        >
          <button
            v-if="file.url"
            class="flex size-6 items-center justify-center rounded-full text-white hover:text-white/80"
            @click="onPreview(file)"
          >
            <Eye class="size-4" />
          </button>
          <button
            class="flex size-6 items-center justify-center rounded-full text-white hover:text-white/80"
            @click="removeFile(file)"
          >
            <X class="size-4" />
          </button>
        </div>
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
        <span class="text-xs">{{ locale.uploadCard }}</span>
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
          {{ locale.uploadDrag }}
          <button
            class="text-primary underline"
            @click.stop="openFilePicker"
          >{{ locale.uploadDragLink }}</button>
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
        <span>{{ locale.uploadClick }}</span>
      </button>
    </div>

    <!-- File list (text / picture modes) -->
    <ul v-if="listType !== 'picture-card' && files.length > 0" class="flex flex-col gap-1">
      <li
        v-for="file in files"
        :key="file.uid"
        class="group flex flex-col gap-1 rounded-md px-2 py-1 hover:bg-accent/50"
      >
        <div class="flex items-center gap-2 text-sm">
          <!-- Thumbnail for picture mode -->
          <img
            v-if="listType === 'picture' && file.url"
            :src="file.url"
            :alt="file.name"
            class="size-8 shrink-0 cursor-pointer rounded object-cover"
            @click="onPreview(file)"
          />
          <component
            :is="getStatusIcon(file.status)"
            :class="cn('size-4 shrink-0', getStatusColor(file.status))"
          />
          <span
            class="flex-1 truncate"
            :class="file.url && 'cursor-pointer hover:text-primary'"
            @click="file.url ? onPreview(file) : undefined"
          >
            {{ file.name }}
          </span>
          <button
            class="shrink-0 text-muted-foreground hover:text-destructive"
            @click="removeFile(file)"
          >
            <X class="size-4" />
          </button>
        </div>
        <!-- Progress bar for uploading files -->
        <EProgress
          v-if="file.status === 'uploading'"
          :model-value="file.percentage ?? 0"
          class="h-1.5"
        />
      </li>
    </ul>

    <!-- Inline tip message -->
    <p v-if="tipMessage" class="text-xs text-destructive">{{ tipMessage }}</p>

    <!-- Image preview overlay -->
    <Teleport to="body">
      <Transition
        enter-active-class="duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="previewUrl"
          class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/80"
          @click="previewUrl = ''"
          @keydown.esc="previewUrl = ''"
          tabindex="0"
          ref="previewOverlayRef"
        >
          <button
            class="absolute top-4 right-4 text-white/70 hover:text-white transition-colors"
            @click.stop="previewUrl = ''"
          >
            <X class="size-6" />
          </button>
          <img
            :src="previewUrl"
            class="max-h-[90vh] max-w-[90vw] object-contain animate-in zoom-in-95 duration-200"
            @click.stop
          />
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
