<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础卡片' },
  { id: 'header', label: '带标题和描述' },
  { id: 'footer', label: '带页脚操作' },
  { id: 'grid', label: '卡片网格布局' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'title', type: 'string', default: '-', description: '卡片标题' },
  { name: 'description', type: 'string', default: '-', description: '卡片描述文字' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '卡片主体内容区域' },
  { name: 'footer', description: '卡片底部操作区域' },
]
</script>

<template>
  <ComponentDoc
    title="Card 卡片"
    description="内容容器组件，支持标题、描述、页脚和自定义内容区域。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于承载独立的信息模块，如用户信息卡、统计数据卡、设置面板、确认对话框内容等。支持标题 + 描述的页眉区域、自由内容区域和操作按钮的页脚区域，常与网格布局组合使用。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础卡片"
        description="最简单的内容卡片"
        code='<ECard>
  <p>卡片内容</p>
</ECard>'
      >
        <ECard class="max-w-sm">
          <p class="text-sm text-muted-foreground">这是一个最简单的卡片，只包含内容区域。</p>
        </ECard>
      </DemoBlock>
    </section>

    <section id="header">
      <DemoBlock
        title="带标题和描述"
        description="通过 title 和 description 属性添加页眉信息"
        code='<ECard title="用户信息" description="管理您的个人资料和偏好设置">
  <p>内容区域</p>
</ECard>'
      >
        <ECard title="用户信息" description="管理您的个人资料和偏好设置" class="max-w-sm">
          <div class="space-y-3">
            <div class="flex justify-between text-sm">
              <span class="text-muted-foreground">用户名</span>
              <span class="font-medium">张三</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-muted-foreground">邮箱</span>
              <span class="font-medium">zhangsan@example.com</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-muted-foreground">角色</span>
              <span class="font-medium">管理员</span>
            </div>
          </div>
        </ECard>
      </DemoBlock>
    </section>

    <section id="footer">
      <DemoBlock
        title="带页脚操作"
        description="使用 footer 插槽添加底部操作按钮"
        code='<ECard title="删除账号">
  <p>确认删除此账号？</p>
  <template #footer>
    <EButton variant="destructive">删除</EButton>
    <EButton variant="outline">取消</EButton>
  </template>
</ECard>'
      >
        <ECard title="删除账号" description="此操作不可逆，请谨慎操作" class="max-w-sm">
          <p class="text-sm text-muted-foreground">删除后，所有数据将永久消失，无法恢复。</p>
          <template #footer>
            <div class="flex gap-2">
              <EButton variant="destructive" size="sm">确认删除</EButton>
              <EButton variant="outline" size="sm">取消</EButton>
            </div>
          </template>
        </ECard>
      </DemoBlock>
    </section>

    <section id="grid">
      <DemoBlock
        title="卡片网格布局"
        description="多卡片网格排列的常见场景"
      >
        <div class="grid grid-cols-3 gap-4">
          <ECard title="总用户数" class="text-center">
            <div class="text-3xl font-bold text-primary py-2">1,234</div>
            <p class="text-xs text-muted-foreground">较上月增长 12%</p>
          </ECard>
          <ECard title="本月订单" class="text-center">
            <div class="text-3xl font-bold text-primary py-2">567</div>
            <p class="text-xs text-muted-foreground">较上月增长 8%</p>
          </ECard>
          <ECard title="活跃会员" class="text-center">
            <div class="text-3xl font-bold text-primary py-2">892</div>
            <p class="text-xs text-muted-foreground">较上月增长 5%</p>
          </ECard>
        </div>
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
