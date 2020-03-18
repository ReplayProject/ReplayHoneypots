const authLog = require('debug')('sd:auth')
authLog.log = console.log.bind(console)

const express = require('express')
var router = express.Router()
const passport = require("passport");

// TODO: remove once login is integrated with frontend
router.get('/login', (req, res) => {
  return res.send(
    `<form action="/login" method="post">
        <div>
        <label>Username:</label>
        <input type="text" name="username"/><br/>
        </div>
        <div>
        <label>Password:</label>
        <input type="password" name="password"/>
        </div>
        <div>
        <input type="submit" value="Submit"/>
        <p>Hit back once logged in (admin:admin)</p>
        </div>
        </form><br>
        <br><br><a href="/test">Authed Link (requires auth)</a>`
  )
})

// Use URL params for passing user object here
router.post('/login', (req, res, next) => {
  passport.authenticate('local', (err, user, info) => {
    if (req.session.returnTo)
      authLog("Requested return to", req.session.returnTo)
    if (err) {
      authLog('login error: ', err)
      return next(err)
    }
    if (!user) {
      authLog('login request failed', info, user)
      return res.send(info)
      // return res.redirect('/login') // optional redirect back to login
    }
    req.logIn(user, err => {
      if (err) return next(err)
      authLog('successful login: ', user)

      // Follow saved state vs returning user object (with saved id)
      return req.session.returnTo
        ? res.redirect(req.session.returnTo)
        : res.send(user)
      // return res.redirect('/')
    })
  })(req, res, next)
})

/* Simple version of login route, can be used later probably
router.post(
    '/login',
    passport.authenticate('local', {
        successReturnToOrRedirect: '/',
        failureRedirect: '/login',
    })
)
*/

// passport.authenticate('local', { successReturnToOrRedirect: '/', failureRedirect: '/login' }))

// Perform a logout by removing the req.user property and clearing the login session (if any).
router.get('/logout', (req, res) => {
  authLog('logout: ', req.user)
  req.logout()
  res.redirect('/')
})

module.exports = router
