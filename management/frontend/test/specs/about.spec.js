import { shallowMount } from '@vue/test-utils'
import test from 'ava'
import about from '../../client/src/pages/about.vue'

// TODO: make more realistic testing suite

test('about.vue', t => {
  const wrapper = shallowMount(about, {
    mocks: {
      $route: {
        name: 'about'
      }
    }
  })
  let html = wrapper.html()
  t.truthy(html.includes('Different Stats'))
})
