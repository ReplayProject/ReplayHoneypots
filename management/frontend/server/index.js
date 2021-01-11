require('dotenv').config()
// Logging setup
const log = require('debug')('sd:status')
const historyLog = require('debug')('sd:history')

log.log = console.log.bind(console)
historyLog.log = console.log.bind(console)

// Get dependencies
const express = require('express')
// const port = process.env.PORT || 8080
const passport = require('passport')
require('./modules/pass')
const authGuard = require('./modules/authGuard')
var fs = require('fs')
var https = require('https')
const key = fs.readFileSync('./server/cert/key.pem')
const cert = fs.readFileSync('./server/cert/cert.pem')
const db = require('./db.js')
const path = require('path')

// Start setting up express
var app = express()

// Enable Cross Origin Access & Run Helmet (security helping through http headers)
app.use(require('cors')())
app.use(require('helmet')())
app.use(require('cookie-parser')())

// Enable a valid CSP
const csp = require('helmet-csp')

app.use(
    csp({
        directives: {
            defaultSrc: [`'self'`],
            connectSrc: [`*`],
            imgSrc: [`https:`, `data:`, `*`],
            styleSrc: [`'self'`, `*`, `'unsafe-inline'`],
            scriptSrc: [`'self'`, `*`, `'unsafe-inline'`, `'unsafe-eval'`],
            fontSrc: [`*`],
        },
    })
)

// Parse body of requests
app.use(require('body-parser').urlencoded({ extended: true })) // application/x-www-form-urlencoded
app.use(require('body-parser').json()) // application/json
// app.use(require('body-parser').raw()) // raw (toggled off because we do not use it)

// Session middleware to allow "persistant" authentication
app.use(
    require('express-session')({
        secret: 'keyboard cat',
        resave: true,
        saveUninitialized: true,
    })
)

// Initialize Passport and restore authentication state, if any, from the session.
app.use(passport.initialize())
app.use(passport.session())

// Define authentication routes
app.use(require('./modules/authroutes'))

// Define actual routes
app.use(require('./modules/api'))

// Serve the actual frontend of the app & other routes (behind the auth guard)
app.get('/test', authGuard(), (req, res) =>
    res.send('you passed the authentication check')
)

// Set up the database design documents
db.setupDesignDocuments()
    .then(() => {
        db.importAllIndexes()
            .then(() => {
                db.importAllDefaults()
            })
            .catch( err => {
                console.log(err)
            })
    })
    .catch(err => {
        console.log(err)
        // Do nothing - error is logged upstream
    })

// Host the app's frontend on port 8080
const dist = path.join(__dirname, '../dist')
// Account for the Single Page Application (SPA) aspect of the app's design
app.use(
    require('connect-history-api-fallback')({
        logger: historyLog,
    })
)

// Serve application static files
app.use(require('serve-static')(dist, { index: ['index.html'] }))

// Handling deserialization errors here.
app.use(function (err, req, res, next) {
    if (err) {
        log('deserial handler', err)
        console.log('Cookie Invalidated')
        req.logout()
        return res
            .status(401)
            .send('You are not authenticated, your cookie has been removed')
    } else {
        next()
    }
})

const httpsServer = https.createServer({ key: key, cert: cert }, app)

httpsServer.listen(8443, () => {
    console.log('listening on 8443')
})
