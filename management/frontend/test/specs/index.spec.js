import { shallowMount } from '@vue/test-utils'
import test from 'ava'
import index from '../../client/src/pages/index.vue'

// TODO: make more realistic testing suite

test('index.vue', t => {
  const wrapper = shallowMount(index, {
    mocks: {
      $route: {
        name: 'index'
      }
    }
  })
  let html = wrapper.html()
  t.truthy(html.includes('General Stats'))
})
