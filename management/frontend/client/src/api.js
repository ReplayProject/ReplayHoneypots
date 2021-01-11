/**
 * API implementation so we don't directly talk to the database
 */

import axios from 'axios'

const API_BASE = '/api/v1/'

function getAdminLogs(id, sort, skip, fields, limit) {
    return genericGetter('admin_logs', id, sort, skip, fields, limit)
}

function addAdminLog(adminLogData) {
    return genericPost('admin_logs', adminLogData)
}

function getLogs(id, sort, skip, fields, limit) {
    return genericGetter('logs', id, sort, skip, fields, limit)
}

function getLogDBInfo() {
    return axios.get(API_BASE + 'logDBInfo')
}

function fetchAlerts(hostname, limit, skip) {
    const paramBuild = {}

    if (hostname) {
        paramBuild.hostname = hostname
    }

    if (limit) {
        paramBuild.limit = limit
    }

    if (skip) {
        paramBuild.skip = skip
    } else {
        paramBuild.skip = 0
    }

    if (hostname || limit || skip) {
        return axios.get(API_BASE + 'alerts', {
            params: paramBuild,
        })
    } else {
        return axios.get(API_BASE + 'alerts')
    }
}

function alertsFeed(component) {
    fetch(API_BASE + 'alertsFeed').then(response => {
        const reader = response.body.getReader()
        const stream = new ReadableStream({
            start(controller) {
                // The following function handles each data chunk
                function push() {
                    // "done" is a Boolean and value a "Uint8Array"
                    reader.read().then(({ done, value }) => {
                        // Is there no more data to read?
                        if (done) {
                            // Tell the browser that we have finished sending data
                            controller.close()
                            return
                        }

                        var str = ''
                        for (var i = 0; i < value.length; i++) {
                            str += String.fromCharCode(parseInt(value[i]))
                        }
                        console.log('Received', str)

                        var obj = JSON.parse(str)
                        if (obj.type === 'change') {
                            var change = obj.data
                            if (!change.deleted) {
                                console.log('New alert')
                                component.$store.commit('unshiftAlerts', change.doc)
                                component.$store.commit('popAlerts') // remove element to keep number the same
                                component.$store.commit('sortAlertsDesc')
                                component.$toasted.show(
                                    'New alert from ' + change.doc.hostname
                                )
                            }
                        }

                        // Get the data and send it to the browser via the controller
                        controller.enqueue(value)
                        push()
                    })
                }

                push()
            },
        })

        return new Response(stream, { headers: { 'Content-Type': 'text/html' } })
    })
}

function getHostsInfo() {
    return axios.get(API_BASE + 'hostInfo')
}

function getHoneyPotByTag(tag) {
    return genericGetter('honeypotByTag', JSON.stringify(tag), undefined, 0, undefined, undefined)
}

function getMetricByHost(uuid) {
    return genericGetter('metricsByUUID', JSON.stringify(uuid), undefined, 0, undefined, undefined)
}

function getHostsInfoBy(startkey, endkey, specificity) {
    return axios.get(API_BASE + 'hostInfo', {
        params: {
            startkey: JSON.stringify(startkey),
            endkey: JSON.stringify(endkey),
            specificity: specificity,
        },
    })
}

function getHoneypots(uuid, sort, skip, fields, limit) {
    return genericGetter('honeypot', uuid, sort, skip, fields, limit)
}

function updateHoneypot(identifier, honeypotData) {
    return genericPut('honeypot', identifier, honeypotData)
}

function updateRole(id, roleData) {
    return genericPut('role', id, roleData)
}

function getRoles(name, sort, skip, fields, limit) {
    return genericGetter('role', name, sort, skip, fields, limit)
}

function addRole(roleData) {
    return genericPost('role', roleData)
}

function getConfigs(id, sort, skip, fields, limit) {
    return genericGetter('config', id, sort, skip, fields, limit)
}

function getAuthGroups(id, sort, skip, fields, limit) {
    return genericGetter('auth_group', id, sort, skip, fields, limit)
}

function getUsers(id, sort, skip, fields, limit) {
    return genericGetter('user', id, sort, skip, fields, limit)
}

function getAuthGroups(name, sort, skip, fields, limit) {
    return genericGetter('auth_group', name, sort, skip, fields, limit)
}

function addAuthGroup(_id) {
    return genericPost('auth_group', _id)
}

function updateUser(identifier, userData) {
    return genericPut('user', identifier, userData)
}

function addUser(userData) {
    return genericPost('user', userData)
}

function deleteUser(id) {
    return genericDelete('user', id)
}

function getConfigs(id, sort, skip, fields, limit) {
    return genericGetter('config', id, sort, skip, fields, limit)
}

function updateConfig(identifier, configData) {
    return genericPut('config', identifier, configData)
}

function addConfig(configData) {
    return genericPost('config', configData)
}

function deleteConfig(id) {
    return genericDelete('config', id)
}

function deleteAuthGroup(id) {
    return genericDelete('auth_group', id)
}

function deleteRole(id) {
    return genericDelete('role', id)
}

function getSessionData() {
    return genericGetter('session')
}

function getAllTags() {
    return axios.get(API_BASE + 'tag')
}

function getAllMetrics(tag, auth, sort, skip, fields, limit) {
    // This function accepts multiple filter parameters, which is 
    // not supported by our generic getter, so we have to be verbose here
    if (!genericParameterChecker(undefined, sort, skip, fields, limit)) {
        return axios.get(API_BASE + 'metrics')
    }

    const paramBuild = {}

    if (tag) {
        paramBuild.tag = tag
    }

    if (auth) {
        paramBuild.auth = auth
    }

    if (sort) {
        paramBuild.sort = JSON.stringify(sort)
    }

    if (skip) {
        paramBuild.skip = skip
    } else {
        paramBuild.skip = 0
    }

    if (fields && fields.length !== 0) {
        paramBuild.fields = JSON.stringify(fields)
    }

    if (limit) {
        paramBuild.limit = limit
    }

    return axios.get(API_BASE + 'metrics', {
        params: paramBuild,
    })
}

function genericParameterChecker(identifier, sort, skip, fields, limit) {
    if (identifier === undefined && sort === undefined && skip === undefined && fields === undefined && limit === undefined) {
        return false
    } else if (fields !== undefined && !Array.isArray(fields)) {
        return false
    } else {
        return true
    }
}

function genericPut(endpoint, identifier, data) {
    return axios.put(API_BASE + endpoint + '/' + identifier, data)
}

function genericPost(endpoint, data) {
    return axios.post(API_BASE + endpoint, data)
}

function genericDelete(endpoint, identifier) {
    return axios.delete(API_BASE + endpoint + '/' + identifier)
}

function genericGetter(endpoint, identifier, sort, skip, fields, limit) {
    if (!genericParameterChecker(identifier, sort, skip, fields, limit)) {
        return axios.get(API_BASE + endpoint)
    }

    const paramBuild = {}

    if (identifier !== undefined) {
        paramBuild.identifier = identifier
    }

    if (sort !== undefined) {
        paramBuild.sort = JSON.stringify(sort)
    }

    if (skip !== undefined) {
        paramBuild.skip = skip
    } else {
        paramBuild.skip = 0
    }

    if (fields !== undefined && fields.length !== 0) {
        paramBuild.fields = JSON.stringify(fields)
    }

    if (limit !== undefined) {
        paramBuild.limit = limit
    }

    return axios.get(API_BASE + endpoint, {
        params: paramBuild,
    })
}

module.exports = {

    // Logs
    getLogs,
    getAdminLogs,
    addAdminLog,

    // Users
    getUsers,
    updateUser,
    addUser,
    deleteUser,


    // Configs
    getConfigs,
    updateConfig,
    addConfig,
    deleteConfig,

    // Roles
    deleteRole,
    getRoles,
    addRole,
    updateRole,

    // Auth Groups
    addAuthGroup,
    deleteAuthGroup,
    getAuthGroups,

    // Alerts
    fetchAlerts,
    alertsFeed,

    // Session
    getLogDBInfo,
    getSessionData,
    // Honeypot
    getHoneypots,
    updateHoneypot,
    getHoneyPotByTag,

    // Metrics
    getAllMetrics,
    getMetricByHost,

    // HostInfo
    getHostsInfo,
    getHostsInfoBy,
    
    // Tags
    getAllTags,
}
