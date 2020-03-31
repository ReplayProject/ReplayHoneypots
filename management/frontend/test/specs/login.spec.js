import { shallowMount } from '@vue/test-utils'
import test from 'ava'
import index from '../../client/src/pages/login.vue'

test('login.vue', t => {
  const wrapper = shallowMount(index, {
    mocks: {
      $route: {
        name: 'login'
      }
    }
  })
  let html = wrapper.html()
  t.truthy(html.includes('Sign In'))
  t.truthy(html.includes('Username'))
  t.truthy(html.includes('Password'))
})
