const authLog = require('debug')('sd:auth')
authLog.log = console.log.bind(console)

const passport = require('passport')
const LocalStrategy = require('passport-local').Strategy

// Fake user database
const users = [
  {
    username: 'admin',
    hash: 'admin'
  },
  {
    username: 'seth',
    hash: 'notseth'
  }
]

/**
 * Function to Check local password and stored hash
 */
function validPassword (attempt, hash) {
  return attempt === hash
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
