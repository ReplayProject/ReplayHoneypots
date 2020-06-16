import { shallowMount } from '@vue/test-utils'
import test from 'ava'
import index from '../../client/src/pages/login.vue'
import sinon from 'sinon'

test('loadPage', t => {
    const wrapper = shallowMount(index, {
        mocks: {
            $route: {
                name: 'login',
            },
        },
    })
    let html = wrapper.html()
    t.truthy(html.includes('Sign In'))
    t.truthy(html.includes('Username'))
    t.truthy(html.includes('Password'))
})

test('testInvalidLogin', async t => {
    const post = sinon.stub().rejects('error with login')
    const show = sinon.spy()
    const push = sinon.spy()

    const wrapper = shallowMount(index, {
        mocks: {
            $route: {
                name: 'login',
            },
            axios: { post },
            $toasted: { show },
            $router: { push },
        },
    })

    wrapper.setData({ username: '', password: '' })

    wrapper.find({ ref: 'form' }).trigger('submit')

    await tick()
    t.truthy(post.called, 'axios post was called for login')
    t.deepEqual(
        post.args[0][1],
        {
            username: '',
            password: '',
        },
        ' username and password were empty'
    )

    t.truthy(show.called, 'error auth notification called')
    t.truthy(
        show.args[0][0].includes('Failed to Login. Error:'),
        'authentication "passed"'
    )
})

// Helper function returns a promise that resolves after all other promise mocks,
// even if they are chained like Promise.resolve().then(...)
// Technically: this is designed to resolve on the next macrotask
function tick() {
    return new Promise(resolve => {
        setTimeout(resolve, 0)
    })
}

test('testValidLogin', async t => {
    const post = sinon.stub().resolves('success')
    const show = sinon.spy()
    const push = sinon.spy()

    const wrapper = shallowMount(index, {
        mocks: {
            $route: {
                name: 'login',
            },
            axios: { post },
            $toasted: { show },
            $router: { push },
        },
    })

    // Set credentials
    wrapper.setData({ username: 'admin', password: 'notadminpassword' })

    // Submit
    wrapper.find({ ref: 'form' }).trigger('submit')
    await tick()

    // Check everything was called
    t.truthy(post.called, 'axios post was called for login')
    t.deepEqual(
        post.args[0][1],
        {
            username: 'admin',
            password: 'notadminpassword',
        },
        ' username and password were the same'
    )

    t.truthy(show.called, 'succesful auth notification called')
    t.is(show.args[0][0], 'Authenticated', 'authentication "passed"')

    t.truthy(push.called, 'router push to dashboard')
    t.is(push.args[0][0], '/dashboard', 'was redirected to dashboard')
})
