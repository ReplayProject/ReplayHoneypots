import { shallowMount } from '@vue/test-utils'
import test from 'ava'
import about from '../../client/src/pages/about.vue'
import sinon from 'sinon'

// TODO: make more realistic testing suite

test('about.vue', t => {
  const spy = sinon.spy()
  const createIndex = sinon.stub().returns({ result: 'exists' })
  const find = sinon.stub().returns({ docs: [] })

  const wrapper = shallowMount(about, {
    mocks: {
      $route: {
        name: 'about'
      },
      $pouch: {
        createIndex,
        find
      },
      $Progress: {
        start: spy,
        finish: spy
      }
    }
  })
  let html = wrapper.html()
  t.truthy(html.includes('At a Glance'))
})
