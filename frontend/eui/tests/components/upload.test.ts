import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EUpload from '@/components/upload/EUpload.vue'

describe('EUpload', () => {
  it('renders with data-slot attribute', () => {
    const wrapper = mount(EUpload)
    expect(wrapper.attributes('data-slot')).toBe('upload')
  })

  it('renders a hidden file input', () => {
    const wrapper = mount(EUpload)
    const input = wrapper.find('input[type="file"]')
    expect(input.exists()).toBe(true)
    expect(input.classes()).toContain('hidden')
  })

  it('applies accept prop to file input', () => {
    const wrapper = mount(EUpload, { props: { accept: 'image/*' } })
    const input = wrapper.find('input[type="file"]')
    expect(input.attributes('accept')).toBe('image/*')
  })

  it('applies multiple prop to file input', () => {
    const wrapper = mount(EUpload, { props: { multiple: true } })
    const input = wrapper.find('input[type="file"]')
    expect(input.attributes('multiple')).toBeDefined()
  })

  it('does not set multiple attribute by default', () => {
    const wrapper = mount(EUpload)
    const input = wrapper.find('input[type="file"]')
    expect(input.attributes('multiple')).toBeUndefined()
  })

  it('applies disabled state', () => {
    const wrapper = mount(EUpload, { props: { disabled: true } })
    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('renders drag area when drag prop is true', () => {
    const wrapper = mount(EUpload, { props: { drag: true } })
    expect(wrapper.text()).toContain('将文件拖拽到此处')
  })

  it('renders click to upload button when drag is false', () => {
    const wrapper = mount(EUpload, { props: { drag: false } })
    expect(wrapper.text()).toContain('点击上传')
  })

  it('renders picture-card layout when listType is picture-card', () => {
    const wrapper = mount(EUpload, { props: { listType: 'picture-card' } })
    // Should render the add card button with "Upload" text
    expect(wrapper.text()).toContain('上传')
    // Should not render the text/picture trigger area
    expect(wrapper.text()).not.toContain('点击上传')
  })

  it('renders file list for text listType', () => {
    const wrapper = mount(EUpload, {
      props: {
        listType: 'text',
        modelValue: [
          { uid: '1', name: 'test.txt', status: 'success' as const },
          { uid: '2', name: 'doc.pdf', status: 'ready' as const },
        ],
      },
    })
    expect(wrapper.text()).toContain('test.txt')
    expect(wrapper.text()).toContain('doc.pdf')
  })

  it('shows accept hint in drag mode', () => {
    const wrapper = mount(EUpload, {
      props: { drag: true, accept: '.jpg,.png' },
    })
    expect(wrapper.text()).toContain('.jpg,.png')
  })

  it('renders picture-card items for existing files', () => {
    const wrapper = mount(EUpload, {
      props: {
        listType: 'picture-card',
        modelValue: [
          { uid: '1', name: 'photo.jpg', status: 'success' as const, url: 'http://example.com/photo.jpg' },
        ],
      },
    })
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('http://example.com/photo.jpg')
  })
})
