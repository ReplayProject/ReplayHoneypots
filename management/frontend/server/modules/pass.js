const authLog = require('debug')('sd:auth')
authLog.log = console.log.bind(console)

const passport = require('passport')
const LocalStrategy = require('passport-local').Strategy

// Configured user database
const fs = require('fs')
const useRootConfig = fs.existsSync(process.env.AUTH_FILE)
const path = useRootConfig
  ? process.env.AUTH_FILE
  : process.env.AUTH_FILE_FALLBACK

authLog('using config: ' + path)

const { salt, users } = require(path)
const crypto = require('crypto')
const computeHash = x =>
  crypto
    .createHash('sha256')
    .update(salt + x)
    .digest('hex')

/**
 * Function to Check local password and stored hash
 */
function validPassword (attempt, hash) {
  return computeHash(attempt) === hash
}

// Configure Passport authenticated session persistence.

// In order to restore authentication state across HTTP requests, Passport needs
// to serialize users into and deserialize users out of the session.  The
// typical implementation of this is as simple as supplying the user ID when
// serializing, and querying the user record by ID from the database when
// deserializing.

passport.serializeUser((user, cb) => {
  let foundUser = users.find(x => x.username == user.username)
  foundUser.id = require('uuid').v4() // generate and ID
  authLog('storing user: ', foundUser)
  cb(null, user.id)
})

passport.deserializeUser((id, cb) => {
  authLog('retrieving user', id)
  let user = users.find(x => x.id == id) // fetch based on ID
  if (!user)
    return cb(new Error('no user found or user-id mismatch'), false, {
      message: 'User ID mismatch, or some other issue'
    })
  authLog('successful retrieval of user', id)
  cb(null, user)
})

/**
 * Actual Authentication Logic
 * (using post body)
 */
passport.use(
  new LocalStrategy(
    {
      usernameField: 'username',
      passwordField: 'password'
    },
    (username, password, done) => {
      authLog('looking for user: ', username)
      // Find user with username
      let user = users.find(x => x.username == username)
      if (!user) return done(null, false, { message: 'Incorrect username.' })
      if (!validPassword(password, user.hash))
        return done(null, false, { message: 'Incorrect password.' })
      return done(null, user)
    }
  )
)

// Export middleware to check for authentication state
module.exports = users
