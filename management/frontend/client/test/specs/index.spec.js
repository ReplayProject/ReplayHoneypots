import { shallow } from 'vue-test-utils'
import test from 'ava'
import index from '../../src/pages/index.vue'

// TODO: make more realistic testing suite

test('index.vue', t => {
  const h4Count = 3
  const wrapper = shallow(index, {
    mocks: {
      $route: {
        name: 'index'
      }
    }
  })
  t.is(wrapper.findAll('h4').length, h4Count)
})
