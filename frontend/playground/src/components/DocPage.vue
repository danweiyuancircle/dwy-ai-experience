<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps<{
  content: string
  title?: string
}>()

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
})

const rendered = computed(() => md.render(props.content))
</script>

<template>
  <div>
    <h1 v-if="title" class="text-2xl font-bold mb-6">{{ title }}</h1>
    <div class="doc-content prose prose-neutral dark:prose-invert max-w-none" v-html="rendered" />
  </div>
</template>

<style>
.doc-content h1 { font-size: 1.5rem; font-weight: 700; margin: 1.5rem 0 0.75rem; }
.doc-content h2 { font-size: 1.25rem; font-weight: 600; margin: 1.25rem 0 0.5rem; border-bottom: 1px solid hsl(var(--border)); padding-bottom: 0.4rem; }
.doc-content h3 { font-size: 1.1rem; font-weight: 600; margin: 1rem 0 0.4rem; }
.doc-content p { margin: 0.5rem 0; line-height: 1.7; }
.doc-content ul, .doc-content ol { margin: 0.5rem 0; padding-left: 1.5rem; }
.doc-content li { margin: 0.2rem 0; line-height: 1.6; }
.doc-content code { font-size: 0.875em; padding: 0.15rem 0.4rem; border-radius: 0.25rem; background: hsl(var(--muted)); font-family: 'SF Mono', Menlo, monospace; }
.doc-content pre { margin: 0.75rem 0; padding: 1rem; border-radius: 0.5rem; background: hsl(var(--muted)); overflow-x: auto; }
.doc-content pre code { padding: 0; background: none; font-size: 0.8125rem; line-height: 1.6; }
.doc-content table { width: 100%; border-collapse: collapse; margin: 0.75rem 0; font-size: 0.875rem; }
.doc-content th { text-align: left; font-weight: 600; padding: 0.5rem 0.75rem; border-bottom: 2px solid hsl(var(--border)); }
.doc-content td { padding: 0.5rem 0.75rem; border-bottom: 1px solid hsl(var(--border)); }
.doc-content blockquote { border-left: 3px solid hsl(var(--primary)); padding: 0.5rem 1rem; margin: 0.75rem 0; background: hsl(var(--muted) / 0.5); border-radius: 0 0.25rem 0.25rem 0; }
.doc-content a { color: hsl(var(--primary)); text-decoration: underline; text-underline-offset: 2px; }
.doc-content hr { border: none; border-top: 1px solid hsl(var(--border)); margin: 1.5rem 0; }
.doc-content strong { font-weight: 600; }
</style>
