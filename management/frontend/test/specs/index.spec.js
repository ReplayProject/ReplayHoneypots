import { shallowMount } from '@vue/test-utils'
import test from 'ava'
import index from '../../client/src/pages/index.vue'
import sinon from 'sinon'

// TODO: make more realistic testing suite

test('index.vue', t => {
  const show = sinon.spy()

  const wrapper = shallowMount(index, {
    mocks: {
      $route: {
        name: 'index'
      },
      $toasted: { show }
    }
  })
  let html = wrapper.html()
  t.truthy(html.includes('General Stats'))
})
