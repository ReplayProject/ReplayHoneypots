// https://github.com/HenningM/express-ws
// const termLog = require('debug')('sd:term')
// termLog.log = console.log.bind(console)

// const express = require('express')
// var router = express.Router()

// /**
//  * Sample Route to show off setting up Websocket endpoints
//  */
// router.ws('/echo', (ws, req) => {
//   ws.on('message', msg => {
//     termLog(msg)
//     ws.send(msg)
//   })
// })

// // Integrated Web Terminal Setup
// const pty = require('node-pty')
// const os = require('os')
// const shell = os.platform() === 'win32' ? 'powershell.exe' : 'bash'

// /**
//  * Host a websocket for the terminal interface
//  * Ran each time a new  websocket client connects
//  */
// router.ws('/', (ws, req) => {
//   termLog('Terminal Instance Started')
//   // Create terminal
//   let term = pty.spawn(shell, [], {
//     name: 'xterm-color',
//     cols: 80,
//     rows: 30,
//     cwd: process.env.HOME,
//     env: process.env
//   })
//   // Listen for client input
//   ws.on('message', data => {
//     if (data.includes('meta')) {
//       // TODO: decide if meta messages are needed
//       termLog('Meta Message!')
//       // Adjust for sizing
//       let rc = data.split(',').slice(1)
//       // term.resize(term, rc[0], rc[1]);
//     } else term.write(data)
//   })
//   // Listen on the terminal for output and send it to the client
//   term.on('data', data => {
//     ws.send(data)
//   })
//   // When socket disconnects, destroy the terminal
//   ws.on('close', () => {
//     term.destroy()
//     termLog('Goodbye :)')
//   })
//   // Log Errors that may come through
//   ws.on('error', msg => {
//     termLog(msg)
//   })
// })

// module.exports = router
