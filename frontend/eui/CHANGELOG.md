# @danweiyuan/eui

## 1.0.1

### Patch Changes

- EUI v1.0.1 — fix critical component interaction bugs

  - Fix EButton click event not propagating through reka-ui as-child (affected Dialog, Popover, Dropdown triggers)
  - Fix EDialog/EPopover/ESheet open state management with reka-ui controlled mode
  - Fix Toast (vue-sonner) CSS not loaded, toast not visible
  - Standardize icons to LoaderCircle, replace raw CSS spinners
  - Add 7 color theme presets (Blue, Green, Rose, Orange, Violet, Slate)
  - Add dark mode support via useTheme composable
  - Fix 15+ component bugs from code review audit (ESelect valueKey/labelKey, EInput iOS Safari, ETabs uncontrolled mode, etc.)
