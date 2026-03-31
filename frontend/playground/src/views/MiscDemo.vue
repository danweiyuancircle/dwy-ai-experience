<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Misc 杂项组件</h1>
    <p class="text-muted-foreground mb-6">EKbd、ESeparator、ESpinner、EEmpty、ETypography、ELabel、EAspectRatio 等工具组件。</p>

    <DemoBlock
      title="Typography 排版"
      description="提供 h1-h4、p、lead、large、small、muted 等排版变体"
      code='<ETypography variant="h1">大标题</ETypography>
<ETypography variant="p">正文段落</ETypography>
<ETypography variant="muted">静音文字</ETypography>'
    >
      <div class="space-y-3">
        <ETypography variant="h1">H1 大标题</ETypography>
        <ETypography variant="h2">H2 二级标题</ETypography>
        <ETypography variant="h3">H3 三级标题</ETypography>
        <ETypography variant="h4">H4 四级标题</ETypography>
        <ETypography variant="lead">Lead 导语文字，比正文大一些</ETypography>
        <ETypography variant="p">P 正文段落，这是一段普通的正文内容，用于展示段落样式。</ETypography>
        <ETypography variant="large">Large 较大文字</ETypography>
        <ETypography variant="small">Small 较小文字</ETypography>
        <ETypography variant="muted">Muted 静音文字，颜色较浅</ETypography>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Kbd 键盘按键"
      description="用于展示快捷键的键盘样式组件"
      code='<EKbd>Ctrl</EKbd> + <EKbd>C</EKbd>'
    >
      <div class="space-y-4">
        <div class="flex items-center gap-2 text-sm">
          <EKbd>Ctrl</EKbd>
          <span>+</span>
          <EKbd>C</EKbd>
          <span class="text-muted-foreground ml-2">复制</span>
        </div>
        <div class="flex items-center gap-2 text-sm">
          <EKbd>Ctrl</EKbd>
          <span>+</span>
          <EKbd>V</EKbd>
          <span class="text-muted-foreground ml-2">粘贴</span>
        </div>
        <div class="flex items-center gap-2 text-sm">
          <EKbd>⌘</EKbd>
          <span>+</span>
          <EKbd>K</EKbd>
          <span class="text-muted-foreground ml-2">打开命令面板</span>
        </div>
        <div class="flex items-center gap-2 text-sm">
          <EKbd>Escape</EKbd>
          <span class="text-muted-foreground ml-2">关闭对话框</span>
        </div>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Separator 分隔线"
      description="水平或垂直方向的分隔线"
      code='<ESeparator />
<ESeparator orientation="vertical" />'
    >
      <div class="space-y-4">
        <!-- 水平 -->
        <div>
          <p class="text-sm mb-2">水平分隔线</p>
          <div>文字内容上方</div>
          <ESeparator class="my-3" />
          <div>文字内容下方</div>
        </div>
        <!-- 垂直 -->
        <div>
          <p class="text-sm mb-2">垂直分隔线</p>
          <div class="flex items-center gap-4 h-8">
            <span>左侧内容</span>
            <ESeparator orientation="vertical" />
            <span>右侧内容</span>
            <ESeparator orientation="vertical" />
            <span>更多内容</span>
          </div>
        </div>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Spinner 加载指示器"
      description="旋转加载指示器，支持 sm / default / lg 三种尺寸"
      code='<ESpinner />
<ESpinner size="lg" />'
    >
      <div class="flex items-center gap-6">
        <div class="flex flex-col items-center gap-2">
          <ESpinner size="sm" />
          <span class="text-xs text-muted-foreground">sm</span>
        </div>
        <div class="flex flex-col items-center gap-2">
          <ESpinner />
          <span class="text-xs text-muted-foreground">default</span>
        </div>
        <div class="flex flex-col items-center gap-2">
          <ESpinner size="lg" />
          <span class="text-xs text-muted-foreground">lg</span>
        </div>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Empty 空状态"
      description="数据为空时的占位展示"
      code='<EEmpty title="暂无数据" description="添加一些数据后这里会显示内容" />'
    >
      <div class="space-y-6">
        <EEmpty />
        <ESeparator />
        <EEmpty title="暂无数据" description="点击上方按钮添加第一条记录" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="Label 标签"
      description="用于关联表单控件的标签元素"
      code='<ELabel for="inputId">用户名</ELabel>
<EInput id="inputId" placeholder="请输入" />'
    >
      <div class="space-y-4 max-w-sm">
        <div class="space-y-1.5">
          <ELabel for="demo-input">用户名</ELabel>
          <EInput id="demo-input" placeholder="请输入用户名" />
        </div>
        <div class="space-y-1.5">
          <ELabel for="demo-email">邮箱地址</ELabel>
          <EInput id="demo-email" placeholder="请输入邮箱" />
        </div>
      </div>
    </DemoBlock>

    <DemoBlock
      title="AspectRatio 宽高比"
      description="保持内容固定宽高比的容器"
      code='<EAspectRatio :ratio="16/9">
  <img src="..." class="object-cover w-full h-full" />
</EAspectRatio>'
    >
      <div class="grid grid-cols-3 gap-4">
        <div>
          <p class="text-xs text-muted-foreground mb-1">16:9</p>
          <EAspectRatio :ratio="16/9">
            <div class="bg-muted rounded-md w-full h-full flex items-center justify-center text-sm text-muted-foreground">
              16:9
            </div>
          </EAspectRatio>
        </div>
        <div>
          <p class="text-xs text-muted-foreground mb-1">4:3</p>
          <EAspectRatio :ratio="4/3">
            <div class="bg-muted rounded-md w-full h-full flex items-center justify-center text-sm text-muted-foreground">
              4:3
            </div>
          </EAspectRatio>
        </div>
        <div>
          <p class="text-xs text-muted-foreground mb-1">1:1</p>
          <EAspectRatio :ratio="1">
            <div class="bg-muted rounded-md w-full h-full flex items-center justify-center text-sm text-muted-foreground">
              1:1
            </div>
          </EAspectRatio>
        </div>
      </div>
    </DemoBlock>
  </div>
</template>
