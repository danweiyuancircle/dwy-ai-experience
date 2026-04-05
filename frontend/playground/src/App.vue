<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTheme, EConfigProvider } from '@danweiyuan/eui'
import { Toaster as EToastRoot } from 'vue-sonner'
import { Sun, Moon, Search } from 'lucide-vue-next'
import SearchDialog from './components/SearchDialog.vue'
import { modules, getModuleByPath, getActiveModuleKey } from './data/nav-config'

const route = useRoute()
const router = useRouter()
const { isDark, toggleDark, colorTheme, setColorTheme } = useTheme()
const searchOpen = ref(false)

const themes = [
  { name: 'neutral', color: '#171717', label: 'Neutral' },
  { name: 'blue', color: '#2563eb', label: 'Blue' },
  { name: 'green', color: '#16a34a', label: 'Green' },
  { name: 'rose', color: '#e11d48', label: 'Rose' },
  { name: 'orange', color: '#ea580c', label: 'Orange' },
  { name: 'violet', color: '#7c3aed', label: 'Violet' },
  { name: 'slate', color: '#475569', label: 'Slate' },
]

const activeModuleKey = computed(() => getActiveModuleKey(route.path))
const currentModule = computed(() => modules.find((m) => m.key === activeModuleKey.value))

function switchModule(key: string) {
  const mod = modules.find((m) => m.key === key)
  if (mod) router.push(mod.prefix)
}

function handleKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    searchOpen.value = true
  }
}

onMounted(() => document.addEventListener('keydown', handleKeydown))
onBeforeUnmount(() => document.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <EConfigProvider>
  <div class="flex flex-col h-screen">
    <!-- Top Nav -->
    <header class="flex items-center h-12 border-b bg-background px-4 shrink-0">
      <router-link to="/" class="font-bold text-base mr-6 shrink-0">DWY Shared</router-link>

      <!-- Module Tabs -->
      <nav class="flex items-center gap-1">
        <button
          v-for="mod in modules"
          :key="mod.key"
          @click="switchModule(mod.key)"
          :class="[
            'px-3 py-1.5 rounded-md text-sm transition-colors',
            activeModuleKey === mod.key
              ? 'bg-primary text-primary-foreground font-medium'
              : 'hover:bg-accent text-muted-foreground',
          ]"
        >
          {{ mod.label }}
        </button>
      </nav>

      <div class="flex-1" />

      <!-- Search -->
      <button
        @click="searchOpen = true"
        class="flex items-center gap-2 rounded-md border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent transition-colors mr-2"
      >
        <Search class="size-3.5" />
        <span class="hidden sm:inline">搜索</span>
        <EKbd class="ml-1">⌘K</EKbd>
      </button>

      <!-- Theme Colors -->
      <div class="flex gap-1 mr-2">
        <button
          v-for="t in themes"
          :key="t.name"
          @click="setColorTheme(t.name)"
          :class="['size-4 rounded-full border-2 transition-all', colorTheme === t.name ? 'border-foreground scale-110' : 'border-transparent']"
          :style="{ background: t.color }"
          :title="t.label"
        />
      </div>

      <!-- Dark Mode -->
      <button @click="toggleDark" class="p-2 rounded-md hover:bg-accent transition-colors">
        <Sun v-if="isDark" class="size-4" />
        <Moon v-else class="size-4" />
      </button>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar -->
      <aside class="w-56 border-r overflow-y-auto overscroll-contain bg-background shrink-0">
        <nav class="p-2" v-if="currentModule">
          <div v-for="cat in currentModule.categories" :key="cat.title" class="mb-3">
            <h3 class="px-3 py-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider">{{ cat.title }}</h3>
            <router-link
              v-for="item in cat.items"
              :key="item.path + item.name"
              :to="item.path"
              class="block px-3 py-1.5 rounded-md text-sm hover:bg-accent transition-colors"
              active-class="bg-accent text-accent-foreground font-medium"
            >
              {{ item.name }}
            </router-link>
          </div>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 overflow-y-auto overscroll-contain p-8">
        <router-view />
      </main>
    </div>

    <SearchDialog v-model:open="searchOpen" />
  </div>
  </EConfigProvider>
</template>
