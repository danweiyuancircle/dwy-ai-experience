<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const isShowBookmarks = ref(true)
const isShowFullUrls = ref(false)
const radioValue = ref('andy')

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础菜单栏' },
  { id: 'checkbox', label: '复选项' },
  { id: 'radio', label: '单选项' },
  { id: 'submenu', label: '子菜单' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'EMenubar', type: '—', description: '菜单栏根容器' },
  { name: 'EMenubarMenu.value', type: 'string', description: '菜单标识值' },
  { name: 'EMenubarTrigger.disabled', type: 'boolean', default: 'false', description: '是否禁用触发器' },
  { name: 'EMenubarContent.align', type: "'start' | 'center' | 'end'", default: "'start'", description: '下拉对齐方式' },
  { name: 'EMenubarContent.sideOffset', type: 'number', description: '侧向偏移量' },
  { name: 'EMenubarItem.disabled', type: 'boolean', default: 'false', description: '是否禁用菜单项' },
  { name: 'EMenubarItem.variant', type: "'default' | 'destructive'", default: "'default'", description: '菜单项样式变体' },
  { name: 'EMenubarItem.inset', type: 'boolean', default: 'false', description: '是否缩进（用于与复选/单选项对齐）' },
  { name: 'EMenubarCheckboxItem.checked', type: 'boolean', description: '复选状态' },
  { name: 'EMenubarRadioGroup.modelValue', type: 'string', description: '单选组当前值' },
  { name: 'EMenubarRadioItem.value', type: 'string', description: '单选项的值' },
  { name: 'EMenubarSubTrigger.inset', type: 'boolean', default: 'false', description: '子菜单触发器是否缩进' },
]

const slotsData = [
  { name: 'EMenubar > default', description: '放置 EMenubarMenu 菜单组' },
  { name: 'EMenubarTrigger > default', description: '触发器文字内容' },
  { name: 'EMenubarContent > default', description: '菜单项内容' },
  { name: 'EMenubarItem > default', description: '菜单项文字和快捷键' },
  { name: 'EMenubarSubContent > default', description: '子菜单内容' },
]
</script>

<template>
  <ComponentDoc
    title="Menubar 菜单栏"
    description="水平菜单栏组件，类似桌面应用的顶部菜单，支持菜单项、分隔线、复选项、单选项和子菜单。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">模拟桌面应用菜单栏交互（如 VS Code、浏览器的文件/编辑/视图菜单）。适用于需要在顶部提供多组操作命令的场景，比如富文本编辑器工具栏、应用设置面板等。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础菜单栏"
        description="包含文件、编辑、视图三个菜单，展示基本菜单项和快捷键"
        code='<EMenubar>
  <EMenubarMenu>
    <EMenubarTrigger>文件</EMenubarTrigger>
    <EMenubarContent>
      <EMenubarItem>新建文件</EMenubarItem>
      <EMenubarItem>打开...</EMenubarItem>
      <EMenubarSeparator />
      <EMenubarItem>保存</EMenubarItem>
    </EMenubarContent>
  </EMenubarMenu>
</EMenubar>'
      >
        <EMenubar>
          <EMenubarMenu>
            <EMenubarTrigger>文件</EMenubarTrigger>
            <EMenubarContent>
              <EMenubarItem>
                新建文件 <span class="ml-auto text-xs text-muted-foreground">Ctrl+N</span>
              </EMenubarItem>
              <EMenubarItem>
                新建窗口 <span class="ml-auto text-xs text-muted-foreground">Ctrl+Shift+N</span>
              </EMenubarItem>
              <EMenubarSeparator />
              <EMenubarItem>
                打开... <span class="ml-auto text-xs text-muted-foreground">Ctrl+O</span>
              </EMenubarItem>
              <EMenubarItem>打开最近文件</EMenubarItem>
              <EMenubarSeparator />
              <EMenubarItem>
                保存 <span class="ml-auto text-xs text-muted-foreground">Ctrl+S</span>
              </EMenubarItem>
              <EMenubarItem>另存为...</EMenubarItem>
              <EMenubarSeparator />
              <EMenubarItem variant="destructive">退出</EMenubarItem>
            </EMenubarContent>
          </EMenubarMenu>

          <EMenubarMenu>
            <EMenubarTrigger>编辑</EMenubarTrigger>
            <EMenubarContent>
              <EMenubarItem>
                撤销 <span class="ml-auto text-xs text-muted-foreground">Ctrl+Z</span>
              </EMenubarItem>
              <EMenubarItem>
                重做 <span class="ml-auto text-xs text-muted-foreground">Ctrl+Y</span>
              </EMenubarItem>
              <EMenubarSeparator />
              <EMenubarItem>
                剪切 <span class="ml-auto text-xs text-muted-foreground">Ctrl+X</span>
              </EMenubarItem>
              <EMenubarItem>
                复制 <span class="ml-auto text-xs text-muted-foreground">Ctrl+C</span>
              </EMenubarItem>
              <EMenubarItem>
                粘贴 <span class="ml-auto text-xs text-muted-foreground">Ctrl+V</span>
              </EMenubarItem>
              <EMenubarSeparator />
              <EMenubarItem>
                全选 <span class="ml-auto text-xs text-muted-foreground">Ctrl+A</span>
              </EMenubarItem>
              <EMenubarItem>
                查找... <span class="ml-auto text-xs text-muted-foreground">Ctrl+F</span>
              </EMenubarItem>
            </EMenubarContent>
          </EMenubarMenu>

          <EMenubarMenu>
            <EMenubarTrigger>视图</EMenubarTrigger>
            <EMenubarContent>
              <EMenubarItem>放大</EMenubarItem>
              <EMenubarItem>缩小</EMenubarItem>
              <EMenubarSeparator />
              <EMenubarItem>全屏</EMenubarItem>
              <EMenubarItem disabled>开发者工具</EMenubarItem>
            </EMenubarContent>
          </EMenubarMenu>
        </EMenubar>
      </DemoBlock>
    </section>

    <section id="checkbox">
      <DemoBlock
        title="复选项"
        description="菜单中可包含可勾选的复选项"
        code='<EMenubarCheckboxItem :checked="isShowBookmarks" @click="isShowBookmarks = !isShowBookmarks">
  显示书签栏
</EMenubarCheckboxItem>'
      >
        <EMenubar>
          <EMenubarMenu>
            <EMenubarTrigger>视图选项</EMenubarTrigger>
            <EMenubarContent>
              <EMenubarCheckboxItem :checked="isShowBookmarks" @click="isShowBookmarks = !isShowBookmarks">
                显示书签栏
              </EMenubarCheckboxItem>
              <EMenubarCheckboxItem :checked="isShowFullUrls" @click="isShowFullUrls = !isShowFullUrls">
                显示完整 URL
              </EMenubarCheckboxItem>
              <EMenubarSeparator />
              <EMenubarItem inset>重置视图</EMenubarItem>
            </EMenubarContent>
          </EMenubarMenu>
        </EMenubar>
        <p class="mt-3 text-sm text-muted-foreground">
          书签栏：{{ isShowBookmarks ? '显示' : '隐藏' }}，完整 URL：{{ isShowFullUrls ? '显示' : '隐藏' }}
        </p>
      </DemoBlock>
    </section>

    <section id="radio">
      <DemoBlock
        title="单选项"
        description="使用 RadioGroup + RadioItem 实现互斥选择"
        code='<EMenubarRadioGroup v-model="radioValue">
  <EMenubarRadioItem value="andy">Andy</EMenubarRadioItem>
  <EMenubarRadioItem value="bob">Bob</EMenubarRadioItem>
</EMenubarRadioGroup>'
      >
        <EMenubar>
          <EMenubarMenu>
            <EMenubarTrigger>切换用户</EMenubarTrigger>
            <EMenubarContent>
              <EMenubarRadioGroup v-model="radioValue">
                <EMenubarRadioItem value="andy">Andy</EMenubarRadioItem>
                <EMenubarRadioItem value="bob">Bob</EMenubarRadioItem>
                <EMenubarRadioItem value="charlie">Charlie</EMenubarRadioItem>
              </EMenubarRadioGroup>
              <EMenubarSeparator />
              <EMenubarItem inset>管理用户...</EMenubarItem>
            </EMenubarContent>
          </EMenubarMenu>
        </EMenubar>
        <p class="mt-3 text-sm text-muted-foreground">当前用户：{{ radioValue }}</p>
      </DemoBlock>
    </section>

    <section id="submenu">
      <DemoBlock
        title="子菜单"
        description="使用 EMenubarSub 创建多级嵌套菜单"
        code='<EMenubarSub>
  <EMenubarSubTrigger>更多工具</EMenubarSubTrigger>
  <EMenubarSubContent>
    <EMenubarItem>保存页面为...</EMenubarItem>
    <EMenubarItem>创建快捷方式</EMenubarItem>
  </EMenubarSubContent>
</EMenubarSub>'
      >
        <EMenubar>
          <EMenubarMenu>
            <EMenubarTrigger>工具</EMenubarTrigger>
            <EMenubarContent>
              <EMenubarItem>任务管理器</EMenubarItem>
              <EMenubarItem>扩展管理</EMenubarItem>
              <EMenubarSeparator />
              <EMenubarSub>
                <EMenubarSubTrigger>更多工具</EMenubarSubTrigger>
                <EMenubarSubContent>
                  <EMenubarItem>保存页面为...</EMenubarItem>
                  <EMenubarItem>创建快捷方式</EMenubarItem>
                  <EMenubarSeparator />
                  <EMenubarItem>开发者工具</EMenubarItem>
                  <EMenubarItem>JavaScript 控制台</EMenubarItem>
                </EMenubarSubContent>
              </EMenubarSub>
              <EMenubarSub>
                <EMenubarSubTrigger>导出</EMenubarSubTrigger>
                <EMenubarSubContent>
                  <EMenubarItem>导出为 PDF</EMenubarItem>
                  <EMenubarItem>导出为 HTML</EMenubarItem>
                  <EMenubarItem>导出为 Markdown</EMenubarItem>
                </EMenubarSubContent>
              </EMenubarSub>
              <EMenubarSeparator />
              <EMenubarItem>清除浏览数据...</EMenubarItem>
            </EMenubarContent>
          </EMenubarMenu>
        </EMenubar>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
