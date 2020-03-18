<template>
  <main
    class="w-100 ph3-m ph3-l"
    :class="{
      'w-75-m': $route.name != 'overview',
      'w-75-l': $route.name != 'overview'
    }"
  >
    <component-title>Terminal Instance</component-title>
    <hr class="o-20" />
    <div v-if="isSocketCapable" class="" ref="term"></div>
    <p v-else class="f3">
      Your browser cannot run the technology required for this feature
      (websockets)
    </p>
  </main>
</template>

<script>
import componentTitle from '../components/title'

import { Terminal } from 'xterm'
import { WebLinksAddon } from 'xterm-addon-web-links'
import { FitAddon } from 'xterm-addon-fit'
import { AttachAddon } from 'xterm-addon-attach'

export default {
  name: 'terminal',
  components: {
    componentTitle
  },
  data () {
    return {
      socket: null,
      terminal: null,
      fitAddon: null
    }
  },
  computed: {
    isSocketCapable () {
      return window.WebSocket
    }
  },
  methods: {
    connect () {
      return new Promise(function (resolve, reject) {
        let socket = new WebSocket(process.env.WS_URL)
        socket.onclose = function () {
          document.body.style.backgroundColor = null
          // alert('connection dies')
          console.log('Connection to terminal is gone.')
        }
        socket.onopen = function () {
          document.body.style.backgroundColor = '#cfc'
          resolve(socket)
        }
        socket.onerror = function (err) {
          document.body.style.backgroundColor = null
          reject(err)
        }
      })
    },
    onResize () {
      if (this.$refs.term && this.fitAddon) {
        this.fitAddon.fit()
        this.socket.send(
          'meta,' + Object.values(this.fitAddon.proposeDimensions())
        )
      }
    }
  },

  async mounted () {
    // Sizing Stuff
    this.$nextTick(() => {
      window.addEventListener('resize', this.onResize)
    })

    this.terminal = new Terminal({
      cursorBlink: true
    })

    // Copy and paste handlers
    // this.terminal.attachCustomKeyEventHandler(async e => {
    //   try {
    //     // Custom Copy
    //     if (e.ctrlKey && e.key === 'Insert') {
    //       // await navigator.clipboard.writeText('wonky')
    //       document.execCommand('copy');
    //       console.log('copied')
    //     }
    //     // Custom Paste
    //     else if (e.shiftKey && e.key === 'Insert') {
    //       // const text = await navigator.clipboard.readText()
    //       // console.log('Pasted content: ', text)
    //       this.terminal.focus();
    //       document.execCommand('paste');
    //       console.log(11)
    //     }
    //   } catch (err) {
    //     console.error('Failed to copy/paste from terminal: ', err)
    //   }
    // })

    // Load WebLinksAddon on terminal, this is all that's needed to get web links
    // working in the terminal.
    this.terminal.loadAddon(new WebLinksAddon())
    this.fitAddon = new FitAddon()
    this.terminal.loadAddon(this.fitAddon)
    this.terminal.open(this.$refs.term)
    this.fitAddon.fit()

    // https://github.com/xtermjs/xterm.js

    try {
      this.socket = await this.connect()
      this.onResize()
      if (this.socket.readyState != WebSocket.OPEN)
        console.log('Socket connection issue')
      const attachAddon = new AttachAddon(this.socket)
      this.terminal.loadAddon(attachAddon)
    } catch (error) {
      // TODO: professionalism
      console.log('ooops ', error)
    }
  }
}
</script>

<style scoped lang="scss">
@import 'xterm/css/xterm.css';
</style>
