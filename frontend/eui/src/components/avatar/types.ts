import type { HTMLAttributes } from 'vue'

export interface EAvatarProps {
  class?: HTMLAttributes['class']
  src?: string
  alt?: string
  fallback?: string
  size?: 'sm' | 'default' | 'lg'
}
