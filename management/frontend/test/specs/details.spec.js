import { shallowMount, createLocalVue } from '@vue/test-utils'
import test from 'ava'
import details from '../../client/src/pages/details.vue'
import sinon from 'sinon'
import store from '../store'

const localVue = createLocalVue()
import VueGoodTablePlugin from 'vue-good-table'
// import 'vue-good-table/dist/vue-good-table.css'
localVue.use(VueGoodTablePlugin)

localVue.filter('formatDBName', value => {
    if (!value) return ''
    value = value.toString()
    return (
        value
            .split('_')
            .map(x => x.replace(/^\w/, c => c.toUpperCase()))
            .join(' ') + ' Logs'
    )
})

test('details.vue', t => {
    const spy = sinon.spy()
    const createIndex = sinon.stub().returns({ result: 'exists' })
    const find = sinon.stub().returns({ docs: [] })

    const wrapper = shallowMount(details, {
        localVue,
        mocks: {
            $route: {
                name: 'details',
                params: {
                    device: 'yogi',
                },
            },
            $store: store,
            $Progress: {
                start: spy,
                finish: spy,
            },
            $pouch: {
                createIndex,
                find,
            },
        },
    })
    let html = wrapper.html()
    t.truthy(html.includes('Yogi Logs'))
    t.truthy(html.includes('Total Logs'))
})
