const express = require('express')
const router = express.Router()
const authGuard = require('./authGuard')
const db = require('../db.js')

const API_BASE = '/api/v1/'

// Crypto function for user updates / creates
const crypto = require('crypto')
const { request } = require('express')
const { role } = require('../db.js')
const computeHash = (x, s) =>
    crypto
        .createHash('sha256')
        .update(s + x)
        .digest('hex')

/**
 * This function is used purely to check login status
 * It returns the record of the logged in user
 */
router.get(API_BASE + 'session', authGuard(), async (req, res) => {
    const results = []

    db.user.get(req.session.passport.user)
        .then( userResponse => {
            delete userResponse.password
            delete userResponse.salt
            results.push(userResponse)
            db.role.get(userResponse.role)
                .then( roleResponse => {
                    results.push(roleResponse)
                    res.send(results)
                })
                .catch( roleError => {
                    console.log(roleError)
                    res.statusCode = 500
                    res.send(roleError)
                })
        })
        .catch( userError => {
            console.log(userError)
            res.statusCode = 500
            res.send(userError)
        })
})

router.get(API_BASE + 'admin_logs', authGuard(), async (req, res) => {
    if(await checkUserPermission(req, res, "adminLogs", 1)) {
        await genericGetter(req, res, db.adminLog, '_id', 'admin_logs')
    }
})

router.post(API_BASE + 'admin_logs', authGuard(), async (req,res) => {
    //Don't need permissions to add logs since they're added from other actions
    // Create the Log
    genericPoster(req, res, db.adminLog, 'admin_logs')
})

router.get(API_BASE + 'logs', authGuard(), async (req, res) => {
    if(await checkUserPermission(req, res, "traffLogs", 1)) {
        await genericGetter(req, res, db.log, 'uuid', 'logs')
    }
})

router.get(API_BASE + 'logDBInfo', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "traffLogs", 1)) {
        try {
            let results = await db.log.info()
            res.send(results)
        } catch (err) {
            console.log('Error in logsDBInfo endpoint: ' + err)
            res.statusCode = 500
            res.send(err)
        }
    }
})

router.get(API_BASE + 'alerts', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "alerts", 1)) {
        await genericGetter(req, res, db.alert, 'hostname', 'alerts')
    }
})

router.get(API_BASE + 'alertsFeed', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "alerts", 1)) {
        var changes = db.alert.changes({
            since: 'now',
            live: true,
            include_docs: true,
        })

        changes.on('change', change => {
            console.log(change)
            res.write(JSON.stringify({ type: 'change', data: change }))
        })

        changes.on('complete', info => {
            console.log(info)
            res.send(res.write(JSON.stringify({ type: 'complete', data: info })))
        })

        changes.on('error', err => {
            console.log(err)
            res.write(JSON.stringify({ type: 'error', data: err }))
        })
    }
})

router.get(API_BASE + 'hostInfo', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "traffLogs", 1)) {
        const optionsBuild = {
            include_docs: false,
            reduce: true,
            // group: true,
            group_level: 1,
        }

        if (req.query.startkey) {
            optionsBuild.startkey = JSON.parse(req.query.startkey)
        }

        if (req.query.endkey) {
            optionsBuild.endkey = JSON.parse(req.query.endkey)
        }

        if (req.query.specificity) {
            optionsBuild.group_level = parseInt(req.query.specificity)
        }

        db.log
            .query(`timespans/hosttime`, optionsBuild)
            .then(function (response) {
                res.send(response)
            })
            .catch(function (err) {
                res.statusCode = 400
                res.send(err)
            })
    }
})

// ------------ CONFIGS ------------

router.get(API_BASE + 'config', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "configs", 1)) {
        await genericGetter(req, res, db.config, '_id', 'config')
    }
})

router.post(API_BASE + 'config', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "configs", 2)) {
        db.config
            .post(req.body)
            .then(function (response) {
                res.send(response)
            })
            .catch(function (err) {
                res.statusCode = 400
                res.send(err)
            })
    }
})

router.get(API_BASE + 'config/:configId', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "configs", 1)) {
        let results = await db.config.get(req.params.configId)
        res.send(results)
    }
})

router.put(API_BASE + 'config/:configId', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "configs", 2)) {
        let updatedConfig = req.body
        db.config
            .get(req.params.configId)
            .then(function (config) {
                updatedConfig._id = config._id
                updatedConfig._rev = config._rev
                return db.config.put(updatedConfig)
            })
            .then(function (response) {
                res.send(response)
            })
            .catch(function (err) {
                res.statusCode = 400
                res.send(err)
            })
    }
})

router.delete(API_BASE + 'config/:identifier', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "configs", 2)) {
        let dbMap = new Map()
        dbMap.set(db.honeypot, "config_id")
        genericDelete(req, res, db.config, dbMap, "configDefault", 'config')
    }
})

// ------------ HONEYPOTS ------------

/**
 * This function returns all non-deleted honeypots
 * that are assigned to auth groups that the currently authenticated
 * user has access to at a permissions level above 0. Utilizes the session
 * token to find logged in user.
 */
router.get(API_BASE + 'honeypot', authGuard(), async (req, res) => {
    const constraints = []
    // Create the "no deleted honeypots" constraint
    constraints.push(buildConstraint('deleted', 'equals', false))
    // Create the "only honeypots in auth groups that user can see" constraint
    const viewableGroups = await getViewableAuthorizationGroups(req)
    constraints.push(buildConstraint('auth_group_id', 'in', viewableGroups))
    // Submit query
    await genericGetter(req, res, db.honeypot, '_id', 'honeypot', undefined, constraints)
})

/**
 * This function returns the single honeypot record with the given id.
 * The honeypot is only returned if the authenticated user has level 1 or 2 access
 * to devices, and level 1 or 2 access to the specific authorization group which the device inhabits.
 */
router.get(API_BASE + 'honeypot/:identifier', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "devices", 1)) {
        let results = await db.honeypot.get(req.params.honeypotId)
        res.send(results)
    }
})

router.get(API_BASE + 'honeypotByTag', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "devices", 1)) {
        let options = {
            selector: {
                tags: {
                    $elemMatch: {
                        $eq: req.query.tag
                    }
                }
            },
            sort: [{ hostname: 'asc' }],
            skip: 0,
            fields: [],
        }
        try {
            let results = await db.honeypot.find(options)
            res.send(results)
        } catch (err) {
            console.log('Error in honeypotByTag endpoint: ' + JSON.stringify(err))
            res.statusCode = 500
            res.send(err)
        }
    }
})

/**
 * This function updates the honeypot with the given id to include
 * the given new body of data. Changes are only allowed if the user has level 2 access to
 * devices AND has level 2 access to the specific auth group which the device inhabits.
 */
router.put(API_BASE + 'honeypot/:identifier', authGuard(), async (req, res) => {
    // Needs to be rebuilt to support the "exceptions" based permissions
    if (await checkUserPermission(req, res, "devices", 2)) {
        if (!req.body) {
            console.log("A put to honeypot was attempted with no data provided. Failing.")
            res.statusCode = 400
            res.send("A put to honeypot was attempted with no data provided. Failing.")
            return
        }
        // Update the honeypot
        genericPutter(req, res, db.honeypot, '_id', 'honeypot')
    }
})

// ------------ ROLES ------------

router.get(API_BASE + 'role', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "roles", 1)) {
        await genericGetter(req, res, db.role, '_id', 'role')
    }
})

router.post(API_BASE + 'role', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "roles", 2)) {
        // Create the role
        genericPoster(req, res, db.role, 'role')
    }
})

router.get(API_BASE + 'role/:roleId', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "roles", 1)) {
        db.role.get(req.params.roleId).then(function (response) {
            res.send(response)
        })
            .catch(function (err) {
                res.statusCode = 400
                res.send(err)
            })
    }
})

router.put(API_BASE + 'role/:identifier', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "roles", 2)) {
        // Update the role
        genericPutter(req, res, db.role, '_id', 'role')
    }
})

router.delete(API_BASE + 'role/:identifier', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "roles", 2)) {
        var selectorBuild = {}

        //select the users whose role field is the identifier
        selectorBuild['role'] = req.params.identifier

        let options = {
            selector: selectorBuild,
        }

        try {
            let results = await db.user.find(options)

            if(results.docs.length !== 0) {
                console.log('Cannot delete A role with users assigned to it')
                res.statusCode = 400
                res.send("Cannot delete a role with a user assigned to it")
            } else {
                let dbMap = new Map()
                dbMap.set(db.user, "role")
                genericDelete(req, res, db.role, dbMap, "auditorDefault", 'role')
            }

        } catch (error) {
            console.log('Error in user endpoint: ' + error)
            res.statusCode = 500
            res.send(error)
        }
    }
})

// ------------ USERS ------------

// Deletes the attributes from the user objects
// that contain secure information
// before data is ever returned from API
function sterilizeUsers(result) {
    for (let i = 0; i < result.docs.length; i++) {
        delete result.docs[i].password
        delete result.docs[i].salt
    }
    return result
}

// Validates any passed in data object meant to be a user
// to ensure that we catch any formatting issues at this layer.
function validateUser(data) {
    if (data.username == undefined || data.password == undefined) {
        console.log("Validate User: Bad login info")
        return false
    }
    if (data.firstname == undefined || data.lastname == undefined) {
        console.log("Validate User: Bad Name Info")
        return false
    }
    if (data.role === undefined || data.local === undefined || data.enabled === undefined) {
        console.log("Validate User: Bad Perms Data")
        return false
    }
    let roleResponse = db.role.get(data.role)
    if(roleResponse === undefined) {
        console.log("Validate User: Bad Role Data")
        return false
    }
    return true
}

// Validates Auth Group object
function validateAuthGroup(data) {
    if (data._id == undefined) {
        console.log("Validate Auth Group: Bad Name Info")
        return false
    }
}

// Creates a salt for new users
function createSalt() {
    return crypto.randomBytes(128).toString('base64')
}

// Used for getting user records. Accepts parameters including
// username, skip, sort, and limit specifications. If none are
// specified, returns all users.
router.get(API_BASE + 'user', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "users", 1)) {
        await genericGetter(req, res, db.user, '_id', 'user', sterilizeUsers)
    }
})

router.get(API_BASE + 'user/:userId', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "users", 1)) {
        db.user.get(req.params.userId).then(function (response) {
            res.send(response)
        })
            .catch(function (err) {
                res.statusCode = 400
                res.send(err)
            })
    }
})

router.post(API_BASE + 'user', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "users", 2)) {
        // Hash the password
        req.body.salt = createSalt()
        req.body.password = computeHash(req.body.password, req.body.salt)
        // Validate the user
        if (validateUser(req.body) === false) {
            console.log("User Post did not pass validation.")
            res.statusCode = 400
            res.send("A post to user was attempted with invalid data. Failing.")
            return
        }
        // Create the user
        genericPoster(req, res, db.user, 'user')
    }
})


router.put(API_BASE + 'user/:identifier', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "users", 2)) {
        // We need to do some additional checking here due to the way we handle passwords
        // The request body will not include a password unless it is being reset
        // In the case of it being blank, we need to fill in the current password
        // and in the case of it having contents, we need to hash it
        // and in either case, we need to fill in the salt
        if (!req.body) {
            console.log("A put to user was attempted with no data provided. Failing.")
            res.statusCode = 400
            res.send("A put to user was attempted with no data provided. Failing.")
            return
        }

        db.user.get(req.params.identifier).then(function (object) {
            // User cannot update own role
            let userResponse = db.user.get(req.session.passport.user)
            if (userResponse._id === req.params.identifier) {
                if(userResponse.role !== req.body.role) {
                    console.log("User Put cannot update own role")
                    res.statusCode = 400
                    res.send("A put to user was attempted with invalid data. Failing")
                    return
                }
                //User cannot disable themselves
                if(userResponse.enabled !== req.body.enabled) {
                    console.log("User cannot disable themseles")
                    req.statusCode = 400
                    res.send("A put to user was attempted with invalid data. Failing")
                    return
                }
            }
            // Generate/set the password and salt
            if (!req.body.password) {
                req.body.password = object.password
            } else {
                req.body.password = computeHash(req.body.password, object.salt)
            }
            req.body.salt = object.salt
            // Validate the user
            if (validateUser(req.body) === false) {
                console.log("User Put did not pass validation.")
                res.statusCode = 400
                res.send("A put to user was attempted with invalid data. Failing.")
                return
            }
            // Update the user
            genericPutter(req, res, db.user, '_id', 'user')
        }).catch(function (getError) {
            console.log(getError)
            res.statusCode = 500
            res.send(getError)
        })
    }
})

router.delete(API_BASE + 'user/:identifier', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "users", 2)) {
        //check if deleting self
        let userResponse = db.user.get(req.session.passport.user)
        if (userResponse._id === req.params.identifier) {
                console.log("User delete cannot delete self")
                res.statusCode = 400
                res.send("A user attempted to delete self. Failing")
                return
        } else {
            let dbMap = new Map()
            genericDelete(req, res, db.user, dbMap, "", 'user')
        }
    }
})

//------------ TAGS --------------
router.get(API_BASE + 'tag', authGuard(), async (req, res) => {
    const optionsBuild = {
        reduce: true,
        group_level: 1,
    }

    db.honeypot
        .query(`uniqueTags/uniqueTags`, optionsBuild)
        .then(function (response) {
            const tags = []
            for (let i = 0; i < response.rows.length; i++) {
                tags.push(response.rows[i].key)
            }
            res.send(tags)
        })
        .catch(function (err) {
            console.log(err)
            res.statusCode = 400
            res.send(err)
        })
})

//-----------AUTH GROUPS---------
router.get(API_BASE + 'auth_group', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "authGroupsMgmt", 1)) {
        await genericGetter(req, res, db.auth_group, '_id', 'auth_group')
    }
})
 
router.get(API_BASE + 'auth_group/:identifier', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "authGroupsMgmt", 1)) {
        let results = await db.auth_group.get(req.params.authGroupId)
        res.send(results)
    }
})

router.post(API_BASE + 'auth_group', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "authGroupsMgmt", 2)) {
        // Create the auth group
        genericPoster(req, res, db.auth_group, 'auth group')
    }
})

router.delete(API_BASE + 'auth_group/:identifier', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "authGroupsMgmt", 2)) {
        var selectorBuild = {}

        //select the Devices whose auth group field is the identifier
        selectorBuild['auth_group_id'] = req.params.identifier

        let options = {
            selector: selectorBuild,
        }

        try {
            let results = await db.honeypot.find(options)

            if (results.docs.length !== 0) {
                console.log('Cannot delete an auth group with devices assigned to it')
                res.statusCode = 400
                res.send("Cannot delete an auth group with devices assigned to it")
            } else {
                let dbMap = new Map()
                genericDelete(req, res, db.auth_group, dbMap, undefined, 'auth group')
            }

        } catch (error) {
            console.log('Error in honeypot endpoint: ' + error)
            res.statusCode = 500
            res.send(error)
        }
    }
})

//-----------Metrics---------
router.get(API_BASE + 'metrics', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "metrics", 1)) {
        const optionsBuild = {
            reduce: true,
            group_level: 1,
        }

        if (req.query.sort !== undefined) {
            optionsBuild.sort = JSON.parse(req.query.sort)
        }
    
        if (req.query.skip !== undefined) {
            optionsBuild.skip = parseInt(req.query.skip)
        }
    
        if (req.query.limit !== undefined) {
            optionsBuild.limit = parseInt(req.query.limit)
        }
    
        if (req.query.fields !== undefined) {
            optionsBuild.fields = JSON.parse(req.query.fields)
        }

        db.metric
            .query(`mostRecentMetrics/mostRecentMetrics`, optionsBuild)
            .then(function (response) {
                // Need to do some processing here because views return different
                // data structures than the normal finds
                //
                // Resassemble all docs into standard format
                // While doing that, check against the given params
                // for filtered tag and auth group
                //
                // PULL HONEYPOTS IN HERE AND FILTER BY TAG AND GROUP
                const docs = []
                for (let i = 0; i < response.rows.length; i++) {
                    // If the tag is filtered and the object matches it, or no filter was given
                    const matchesTag = (req.query.tag !== undefined && req.query.tag === response.rows[i].value) || (req.query.tag === undefined || req.query.tag === "")
                    // If the auth group is filtered and the object matches it, or no filter was given
                    const matchesAuth = (req.query.auth !== undefined && req.query.auth === response.rows[i].value) || (req.query.auth === undefined || req.query.auth === "")
                    if (matchesTag === true && matchesAuth === true) {
                        docs.push(response.rows[i].value)
                    }
                }
                // Swap the field names to match expected format
                delete response.rows
                response.docs = docs
                res.send(response)
            })
            .catch(function (err) {
                res.statusCode = 400
                res.send(err)
            })
    }
})

router.get(API_BASE + 'metricsByUUID', authGuard(), async (req, res) => {
    if (await checkUserPermission(req, res, "metrics", 1)) {
        await genericGetter(req, res, db.metric, 'uuid', 'metrics')
    }
})

module.exports = router

// GENERIC FUNCTIONS FOR ABSTRACTION

async function genericGetter(request, response, database, identifyingFieldName, endpointName, resultsProcessing, constraints) {
    var selectorBuild = {}

    if (request.query.identifier !== undefined) {
        selectorBuild[identifyingFieldName] = request.query.identifier
    }

    selectorBuild = buildSelectorFromConstraints(selectorBuild, constraints)

    let options = {
        selector: selectorBuild,
    }

    if (request.query.sort !== undefined) {
        options.sort = JSON.parse(request.query.sort)
    }

    if (request.query.skip !== undefined) {
        options.skip = parseInt(request.query.skip)
    }

    if (request.query.limit !== undefined) {
        options.limit = parseInt(request.query.limit)
    } else {
        options.limit = 1000000
    }

    if (request.query.fields !== undefined) {
        options.fields = JSON.parse(request.query.fields)
    }

    try {
        let results = await database.find(options)
        if (resultsProcessing !== undefined) {
            results = resultsProcessing(results)
        }
        response.send(results)
    } catch (err) {
        console.log('Error in ' + endpointName + ' endpoint: ' + JSON.stringify(err))
        response.statusCode = 500
        response.send(err)
    }
}

function genericPutter(req, res, database, endpointName) {
    if (!req.body) {
        console.log("A put to " + endpointName + " was attempted with no data provided. Failing.")
        res.statusCode = 400
        res.send("A put to " + endpointName + "  was attempted with no data provided. Failing.")
        return
    }

    let requestData = req.body
    // Get the object, move the revision number, and update
    database.get(req.params.identifier).then(function (object) {
        requestData._id = object._id
        requestData._rev = object._rev
        database.put(requestData).then(function (putResponse) {
            res.send(putResponse)
        }).catch(function (putError) {
            res.statusCode = 500
            res.send(putError)
        })
    }).catch(function (getError) {
        res.statusCode = 500
        res.send(getError)
    })
}

function genericPoster(req, res, database, endpointName) {
    if (!req.body) {
        console.log("A post to " + endpointName + " was attempted with no data provided. Failing.")
        res.statusCode = 400
        res.send("A post to " + endpointName + "  was attempted with no data provided. Failing.")
        return
    }

    let requestData = req.body

    database.post(requestData)
        .then(function (postResponse) {
            console.log(postResponse)
            res.send(postResponse)
        })
        .catch(function (postError) {
            console.log(postError)
            res.statusCode = 500
            res.send(postError)
        })
}

function genericDelete(req, res, database, otherDBToIdMap, defaultReplaceValue, endpointName) {
    database.get(req.params.identifier)
    .then(function (getResponse) {
        database.remove(getResponse)
        .then(async function (deleteResponse) {
            let dbsToCheck = otherDBToIdMap.keys()
            for(let otherDB of dbsToCheck) {
                let fieldName = otherDBToIdMap.get(otherDB)

                otherDB.allDocs({include_docs: true}).then(async function(result) {
                    for(let idx = 0; idx < result.rows.length; idx++) {
                        let doc = result.rows[idx].doc;
                        let shouldUpdate = false;
                        if(Array.isArray(doc[fieldName])) {
                            let arr = doc[fieldName];
                            for(let i = 0; i < arr.length; i++) {
                                let elt = arr[i];
                                // Assuming id is stored in object with id field in array
                                if(elt.id === req.params.identifier) {
                                    if(defaultReplaceValue !== undefined) {
                                        doc[fieldName][i] = defaultReplaceValue;
                                    } else {
                                        // Remove from array
                                        doc[fieldName].splice(i, 1);
                                    }
                                    shouldUpdate = true;
                                }
                            }
                        } else if(doc[fieldName] === req.params.identifier){
                            doc[fieldName] = defaultReplaceValue;
                            shouldUpdate = true;
                        }

                        if(shouldUpdate) {
                            console.log("Replacing (" + doc._id + ")'s " + fieldName + " with default value " + defaultReplaceValue);
                            console.log(doc);
                            let putResponse = await otherDB.put(doc);
                            console.log(putResponse);
                        }
                    }
                    res.send(deleteResponse)
                }).catch(function (findError) {
                    console.log("The " + endpointName + " delete endpoint encountered a find error: " + JSON.stringify(findError))
                    res.statusCode = 500
                    res.send(findError)
                })
            }
        })
        .catch(function (deleteError) {
            console.log("The " + endpointName + " delete endpoint encountered a delete error: " + JSON.stringify(deleteError))
            res.statusCode = 500
            res.send(deleteError)
        })
    }).catch(function (getError) {
        console.log("The " + endpointName + " delete endpoint encountered a get error: " + JSON.stringify(getError))
        res.statusCode = 500
        res.send(getError)
    })
}

function buildSelectorFromConstraints(selector, constraints) {
    if (constraints !== undefined && Array.isArray(constraints) && constraints.length > 0) {
        // Constraints come in with a field, an operator, and a value. 
        for (let i = 0; i < constraints.length; i++) {
            // Build the operator object
            let constraint = {}
            if (constraints[i].operator === "in") {
                constraint["$in"] = constraints[i].value
            } else if (constraints[i].operator === "equals") {
                constraint["$eq"] = constraints[i].value
            }
            // Assign the operator to the field
            selector[constraints[i].field] = constraint
        }
    }
    return selector
}

function buildConstraint(field, operator, value) {
    return {
        field: field,
        operator: operator,
        value: value
    }
}

async function checkUserPermission(req, res, permission, neededLevel) {
    try {
        let userResponse = await db.user.get(req.session.passport.user)
        try {
            let roleResponse = await db.role.get(userResponse.role)
            if (roleResponse[permission] !== undefined && roleResponse[permission] >= neededLevel) {
                return true
            } else {
                res.statusCode = 401
                res.send("You do not have permissions for this operation.")
                return false
            }
        } catch (roleError) {
            console.log("Error while checking permission", permission, "against level", neededLevel, "ERROR:", JSON.stringify(roleError))
            res.statusCode = 500
            res.send(roleError)
            return false
        }
    } catch (userError) {
        console.log("Error while getting currently logged in user record for permissions level check.", JSON.stringify(userError))
        res.statusCode = 500
        res.send(userError)
        return false
    }
}

async function getViewableAuthorizationGroups(req) {
    try {
        let userResponse = await db.user.get(req.session.passport.user)
        try {
            let roleResponse = await db.role.get(userResponse.role)
            try {
                // Call with empty selector to get all
                let authGroups = (await db.auth_group.find({ selector: {} })).docs
                const groupList = []

                if (roleResponse.devices == 0) {
                    for (let i = 0; i < roleResponse.authGroupsList.length; i++) {
                        if (roleResponse.authGroupsList[i].access > 0) {
                            groupList.push(roleResponse.authGroupsList[i].id)
                        }
                    }
                } else {
                    let lockedOutGroups = []
                    // Build the list of honeypots that are not visible via exceptions to baseline
                    for (let i = 0; i < roleResponse.authGroupsList.length; i++) {
                        if (roleResponse.authGroupsList[i].access === 0) {
                            lockedOutGroups.push(roleResponse.authGroupsList[i].id)
                        }
                    }
                    // Add everything not excepted
                    for (let i = 0; i < authGroups.length; i++) {
                        if (lockedOutGroups.includes(authGroups[i]._id) === false) {
                            groupList.push(authGroups[i]._id)
                        }
                    }
                }
                return groupList
            } catch (authGroupError) {
                console.log("Error while getting all auth groups. ERROR:", JSON.stringify(authGroupError))
                return []
            }
        } catch (roleError) {
            console.log("Error while checking viewable auth groups. ERROR:", JSON.stringify(roleError))
            return []
        }
    } catch (userError) {
        console.log("Error while getting currently logged in user record for authorization groups check.", JSON.stringify(userError))
        return []
    }
}