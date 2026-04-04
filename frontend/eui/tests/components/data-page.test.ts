import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import EDataPage from '@/components/data-page/EDataPage.vue'

const mockFetchFn = vi.fn().mockResolvedValue({ items: [], total: 0 })

const defaultColumns = [
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'age', header: 'Age' },
]

describe('EDataPage', () => {
  it('renders without error', () => {
    const wrapper = mount(EDataPage, {
      props: {
        columns: defaultColumns,
        fetchFn: mockFetchFn,
      },
    })
    expect(wrapper.find('[data-slot="data-page"]').exists()).toBe(true)
  })

  it('renders search input by default', () => {
    const wrapper = mount(EDataPage, {
      props: {
        columns: defaultColumns,
        fetchFn: mockFetchFn,
      },
    })
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('hides search input when searchable is false', () => {
    const wrapper = mount(EDataPage, {
      props: {
        columns: defaultColumns,
        fetchFn: mockFetchFn,
        searchable: false,
      },
    })
    // The search input wrapper with v-if should not exist
    const inputs = wrapper.findAll('input')
    expect(inputs.length).toBe(0)
  })

  it('calls fetchFn on mount', () => {
    mount(EDataPage, {
      props: {
        columns: defaultColumns,
        fetchFn: mockFetchFn,
      },
    })
    expect(mockFetchFn).toHaveBeenCalled()
  })
})
