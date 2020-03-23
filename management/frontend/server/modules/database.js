const PouchDB = require('pouchdb')
const httpPouch = require('express-pouchdb')

const TempPouchDB = PouchDB.defaults({
  // db: require("memdown"),
  prefix: './.data/' // db stored in .data folder
})

module.exports = httpPouch(TempPouchDB)

/**
   *  {
    mode: "fullCouchDB", // specified for clarity. It's the default so not necessary.
    overrideMode: {
      exclude: [
        "routes/authentication",
        // disabling the above, gives error messages which require you to disable the
        // following parts too. Which makes sense since they depend on it.
        "routes/authorization",
        "routes/session"
      ]
    }
  }
   */
