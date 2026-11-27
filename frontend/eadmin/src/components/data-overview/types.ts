/**
 * 数据概览页的注入数据。
 * 页面把数字格式化好再传进来，组件只排版。
 */
import type { Component } from 'vue'

/** 一张指标。 */
export interface OverviewMetric {
  /** 指标名。示例：``'今日注册'``。 */
  title: string
  /** 已格式化的值。示例：``128`` 或 ``'¥99.00'``。 */
  value: string | number
  /** 点击跳转。不传则不可点。示例：``'/admin/users'``。 */
  to?: string
  /** 右上角图标。不传则不显示图标井。 */
  icon?: Component
}

/** 带标题的一组指标。 */
export interface OverviewSection {
  /** 分组名。示例：``'用户'``。 */
  title: string
  /**
   * 这一组在宽屏上的列数。
   * 枚举 ``{2, 3, 5}``，默认 ``3``。
   */
  columns?: 2 | 3 | 5
  /** 组内指标，按数组顺序从左到右。 */
  metrics: OverviewMetric[]
}

/** 概览底部的快捷入口。 */
export interface OverviewLink {
  /** 入口标题。示例：``'API Key'``。 */
  title: string
  /** 一行说明。示例：``'创建或管理密钥'``。 */
  description: string
  /** 点击跳转。示例：``'/keys'``。 */
  to: string
  /** 左上角图标。不传则只留箭头。 */
  icon?: Component
}
