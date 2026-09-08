# 2.x 查 API

精确 props/emits **不要**写进 skill。按安装版本读类型。

## manifest（≥2.1.0）

```
node_modules/@dwydev/eui/dist/component-manifest.json
```

- 组件名 → `componentToDir["EButton"]` → 目录 `button`
- `directories["button"].types` → `components/button/types.d.ts`
- 拼接 `node_modules/@dwydev/eui/dist/` + 该路径

`<2.1.0` 没有 manifest：直接 `ls dist/components/`。

## types

```
node_modules/@dwydev/eui/dist/components/{kebab}/types.d.ts
```

`{kebab}`：去 `E` 前缀后 kebab-case（`EDatePicker` → `date-picker`）。不确定就 `ls`，不要猜。

## slots

`.d.ts` 里 slot 常是 `any`。需要具名/作用域插槽时 clone 该版本 tag，在 `frontend/eui/src/components/{kebab}/*.vue` 搜 `<slot`。

npm 包 `files` 不含 `.vue`，`node_modules` 里没有模板。
