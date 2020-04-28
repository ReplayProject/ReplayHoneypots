import { shallowMount } from '@vue/test-utils'
import test from 'ava'
import sparkline from '../../client/src/components/sparkline.vue'
import sinon from 'sinon'
import store from '../store'

// Helper function returns a promise that resolves after all other promise mocks,
// even if they are chained like Promise.resolve().then(...)
// Technically: this is designed to resolve on the next macrotask
function tick () {
  return new Promise(resolve => {
    setTimeout(resolve, 0)
  })
}

test('sparkline.vue init', t => {
  const spy = sinon.spy()
  const createIndex = sinon.stub().returns({ result: 'exists' })
  const find = sinon.stub().returns({ docs: [] })

  const wrapper = shallowMount(sparkline, {
    mocks: {
      $route: {
        name: 'index'
      },
      $pouch: {
        createIndex,
        find
      },
      $store: store,
      $Progress: {
        start: spy,
        finish: spy
      }
    }
  })
  let html = wrapper.html()
  t.truthy(html.includes('line-chart-stub'))
})

test.only('sparkline.vue load data', async t => {
  const spy = sinon.spy()
  const createIndex = sinon.stub().returns({ result: 'exists' })
  const find = sinon.stub().returns({ docs: [] })

  const wrapper = shallowMount(sparkline, {
    mocks: {
      $route: {
        name: 'index'
      },
      $pouch: {
        createIndex,
        find
      },
      $store: store,
      $Progress: {
        start: spy,
        finish: spy
      }
    }
  })
  let html = wrapper.html()

  await tick()

  t.truthy(html.includes('line-chart-stub'))
  t.truthy(find.called, 'find was called')
})
