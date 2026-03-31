<script setup lang="ts">
import { inject, computed, provide } from 'vue'
import { useId } from 'reka-ui'
import { Field } from 'vee-validate'
import { cn } from '@/utils/cn'
import { FORM_ITEM_INJECTION_KEY } from '@/composables'
import { FORM_CONTEXT_KEY } from './context'
import type { EFormItemProps } from './types'

const props = defineProps<EFormItemProps>()

const formContext = inject(FORM_CONTEXT_KEY, undefined)

const id = useId()
provide(FORM_ITEM_INJECTION_KEY, id)

const resolvedLabelWidth = computed(() => {
  return props.labelWidth ?? formContext?.labelWidth?.value
})

const labelPosition = computed(() => {
  return formContext?.labelPosition?.value ?? 'right'
})

const isTopLabel = computed(() => labelPosition.value === 'top')
</script>

<template>
  <div
    data-slot="form-item"
    :class="cn(
      'grid gap-2',
      !isTopLabel && 'grid-cols-[auto_1fr] items-start',
      props.class,
    )"
  >
    <template v-if="prop">
      <Field
        v-slot="{ field, errorMessage }"
        :name="prop"
        :validate-on-input="true"
      >
        <!-- Label -->
        <label
          v-if="label"
          data-slot="form-label"
          :data-error="!!errorMessage"
          :for="`${id}-form-item`"
          :class="cn(
            'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
            'data-[error=true]:text-destructive',
            !isTopLabel && 'flex h-9 items-center',
            labelPosition === 'right' && !isTopLabel && 'text-right',
          )"
          :style="resolvedLabelWidth ? { width: resolvedLabelWidth, minWidth: resolvedLabelWidth } : undefined"
        >
          <span v-if="required" class="text-destructive mr-1">*</span>
          {{ label }}
        </label>

        <!-- Control -->
        <div>
          <div
            :id="`${id}-form-item`"
            :aria-invalid="!!errorMessage"
            :aria-describedby="errorMessage ? `${id}-form-item-message` : undefined"
          >
            <slot v-bind="{ field, errorMessage }" />
          </div>
          <p
            v-if="errorMessage"
            :id="`${id}-form-item-message`"
            data-slot="form-message"
            :class="cn('text-destructive text-sm mt-1')"
          >
            {{ errorMessage }}
          </p>
        </div>
      </Field>
    </template>

    <template v-else>
      <!-- Label without validation -->
      <label
        v-if="label"
        data-slot="form-label"
        :class="cn(
          'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
          !isTopLabel && 'flex h-9 items-center',
          labelPosition === 'right' && !isTopLabel && 'text-right',
        )"
        :style="resolvedLabelWidth ? { width: resolvedLabelWidth, minWidth: resolvedLabelWidth } : undefined"
      >
        <span v-if="required" class="text-destructive mr-1">*</span>
        {{ label }}
      </label>

      <!-- Control without validation -->
      <div>
        <slot />
      </div>
    </template>
  </div>
</template>
