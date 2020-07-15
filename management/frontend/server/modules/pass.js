const authLog = require('debug')('sd:auth')
authLog.log = console.log.bind(console)

const passport = require('passport')
const LocalStrategy = require('passport-local').Strategy

// Configured user database
var PouchDB = require('pouchdb')
var db = new PouchDB(process.env.DB_URL + '/frontend_users')
let salt = null

// Get seed file
const fs = require('fs')
const useRootConfig = fs.existsSync(process.env.AUTH_FILE)
const path = useRootConfig
    ? process.env.AUTH_FILE
    : '../../' + process.env.AUTH_FILE_FALLBACK

async function setupDB() {
    try {
        let dbinfo = await db.info()
        // Do we need to seed the database with data
        if (dbinfo.doc_count == 0) {
            authLog('New', dbinfo.db_name, 'created, adding default admin user')

            // TODO: real admin accounts admin, notseth
            let resp = await db.bulkDocs(require(path).documents)
            authLog(resp)
        } else {
            authLog('Using existing', dbinfo.db_name, 'configuration')
        }

        // load the data into memory
        salt = (await db.get('salt')).value
    } catch (error) {
        authLog(error)
    }
}

setupDB()

const crypto = require('crypto')
const computeHash = x =>
    crypto
        .createHash('sha256')
        .update(salt + x)
        .digest('hex')

/**
 * Function to Check local password and stored hash
 */
function validPassword(attempt, hash) {
    return computeHash(attempt) === hash
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
        authLog('deserialize retrieved user', id)
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
            authLog('looking for user-' + username)
            let user
            try {
                // Find user with username
                user = await db.get('user-' + username)
                if (!validPassword(password, user.hash))
                    return done(null, false, { message: 'Incorrect password.' })
                return done(null, user)
            } catch (error) {
                if (!user) return done(null, false, { message: 'Incorrect username.' })
            }
        }
    )
)

// Export middleware to check for authentication state
module.exports = db
