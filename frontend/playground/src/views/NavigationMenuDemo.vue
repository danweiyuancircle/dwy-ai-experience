<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础导航' },
  { id: 'dropdown', label: '下拉面板' },
  { id: 'mixed', label: '混合导航' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'ENavigationMenu.viewport', type: 'boolean', default: 'true', description: '是否使用 Viewport 容器渲染下拉内容' },
  { name: 'ENavigationMenuTrigger.disabled', type: 'boolean', default: 'false', description: '是否禁用触发器' },
  { name: 'ENavigationMenuLink.active', type: 'boolean', default: 'false', description: '是否为激活状态' },
  { name: 'ENavigationMenuLink.href', type: 'string', description: '链接地址' },
  { name: 'ENavigationMenuLink.asChild', type: 'boolean', default: 'false', description: '是否使用子元素作为渲染载体' },
]

const slotsData = [
  { name: 'ENavigationMenu > default', description: '放置 ENavigationMenuList 和 ENavigationMenuViewport' },
  { name: 'ENavigationMenuList > default', description: '放置 ENavigationMenuItem 列表' },
  { name: 'ENavigationMenuItem > default', description: '放置 Trigger + Content 或直接放置 Link' },
  { name: 'ENavigationMenuContent > default', description: '下拉面板内容' },
  { name: 'ENavigationMenuLink > default', description: '链接文字内容' },
]
</script>

<template>
  <ComponentDoc
    title="NavigationMenu 导航菜单"
    description="水平导航菜单组件，支持下拉面板和直接链接，适用于网站顶部主导航，提供丰富的下拉内容展示能力。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">用于网站顶部的主导航栏，适合展示分类丰富的导航结构。与普通 Dropdown 不同，NavigationMenu 的下拉面板可以包含复杂的网格布局、描述文字和图标列表，类似于大型网站的 Mega Menu。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础导航"
        description="纯链接导航，无下拉面板"
      >
        <ENavigationMenu>
          <ENavigationMenuList>
            <ENavigationMenuItem>
              <ENavigationMenuLink href="#" active>首页</ENavigationMenuLink>
            </ENavigationMenuItem>
            <ENavigationMenuItem>
              <ENavigationMenuLink href="#">关于我们</ENavigationMenuLink>
            </ENavigationMenuItem>
            <ENavigationMenuItem>
              <ENavigationMenuLink href="#">联系方式</ENavigationMenuLink>
            </ENavigationMenuItem>
            <ENavigationMenuItem>
              <ENavigationMenuLink href="#">博客</ENavigationMenuLink>
            </ENavigationMenuItem>
          </ENavigationMenuList>
        </ENavigationMenu>
      </DemoBlock>
    </section>

    <section id="dropdown">
      <DemoBlock
        title="下拉面板"
        description="hover 触发下拉面板，展示分类详细内容"
        code='<ENavigationMenu>
  <ENavigationMenuList>
    <ENavigationMenuItem>
      <ENavigationMenuTrigger>产品</ENavigationMenuTrigger>
      <ENavigationMenuContent>
        <!-- 下拉面板内容 -->
      </ENavigationMenuContent>
    </ENavigationMenuItem>
  </ENavigationMenuList>
  <ENavigationMenuViewport />
</ENavigationMenu>'
      >
        <ENavigationMenu>
          <ENavigationMenuList>
            <ENavigationMenuItem>
              <ENavigationMenuTrigger>产品</ENavigationMenuTrigger>
              <ENavigationMenuContent>
                <div class="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2">
                  <ENavigationMenuLink href="#" class="block select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div class="text-sm font-medium leading-none mb-1">组件库</div>
                    <p class="line-clamp-2 text-sm leading-snug text-muted-foreground">89 个高质量 Vue 3 组件，开箱即用</p>
                  </ENavigationMenuLink>
                  <ENavigationMenuLink href="#" class="block select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div class="text-sm font-medium leading-none mb-1">工具库</div>
                    <p class="line-clamp-2 text-sm leading-snug text-muted-foreground">HTTP 请求、表单校验、日期处理等工具集</p>
                  </ENavigationMenuLink>
                  <ENavigationMenuLink href="#" class="block select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div class="text-sm font-medium leading-none mb-1">后端基础设施</div>
                    <p class="line-clamp-2 text-sm leading-snug text-muted-foreground">FastAPI 配置、数据库、缓存、认证等</p>
                  </ENavigationMenuLink>
                  <ENavigationMenuLink href="#" class="block select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div class="text-sm font-medium leading-none mb-1">CLI 工具</div>
                    <p class="line-clamp-2 text-sm leading-snug text-muted-foreground">项目脚手架与 Claude 配置同步</p>
                  </ENavigationMenuLink>
                </div>
              </ENavigationMenuContent>
            </ENavigationMenuItem>

            <ENavigationMenuItem>
              <ENavigationMenuTrigger>资源</ENavigationMenuTrigger>
              <ENavigationMenuContent>
                <div class="grid w-[400px] gap-3 p-4">
                  <ENavigationMenuLink href="#" class="block select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div class="text-sm font-medium leading-none mb-1">快速开始</div>
                    <p class="line-clamp-2 text-sm leading-snug text-muted-foreground">5 分钟上手，创建第一个项目</p>
                  </ENavigationMenuLink>
                  <ENavigationMenuLink href="#" class="block select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div class="text-sm font-medium leading-none mb-1">API 文档</div>
                    <p class="line-clamp-2 text-sm leading-snug text-muted-foreground">完整的组件和工具 API 参考文档</p>
                  </ENavigationMenuLink>
                  <ENavigationMenuLink href="#" class="block select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div class="text-sm font-medium leading-none mb-1">更新日志</div>
                    <p class="line-clamp-2 text-sm leading-snug text-muted-foreground">查看每个版本的变更内容</p>
                  </ENavigationMenuLink>
                </div>
              </ENavigationMenuContent>
            </ENavigationMenuItem>

            <ENavigationMenuItem>
              <ENavigationMenuLink href="#">文档</ENavigationMenuLink>
            </ENavigationMenuItem>
          </ENavigationMenuList>
          <ENavigationMenuViewport />
        </ENavigationMenu>
      </DemoBlock>
    </section>

    <section id="mixed">
      <DemoBlock
        title="混合导航"
        description="同时包含下拉面板和普通链接的完整导航栏"
      >
        <ENavigationMenu>
          <ENavigationMenuList>
            <ENavigationMenuItem>
              <ENavigationMenuTrigger>入门</ENavigationMenuTrigger>
              <ENavigationMenuContent>
                <div class="grid w-[500px] gap-3 p-4 md:grid-cols-[.75fr_1fr]">
                  <div class="row-span-3 rounded-md bg-gradient-to-b from-muted/50 to-muted p-6 flex flex-col justify-end">
                    <div class="mb-2 text-lg font-medium">DWY Shared</div>
                    <p class="text-sm leading-tight text-muted-foreground">前后端共享基础包，加速项目开发</p>
                  </div>
                  <ENavigationMenuLink href="#" class="block select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div class="text-sm font-medium leading-none mb-1">安装</div>
                    <p class="text-sm leading-snug text-muted-foreground">如何安装和配置依赖</p>
                  </ENavigationMenuLink>
                  <ENavigationMenuLink href="#" class="block select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div class="text-sm font-medium leading-none mb-1">项目结构</div>
                    <p class="text-sm leading-snug text-muted-foreground">了解 monorepo 的目录组织</p>
                  </ENavigationMenuLink>
                  <ENavigationMenuLink href="#" class="block select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div class="text-sm font-medium leading-none mb-1">主题定制</div>
                    <p class="text-sm leading-snug text-muted-foreground">自定义配色和样式变量</p>
                  </ENavigationMenuLink>
                </div>
              </ENavigationMenuContent>
            </ENavigationMenuItem>

            <ENavigationMenuItem>
              <ENavigationMenuLink href="#" active>组件</ENavigationMenuLink>
            </ENavigationMenuItem>

            <ENavigationMenuItem>
              <ENavigationMenuLink href="#">GitHub</ENavigationMenuLink>
            </ENavigationMenuItem>
          </ENavigationMenuList>
          <ENavigationMenuViewport />
        </ENavigationMenu>
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
