const authLog = require('debug')('sd:auth')
authLog.log = console.log.bind(console)

const express = require('express')
var router = express.Router()
const passport = require('passport')

// Import other modules
const authGuard = require('./authGuard')
const users = require('./pass')

/**
 * Used to check if the user is authenticated on every page change on the frontend
 */
router.get('/user', authGuard(), async (req, res) => {
    try {
        authLog('user passed auth check')
        if (
            req.session &&
            req.session.passport &&
            req.session.passport.user &&
            req.session.passport.user != ''
        )
            res.send({ userId: req.session.passport.user })
        else throw Error('ID Mismatch')
    } catch (error) {
        authLog('/user guard', error)
        res.send({ userID: 'undefined' })
    }
})

/**
 * Logs the user in with verbose logging
 *
 * Use URL params for passing user object here
 */
router.post('/login', (req, res, next) => {
    passport.authenticate('local', (err, user, info) => {
        // Logging return to sessions
        if (req.session.returnTo) authLog('Requested return to', req.session.returnTo)

        if (err) {
            authLog('login error: ', err)
            return next(err)
        }

        if (!user) {
            authLog('login request failed', info, user)
            return res.status(400).send([user, 'Cannot log in', info])
        }

        req.logIn(user, err => {
            if (err) return next(err)
            authLog('successful login: ', user)
            res.send(user._id)
        })
    })(req, res, next)
})

router.get(
    '/login/sso',
    passport.authenticate('saml', {
        successReturnToOrRedirect: '/',
    })
)

router.post('/login/callback', (req, res, next) => {
    passport.authenticate('saml', (err, user, info) => {
        // Logging return to sessions
        if (req.session.returnTo) authLog('Requested return to', req.session.returnTo)

        if (err) {
            authLog('login error: ', err)
            return next(err)
        }
        if (!user) {
            authLog('login request failed', info, user)
            res.redirect('/')
            // return res.status(400).send([user, 'Cannot log in', info])
        } else {
            req.logIn(user, err => {
                if (err) return next(err)
                authLog('successful login: ', user)
                res.redirect('/')
            })
        }
    })(req, res, next)
})

// Perform a logout by removing the req.user property and clearing the login session (if any).
router.get('/logout', (req, res) => {
    authLog('logout:', req.session.passport.user)
    req.logout()
    res.send('logged out')
})

module.exports = router
