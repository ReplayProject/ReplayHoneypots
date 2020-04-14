// Logging setup
const log = require('debug')('sd:status')
const historyLog = require('debug')('sd:history')

log.log = console.log.bind(console)
historyLog.log = console.log.bind(console)

// Get dependencies
const express = require('express')
const port = process.env.PORT || 8080
const passport = require('passport')
require('./modules/pass')
const authGuard = require('./modules/authGuard')

// Start setting up express
var app = express()

// Enable Cross Origin Access & Run Helmet (security helping through http headers)
app.use(require('cors')())
app.use(require('helmet')())
app.use(require('cookie-parser')())

// Parse body of requests
app.use(require('body-parser').urlencoded({ extended: true })) // application/x-www-form-urlencoded
app.use(require('body-parser').json()) // application/json
// app.use(require('body-parser').raw()) // raw (toggled off because we do not use it)

// Session middleware to allow "persistant" authentication
app.use(
  require('express-session')({
    secret: 'keyboard cat',
    resave: true,
    saveUninitialized: true
  })
)

// Initialize Passport and restore authentication state, if any, from the session.
app.use(passport.initialize())
app.use(passport.session())

// Define authentication routes
app.use(require('./modules/authroutes'))

// Define actual routes

// Serve the actual frontend of the app & other routes (behind the auth guard)
app.get('/test', authGuard(), (req, res) =>
  res.send('you passed the authentication check')
)

// Host the app's frontend on port 8080
const path = require('path')
const dist = path.join(__dirname, '../dist')
// Account for the SPA portion of the app
app.use(
  require('connect-history-api-fallback')({
    logger: historyLog
  })
)
// Serve application files
app.use(require('serve-static')(dist, { index: ['index.html'] }))

// Handling deserialization errors here.
app.use(function (err, req, res, next) {
  if (err) {
    console.log('Cookie Invalidated')
    req.logout()
    return res
      .status(401)
      .send('You are not authenticated, your cookie has been removed')
  } else {
    next()
  }
})

// listen for frontend requests :)
app.listen(port, () => log('Frontend listening on', port))
