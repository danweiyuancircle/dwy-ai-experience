<script lang="ts">
const DEFAULT_PRESETS = [
  '#000000', '#ffffff', '#ef4444', '#f97316', '#eab308',
  '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6',
]
</script>

<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  PopoverRoot,
  PopoverTrigger,
  PopoverPortal,
  PopoverContent,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EColorPickerProps, EColorPickerEmits } from './types'

const props = withDefaults(defineProps<EColorPickerProps>(), {
  modelValue: '#000000',
  presets: () => DEFAULT_PRESETS,
  showAlpha: false,
  disabled: false,
})

const emit = defineEmits<EColorPickerEmits>()

const inputValue = ref(props.modelValue ?? '#000000')
const alpha = ref(1)

watch(() => props.modelValue, (val) => {
  if (!val) {
    inputValue.value = '#000000'
    alpha.value = 1
    return
  }
  // Parse alpha from 8-digit hex if present
  if (val.length === 9 && val.startsWith('#')) {
    inputValue.value = val.slice(0, 7)
    alpha.value = parseInt(val.slice(7, 9), 16) / 255
  } else {
    inputValue.value = val
    alpha.value = 1
  }
})

function buildColorWithAlpha(hex: string, a: number): string {
  if (a >= 1) return hex.slice(0, 7)
  const alphaHex = Math.round(a * 255).toString(16).padStart(2, '0')
  return `${hex.slice(0, 7)}${alphaHex}`
}

function handleColorChange(val: string) {
  inputValue.value = val
  const finalValue = props.showAlpha ? buildColorWithAlpha(val, alpha.value) : val
  emit('update:modelValue', finalValue)
  emit('change', finalValue)
}

function handleAlphaChange(event: Event) {
  const val = parseFloat((event.target as HTMLInputElement).value)
  alpha.value = val
  const finalValue = buildColorWithAlpha(inputValue.value, val)
  emit('update:modelValue', finalValue)
  emit('change', finalValue)
}

function handleInput(event: Event) {
  const val = (event.target as HTMLInputElement).value
  handleColorChange(val)
}

function selectPreset(color: string) {
  handleColorChange(color)
}
</script>

<template>
  <PopoverRoot>
    <PopoverTrigger
      :disabled="props.disabled"
      as-child
    >
      <button
        type="button"
        :disabled="props.disabled"
        :class="cn(
          'inline-flex items-center gap-2 h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
          props.class,
        )"
      >
        <span
          class="size-5 rounded border border-input flex-shrink-0"
          :style="{ backgroundColor: inputValue }"
        />
        <span class="font-mono">{{ inputValue }}</span>
      </button>
    </PopoverTrigger>

    <PopoverPortal>
      <PopoverContent
        :side-offset="4"
        class="z-50 w-64 rounded-md border bg-popover p-3 shadow-md outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95"
      >
        <!-- Native color picker -->
        <div class="flex flex-col gap-3">
          <div class="flex items-center gap-2">
            <input
              type="color"
              :value="inputValue"
              class="size-10 rounded cursor-pointer border border-input"
              @input="handleInput"
            />
            <input
              type="text"
              :value="inputValue"
              maxlength="9"
              class="flex-1 h-8 rounded border border-input bg-transparent px-2 text-sm font-mono outline-none focus:border-ring"
              @change="handleInput"
            />
          </div>

          <!-- Alpha slider -->
          <div v-if="props.showAlpha" class="flex flex-col gap-1">
            <label class="text-xs text-muted-foreground">Alpha</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              :value="alpha"
              class="w-full"
              @input="handleAlphaChange"
            />
          </div>

          <!-- Presets -->
          <div v-if="props.presets.length > 0" class="flex flex-col gap-1">
            <p class="text-xs text-muted-foreground">Presets</p>
            <div class="flex flex-wrap gap-1">
              <button
                v-for="color in props.presets"
                :key="color"
                type="button"
                class="size-6 rounded border border-input hover:scale-110 transition-transform focus:outline-none focus:ring-2 focus:ring-ring"
                :style="{ backgroundColor: color }"
                :title="color"
                @click="selectPreset(color)"
              />
            </div>
          </div>
        </div>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
