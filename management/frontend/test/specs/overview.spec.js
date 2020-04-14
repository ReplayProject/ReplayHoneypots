import { shallowMount } from '@vue/test-utils'
import test from 'ava'
import overview from '../../client/src/pages/overview.vue'

// TODO: make more realistic testing suite

test('overview.vue', t => {
  const wrapper = shallowMount(overview, {
    mocks: {
      $route: {
        name: 'overview'
      }
    }
  })
  let html = wrapper.html()
  t.truthy(html.includes('index-stub'))
  t.truthy(html.includes('about-stub'))
})
