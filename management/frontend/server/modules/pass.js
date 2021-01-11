const authLog = require('debug')('sd:auth')
authLog.log = console.log.bind(console)

const passport = require('passport')
const LocalStrategy = require('passport-local').Strategy
const SamlStrategy = require('passport-saml').Strategy

// Configured user database
var PouchDB = require('pouchdb')
var db = new PouchDB(process.env.DB_URL + '/users')

// Crypto libs
const crypto = require('crypto')
const computeHash = (x, s) =>
    crypto
        .createHash('sha256')
        .update(s + x)
        .digest('hex')

/**
 * Function to Check local password and stored hash
 */
function validPassword(attempt, hash, salt) {
    // console.log(computeHash(attempt, salt), hash)
    return computeHash(attempt, salt) === hash
}

// Configure Passport authenticated session persistence.

// In order to restore authentication state across HTTP requests, Passport needs
// to serialize users into and deserialize users out of the session.  The
// typical implementation of this is as simple as supplying the user ID when
// serializing, and querying the user record by ID from the database when
// deserializing.

// https://stackoverflow.com/questions/27637609/understanding-passport-serialize-deserialize

// TODO: revisit serialization when we have RBAC to add user data

passport.serializeUser(async (user, cb) => {
    try {
        authLog('serialize user id: ', user._id)
        cb(null, user._id)
    } catch (error) {
        authLog('serialize', error)
    }
})

passport.deserializeUser(async (id, cb) => {
    try {
        let user = await db.get(id)
        if (!user)
            return cb(new Error('no user found or user-id mismatch'), false, {
                message: 'User ID mismatch, or some other issue',
            })
        cb(null, user)
    } catch (error) {
        authLog('deserial', error)
    }
})

/**
 * Actual Authentication Logic
 * (using post body)
 */
passport.use(
    new LocalStrategy(
        {
            usernameField: 'username',
            passwordField: 'password',
        },
        async (username, password, done) => {
            authLog('looking for user ' + username)
            // Build selector
            const selectorBuild = {
                username: username,
            }
            const options = {
                selector: selectorBuild,
                limit: 1,
            }
            // Process user
            let user
            try {
                // Find user with username
                user = await db.find(options)
                if (user.docs.length === 0)
                    return done(null, false, { message: 'Incorrect username.' })
                user = user.docs[0]
                if (user.enabled === false)
                    return done(null, false, { message: 'User is disabled.' })
                if (user.local === false)
                    return done(null, false, { message: 'Not a local user.' })
                if (!validPassword(password, user.password, user.salt))
                    return done(null, false, { message: 'Incorrect password.' })
                // THIS INFORMATION SHOULD NEVER BE LOGGED, REMOVE IT HERE BEFORE PASSING TO DONE
                delete user.password
                delete user.salt
                // Move on
                return done(null, user)
            } catch (error) {
                if (!user) return done(null, false, { message: 'Incorrect username.' })
            }
        }
    )
)

passport.use(
    new SamlStrategy(
        {
            path: '/login/callback',
            entryPoint: process.env.SAML_URL,
            issuer: 'passport-saml',
        },
        async (profile, done) => {
            authLog('looking for user ' + profile.nameID)
            // Build selector
            const selectorBuild = {
                username: profile.nameID,
            }
            const options = {
                selector: selectorBuild,
                limit: 1,
            }
            // Process user
            let user
            try {
                // Find user with username
                user = await db.find(options)
                if (user.docs.length === 0)
                    return done(null, false, {
                        message: 'You do not have access to this application.',
                    })
                user = user.docs[0]
                if (user.enabled === false)
                    return done(null, false, { message: 'User is disabled.' })
                if (user.local === true)
                    return done(null, false, { message: 'Not a SAML user.' })
                // THIS INFORMATION SHOULD NEVER BE LOGGED, REMOVE IT HERE BEFORE PASSING TO DONE
                delete user.password
                delete user.salt
                // Move on
                return done(null, user)
            } catch (error) {
                if (!user) return done(null, false, { message: 'Incorrect username.' })
            }
            return done(null, profile)
        }
    )
)

// Export middleware to check for authentication state
module.exports = db
