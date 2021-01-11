const PouchDB = require('pouchdb')
PouchDB.plugin(require('pouchdb-find'))

const alert = new PouchDB(process.env.DB_URL + '/alerts')
const log = new PouchDB(process.env.DB_URL + '/aggregate_logs')
const config = new PouchDB(process.env.DB_URL + '/configs')
const honeypot = new PouchDB(process.env.DB_URL + '/honeypots')
const role = new PouchDB(process.env.DB_URL + '/roles')
const user = new PouchDB(process.env.DB_URL + '/users')
const tag = new PouchDB(process.env.DB_URL + '/tags')
const auth_group = new PouchDB(process.env.DB_URL + '/auth_groups')
const metric = new PouchDB(process.env.DB_URL + '/metrics')
const adminLog = new PouchDB(process.env.DB_URL + '/admin_logs')

const timeGroupingQueryDoc = {
    //  design doc for summary of hosts data, and a time grouping of logs
    _id: `_design/timespans`,
    views: {
        hosttime: {
            map: function (doc) {
                emit(
                    [
                        doc.uuid,
                        // This precision allows for different group by criteria on query
                        Math.floor(doc.timestamp / 1000),
                        Math.floor(doc.timestamp / 100),
                        Math.floor(doc.timestamp / 10),
                        Math.floor(doc.timestamp / 1),
                    ],
                    null
                )
            }.toString(),
            reduce: '_count',
        },
    },
}

const mostRecentMetricView = {
    _id: `_design/mostRecentMetrics`,
    views: {
        mostRecentMetrics: {
            map: function (doc) {
                emit(doc.uuid, doc);
            }.toString(),
            reduce: function(keys, values) {
                var top=0;
                var index=0;
                for (var i=0;i<values.length;i++) {
                    if (values[i].timestamp > top) {
                        top = values[i].timestamp;
                        index = i;
                    }
                }
                return values[index];
            }.toString(),
        }
    }
}

const uniqueTagsView = {
    _id: `_design/uniqueTags`,
    views: {
        uniqueTags: {
            map: function (doc) {
                for(var i = 0; i < doc.tags.length; i++) {
                    emit(doc.tags[i])
                }
            }.toString(),
            reduce: '_count',
        }
    }
}

const configValidateDoc = {
    _id: '_design/validate',
    language: 'javascript',
    validate_doc_update: `
        function(newDoc, oldDoc, userCtx, secObj) {
            if(newDoc._deleted == undefined || newDoc._deleted === false) {

                // Ensure object has all of and only the required fields
                var shouldHave = ["filtered_ports","fingerprint","metrics_interval", "os", "portscan_threshold", "portscan_window", "response_delay", "services",
                                  "update_interval", "whitelist_addrs", "whitelist_ports"];

                // Don't get keys of special DB fields, they can be different depending on the operation
                var objWithRemovedDBFields = JSON.parse(JSON.stringify(newDoc));
                delete objWithRemovedDBFields._id;
                delete objWithRemovedDBFields._rev;
                delete objWithRemovedDBFields._revisions;
                delete objWithRemovedDBFields._deleted;
                
                var keys = Object.keys(objWithRemovedDBFields);
            
                if(shouldHave.length != keys.length) {
                    throw({ forbidden: 'Object must have these keys: ' + shouldHave + ". Your object has keys: " + keys});
                }
            
                for(var i = 0; i < keys.length; i++) {
                    var key = keys[i];
                    if(shouldHave.indexOf(key) == -1) {
                        throw({ forbidden: "Object can't have field: " + key});
                    }
                }
            
                // Validate response delay
                if (newDoc.response_delay == undefined) {
                    throw({ forbidden: 'Response delay is undefined' });
                }

                if ((newDoc.response_delay^0) !== newDoc.response_delay) {
                    throw({ forbidden: 'Response delay must be an integer' });
                }

                if (newDoc.response_delay < 0 || newDoc.response_delay > 60) {
                    throw({ forbidden: 'Response delay must be in the range [0,60]' });
                }

                // Validate portscan window
                if (newDoc.portscan_window == undefined) {
                    throw({ forbidden: 'Portscan window is undefined' });
                }

                if ((newDoc.portscan_window^0) !== newDoc.portscan_window) {
                    throw({ forbidden: 'Portscan window must be an integer' });
                }

                if (newDoc.portscan_window < 0 || newDoc.portscan_window > 300) {
                    throw({ forbidden: 'Portscan window must be in the range [0,300]' });
                }

                // Validate portscan threshold
                if (newDoc.portscan_threshold == undefined) {
                    throw({ forbidden: 'Portscan threshold is undefined' });
                }

                if ((newDoc.portscan_threshold^0) !== newDoc.portscan_threshold) {
                    throw({ forbidden: 'Portscan threshold must be an integer' });
                }

                if (newDoc.portscan_threshold < 0 || newDoc.portscan_threshold > 10000) {
                    throw({ forbidden: 'Portscan threshold must be in the range [0,10000]' });
                }

                // Validate metrics interval
                if (newDoc.metrics_interval == undefined) {
                    throw({ forbidden: 'Metrics interval is undefined' });
                }

                if ((newDoc.metrics_interval^0) !== newDoc.metrics_interval) {
                    throw({ forbidden: 'Metrics interval must be an integer' });
                }

                if (newDoc.metrics_interval < 0 || newDoc.metrics_interval > 120) {
                    throw({ forbidden: 'Metrics Interval must be in the range [0,120]' });
                }

                // Validate update interval
                if (newDoc.update_interval == undefined) {
                    throw({ forbidden: 'Update interval is undefined' });
                }

                if ((newDoc.update_interval^0) !== newDoc.update_interval) {
                    throw({ forbidden: 'Update interval must be an integer' });
                }

                if (newDoc.update_interval < 0 || newDoc.update_interval > 120) {
                    throw({ forbidden: 'Update Interval must be in the range [0,120]' });
                }

                // Check rest of fields - TODO

                if(newDoc.whitelist_addrs == undefined || newDoc.whitelist_ports == undefined || newDoc.os == undefined || newDoc.fingerprint == undefined || newDoc.filtered_ports == undefined || newDoc.services == undefined) {
                    throw({ forbidden: 'Missing required field' });
                }
                for(var i = 0; i < newDoc.services.length; i++) {
                    var service = newDoc.services[i];
                    if(service.name == undefined || service.port == undefined || service.protocol == undefined || service.response_model == undefined) {
                        throw({ forbidden: 'Missing required service fields for service #' + i });
                    }
                }
            }
        }
    `,
}
const adminLogValidateDoc = {
    _id: '_design/validate',
    language: 'javascript',
    validate_doc_update: `
        function(newDoc, oldDoc, userCtx, secObj) {
            if(newDoc._deleted == undefined || newDoc._deleted === false) {
                if(newDoc.changedBy == undefined || newDoc.message == undefined) {
                    throw({ forbidden: 'Missing required field' });
                }
            }
        }
    `,
}
const honeypotValidateDoc = {
    _id: '_design/validate',
    language: 'javascript',
    validate_doc_update: `
        function(newDoc, oldDoc, userCtx, secObj) {
            if(newDoc._deleted == undefined || newDoc._deleted === false) {

                // Ensure object has all of and only the required fields
                var shouldHave = ["ip_addr","auth_group_id","config_id", "tags", "deleted", "hostname"];
                // Don't get keys of special DB fields, they can be different depending on the operation
                var objWithRemovedDBFields = JSON.parse(JSON.stringify(newDoc));
                delete objWithRemovedDBFields._id;
                delete objWithRemovedDBFields._rev;
                delete objWithRemovedDBFields._revisions;
                delete objWithRemovedDBFields._deleted;
                
                var keys = Object.keys(objWithRemovedDBFields);
            
                if(shouldHave.length != keys.length) {
                    throw({ forbidden: 'Object must have these keys: ' + shouldHave + ". Your object has keys: " + keys});
                }
            
                for(var i = 0; i < keys.length; i++) {
                    var key = keys[i];
                    if(shouldHave.indexOf(key) == -1) {
                        throw({ forbidden: "Object can't have field: " + key});
                    }
                }

                if(Array.isArray(newDoc.tags) === false) {
                    throw({ forbidden: 'Tags is not an array' });
                }
                if(newDoc.hostname == undefined || newDoc.ip_addr == undefined || newDoc.auth_group_id == undefined || newDoc.config_id == undefined ) {
                    throw({ forbidden: 'Missing required field' });
                }
            }
        }
    `,
}

const roleValidateDoc = {
    _id: '_design/validate',
    language: 'javascript',
    validate_doc_update: `
        function(newDoc, oldDoc, userCtx, secObj) {
            if(newDoc._deleted == undefined || newDoc._deleted === false) {
                const minPermLevel = 0;
                const maxPermLevel = 2;

                // Ensure object has all of and only the required fields
                var shouldHave = ["users", "alerts", "metrics", "roles", "adminLogs", "traffLogs", "devices", "authGroupsMgmt", "configs", "authGroupsList"];

                // Don't get keys of special DB fields, they can be different depending on the operation
                var objWithRemovedDBFields = JSON.parse(JSON.stringify(newDoc));
                delete objWithRemovedDBFields._id;
                delete objWithRemovedDBFields._rev;
                delete objWithRemovedDBFields._revisions;
                delete objWithRemovedDBFields._deleted;
                
                var keys = Object.keys(objWithRemovedDBFields);
            
                if(shouldHave.length != keys.length) {
                    throw({ forbidden: 'Object must have these keys: ' + shouldHave + ". Your object has keys: " + keys});
                }
            
                for(var i = 0; i < keys.length; i++) {
                    var key = keys[i];
                    if(shouldHave.indexOf(key) == -1) {
                        throw({ forbidden: "Object can't have field: " + key});
                    }
                }

                if (newDoc._id == undefined || newDoc._id === "") {
                    throw({ forbidden: 'Missing id data' });
                }

                if (newDoc.users == undefined || newDoc.roles == undefined || newDoc.adminLogs == undefined || newDoc.traffLogs == undefined || newDoc.devices == undefined || newDoc.metrics == undefined || newDoc.authGroupsMgmt == undefined || newDoc.configs == undefined || newDoc.alerts == undefined) {
                    throw({ forbidden: 'Missing permissions level data' });
                }

                if (newDoc.authGroupsList == undefined) {
                    throw({ forbidden: 'Missing auth groups list' });
                }

                if (newDoc.users < minPermLevel || newDoc.users > maxPermLevel) {
                    throw({ forbidden: 'Users permission level is not in valid range [0,2]' });
                }

                if (newDoc.roles < minPermLevel || newDoc.roles > maxPermLevel) {
                    throw({ forbidden: 'Roles permission level is not in valid range [0,2]' });
                }

                if (newDoc.adminLogs < minPermLevel || newDoc.adminLogs > maxPermLevel) {
                    throw({ forbidden: 'AdminLogs permission level is not in valid range [0,2]' });
                }

                if (newDoc.traffLogs < minPermLevel || newDoc.traffLogs > maxPermLevel) {
                    throw({ forbidden: 'Traffic Logs permission level is not in valid range [0,2]' });
                }

                if (newDoc.devices < minPermLevel || newDoc.devices > maxPermLevel) {
                    throw({ forbidden: 'Devices permission level is not in valid range [0,2]' });
                }

                if (newDoc.metrics < minPermLevel || newDoc.metrics > maxPermLevel) {
                    throw({ forbidden: 'Metrics permission level is not in valid range [0,2]' });
                }

                if (newDoc.authGroupsMgmt < minPermLevel || newDoc.authGroupsMgmt > maxPermLevel) {
                    throw({ forbidden: 'Auth Groups permission level is not in valid range [0,2]' });
                }

                if (newDoc.alerts < minPermLevel || newDoc.alerts > maxPermLevel) {
                    throw({ forbidden: 'Alerts permission level is not in valid range [0,2]' });
                }

                if (Array.isArray(newDoc.authGroupsList) === false) {
                    throw({ forbidden: 'Auth groups list is not an array' });
                }

                for (var i = 0; i < newDoc.authGroupsList.length; i++) {
                    var authGroupObject = newDoc.authGroupsList[i];
                    if (authGroupObject.id == undefined || authGroupObject.access == undefined) {
                        throw({ forbidden: 'An element of the auth groups list does not include name and access' });
                    }
                    if (authGroupObject.access < minPermLevel || authGroupObject.access > maxPermLevel) {
                        throw({ forbidden: 'An element of the auth groups list contains an access level outside the range [0,2]' });
                    }
                }
            }
        }
        `,
}

const authGroupValidateDoc = {
    _id: '_design/validate',
    language: 'javascript',
    validate_doc_update: `
        function(newDoc, oldDoc, userCtx, secObj) {
            if(newDoc._deleted == undefined || newDoc._deleted === false) {
                // Ensure object has all of and only the required fields
                var shouldHave = [];

                // Don't get keys of special DB fields, they can be different depending on the operation
                var objWithRemovedDBFields = JSON.parse(JSON.stringify(newDoc));
                delete objWithRemovedDBFields._id;
                delete objWithRemovedDBFields._rev;
                delete objWithRemovedDBFields._revisions;
                delete objWithRemovedDBFields._deleted;
                
                var keys = Object.keys(objWithRemovedDBFields);
            
                if(shouldHave.length != keys.length) {
                    throw({ forbidden: 'Object must have these keys: ' + shouldHave + ". Your object has keys: " + keys});
                }
            
                for(var i = 0; i < keys.length; i++) {
                    var key = keys[i];
                    if(shouldHave.indexOf(key) == -1) {
                        throw({ forbidden: "Object can't have field: " + key});
                    }
                }

                if (newDoc._id == undefined || newDoc._id === "") {
                    throw({ forbidden: 'Missing id data' });
                }
            }
        }
        `,
}

const userValidateDoc = {
    _id: '_design/validate',
    language: 'javascript',
    validate_doc_update: `
        function(newDoc, oldDoc, userCtx, secObj) {
            if(newDoc._deleted == undefined || newDoc._deleted === false) {

                // Ensure object has all of and only the required fields
                var shouldHave = ["firstname","lastname","username", "password", "salt", "role", "local", "enabled", "otp"];
                
                // Don't get keys of special DB fields, they can be different depending on the operation
                var objWithRemovedDBFields = JSON.parse(JSON.stringify(newDoc));
                delete objWithRemovedDBFields._id;
                delete objWithRemovedDBFields._rev;
                delete objWithRemovedDBFields._revisions;
                delete objWithRemovedDBFields._deleted;
                
                var keys = Object.keys(objWithRemovedDBFields);
            
                if(shouldHave.length != keys.length) {
                    throw({ forbidden: 'Object must have these keys: ' + shouldHave + ". Your object has keys: " + keys});
                }
            
                for(var i = 0; i < keys.length; i++) {
                    var key = keys[i];
                    if(shouldHave.indexOf(key) == -1) {
                        throw({ forbidden: "Object can't have field: " + key});
                    }
                }

                if (newDoc.username == undefined || newDoc.password == undefined || newDoc.salt == undefined || newDoc.otp == undefined) {
                    throw({ forbidden: 'Missing login data' });
                }

                if (newDoc.firstname == undefined || newDoc.lastname == undefined) {
                    throw({ forbidden: 'Missing name data' });
                }

                if (newDoc.role === undefined || newDoc.local === undefined || newDoc.enabled === undefined) {
                    throw({ forbidden: 'Missing meta data' });
                }
            }
        }
        `,
}

const metricValidateDoc = {
    _id: '_design/validate',
    language: 'javascript',
    validate_doc_update: `
    function(newDoc, oldDoc, userCtx, secObj) {
        if(newDoc._deleted == undefined || newDoc._deleted === false) {

            // Ensure object has all of and only the required fields
            var shouldHave = ["uuid","hostname","timestamp", "cpu", "ram", "storage"];

            // Don't get keys of special DB fields, they can be different depending on the operation
            var objWithRemovedDBFields = JSON.parse(JSON.stringify(newDoc));
            delete objWithRemovedDBFields._id;
            delete objWithRemovedDBFields._rev;
            delete objWithRemovedDBFields._revisions;
            delete objWithRemovedDBFields._deleted;
            
            var keys = Object.keys(objWithRemovedDBFields);
        
            if(shouldHave.length != keys.length) {
                throw({ forbidden: 'Object must have these keys: ' + shouldHave + ". Your object has keys: " + keys});
            }
        
            for(var i = 0; i < keys.length; i++) {
                var key = keys[i];
                if(shouldHave.indexOf(key) == -1) {
                    throw({ forbidden: "Object can't have field: " + key});
                }
            }

            if(newDoc.uuid == undefined || newDoc.hostname == undefined || newDoc.cpu == undefined || newDoc.ram == undefined || newDoc.storage == undefined) {
                throw({ forbidden: 'Missing required field' });
            }
        }
    }
    `,
}



// CONFIG

const defaultConfigs = [
    {
        _id: 'configNoServices',
        response_delay: 10,
        metrics_interval: 15,
        update_interval: 1,
        portscan_window: 60,
        portscan_threshold: 500,
        whitelist_addrs: [],
        whitelist_ports: [],
        os: 'undetermined',
        fingerprint: 'undetermined',
        filtered_ports: [],
        services: [],
    },
    {
        _id: "configDefault",
        filtered_ports: [],
        fingerprint: "SCAN(V=7.80%E=4%D=11/11%OT=22%CT=%CU=38424%PV=N%DS=12%DC=T%G=N%TM=5FAC2F08%P=i686-pc-windows-windows)SEQ(SP=107%GCD=2%ISR=10A%TI=Z%II=I%TS=A)OPS(O1=M5B4ST11NW7%O2=M5B4ST11NW7%O3=M5B4NNT11NW7%O4=M5B4ST11NW7%O5=M5B4ST11NW7%O6=M5B4ST11)WIN(W1=FE88%W2=FE88%W3=FE88%W4=FE88%W5=FE88%W6=FE88)ECN(R=Y%DF=Y%T=3F%W=FAF0%O=M5B4NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS%RD=0%Q=)T2(R=N)T3(R=N)T4(R=N)T5(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T=3F%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=F6E4%RUD=G)IE(R=Y%DFI=N%T=3F%CD=S)",
        metrics_interval: 15,
        os: "Linux 2.6.32",
        portscan_threshold: 50,
        portscan_window: 60,
        response_delay: 0,
        services: [
            {
                name: "ssh",
                port: 2201,
                protocol: "tcp",
                response_model: [
                    {
                        request: null,
                        responses: [
                            {
                                payload: "5353482d322e302d4f70656e5353485f362e362e317031205562756e74752d327562756e7475322e31330d0a",
                                protocol: 6
                            },
                            {
                                payload: "5353482d322e302d4f70656e5353485f362e362e317031205562756e74752d327562756e7475322e31330d0a",
                                protocol: 6
                            },
                            {
                                payload: "5353482d322e302d4f70656e5353485f362e362e317031205562756e74752d327562756e7475322e31330d0a",
                                protocol: 6
                            }
                        ]
                    },
                    {
                        request: {
                            payload: "5353482d312e352d4e6d61704e53455f312e300a",
                            protocol: 6
                        },
                        responses: [
                            {
                                payload: "50726f746f636f6c206d616a6f722076657273696f6e73206469666665722e0a",
                                protocol: 6
                            },
                            {
                                payload: "50726f746f636f6c206d616a6f722076657273696f6e73206469666665722e0a",
                                protocol: 6
                            },
                            {
                                payload: "5353482d322e302d4f70656e5353485f362e362e317031205562756e74752d327562756e7475322e31330d0a",
                                protocol: 6
                            }
                        ]
                    },
                    {
                        request: {
                            payload: "000001c40814f85ca66a8c5d7de420904f93e25eafb30000007e6469666669652d68656c6c6d616e2d67726f7570312d736861312c6469666669652d68656c6c6d616e2d67726f757031342d736861312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861323536000000077373682d647373000000576165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c6165733139322d6362632c6165733235362d6362632c6165733132382d6374722c6165733139322d6374722c6165733235362d637472000000576165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c6165733139322d6362632c6165733235362d6362632c6165733132382d6374722c6165733139322d6374722c6165733235362d63747200000021686d61632d6d64352c686d61632d736861312c686d61632d726970656d6431363000000021686d61632d6d64352c686d61632d736861312c686d61632d726970656d64313630000000046e6f6e65000000046e6f6e6500000000000000000000000000cfc1dc1176aac4b9",
                            protocol: 6
                        },
                        responses: [
                            {
                                payload: "0000066c0a14f1a3da169551ec04b160749b924f25ee000000d4637572766532353531392d736861323536406c69627373682e6f72672c656364682d736861322d6e697374703235362c656364682d736861322d6e697374703338342c656364682d736861322d6e697374703532312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d7368613235362c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861312c6469666669652d68656c6c6d616e2d67726f757031342d736861312c6469666669652d68656c6c6d616e2d67726f7570312d736861310000002f7373682d7273612c7373682d6473732c65636473612d736861322d6e697374703235362c7373682d65643235353139000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e7365000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e736500000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d393600000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c",
                                protocol: 6
                            },
                            {
                                payload: "756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d3936000000156e6f6e652c7a6c6962406f70656e7373682e636f6d000000156e6f6e652c7a6c6962406f70656e7373682e636f6d0000000000000000000000000000000000000000000000",
                                protocol: 6
                            }
                        ]
                    },
                    {
                        request: {
                            payload: "0000008c051e000000810053c68c0853154fb3789f9fd78ee36da2f16b6d2dfde89e0b7ce6ca2555408ebbabda9bc1c39393e3ba8f1590674361662d7ecf86412ccb45dcd12d4b90e7109221ec68fe5b4e1397b7682db2165ea68446cf3eff8e9b74165438a6089adda77bf3bd5204360f3e8945fdc4023f84082889eed18c2fbaded86a0e11216eaf26a22e5039817e",
                            protocol: 6
                        },
                        responses: [
                            {
                                payload: "0000027c041f000001b3000000077373682d6473730000008100e7bca39f6f1566466819863d578904e6c47e2d4047cc845180bf51f924bb7b0a84617bc0cda6dae8c87990cae6fa9e0b44b910ddb1628e85b2108fe0541161e4f10f5ee734ee0f8705bae6a0230d1454d2e1c57d2021e7093ebede32433b4e13efac4ddd46f4e04bcc0f073bdf6a0e6080c5bdf3c3e1900c480f8f3832cc6677000000150081984d6f44e3fc21a3e452684ce712c5b5aff11f0000008100dc4c117da78e3cb2fb4ca0e0197ebb2db91ff54b5d96909d0b87683231a0b339d8330587e9aecb8f7be2e3f2a679965d8b1e8531d16aabedafadf4f50d1ab1d114b45d8746c679204beda0df7dd6602ad49030a7e913d4591ff54e018c3c70a3ecb5826b56702702d64b6297dbcf0f6b680b396ba1666d9560a490c7a3440ce20000008100dc487e9ad274175ba38133ae1ebf5fa1d2beb863b59ecca2e4ad59a13bd780723b96d2d9ca0cf42c9a0b0632ac4e6acd88b221f6fed411b73b99d5743b8df79b10ff46c07412a592a2c5bc5a858d56c44c5d2b8b7bfdef0e8ca546b07c5ef9a2e0eb438c5d69438b2c4593b28e9514970ce8983d6c3974140d2e2d95120c41cb0000008047377013de19523296e4cd969fc411f45e18c1aff538348ba876a1e2572089de43530a2f1941b4d2385b1fcac62c72df562930aee5d955f5ca0b62785c62de28bad24bdc69c0f87d6cbbd61afc92000a36062b3b579a69bbe5bf1f69d66923d63a90ecaedb5e6e30517ec8be04647bea1578c14edcf6f52488fbc092bf0e796800000037000000077373682d647373000000285e6eebb741db6f76774a8448ad74b05a76aadaa43ea75181b1f99a73e003b5b26c923dfa63bdc4c7000000000000000c0a1500000000000000000000",
                                protocol: 6
                            },
                            {
                                payload: "5353482d322e302d4f70656e5353485f362e362e317031205562756e74752d327562756e7475322e31330d0a",
                                protocol: 6
                            }
                        ]
                    },
                    {
                        request: {
                            payload: "5353482d322e302d4e6d61702d535348322d486f73746b65790d0a",
                            protocol: 6
                        },
                        responses: [
                            {
                                payload: "0000066c0a14d8c5da2cfbc697ef53b9a09634047d03000000d4637572766532353531392d736861323536406c69627373682e6f72672c656364682d736861322d6e697374703235362c656364682d736861322d6e697374703338342c656364682d736861322d6e697374703532312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d7368613235362c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861312c6469666669652d68656c6c6d616e2d67726f757031342d736861312c6469666669652d68656c6c6d616e2d67726f7570312d736861310000002f7373682d7273612c7373682d6473732c65636473612d736861322d6e697374703235362c7373682d65643235353139000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e7365000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e736500000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d393600000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c",
                                protocol: 6
                            },
                            {
                                payload: "756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d3936000000156e6f6e652c7a6c6962406f70656e7373682e636f6d000000156e6f6e652c7a6c6962406f70656e7373682e636f6d0000000000000000000000000000000000000000000000",
                                protocol: 6
                            }
                        ]
                    },
                    {
                        request: {
                            payload: "0000008c051e00000081009b43b61893de0e63eeef08710e91987f13657950e6d34a7bf1f86c178d3ebc8d353159519e8090f7fa7653ba43404135cfc107d45e6d34bd5ba81b08d8aae6808224cbcbdf53f2ce315f640c929c1b4bcb5f6901becfb9344a888c44ad5d243cb94651ef636bfb7e6ea13dfe3973e0e1ae500e9136c92677d3cbb58aa5be2e2fd93fecf277",
                            protocol: 6
                        },
                        responses: [
                            {
                                payload: "000002bc071f00000117000000077373682d727361000000030100010000010100ba69fa284d9f66554185344864328451d41b73bbae175f0125842b07c3fcd5948c7f1d7ca535b6fdfb5d5d9b6560250db5a719160ecf8bebe11b6320e7bd15114eb3138072f4c6c781d0490da9ec6cf616194a2aad331e23b4636d1efb0cc599dbc6f55493675ab16bed0649fc27925a8126f3593428e218ca30e235494957b622b102cd85f308aad84752b8ac3f28d93c19f229d5303ef1c706780b67b15a6d4c9e03ffc321016b113a44333a8c10be7041cf6ffc79c12fa0c49c69ffa40df350a302b780436d4923aa630f492cecdae982413cbfda62e410d2727be11af9bcbe3868d225ac623d8c9736c746d5ec178d039915b97b268727d66db901f3219d0000008100ea4b7406fc6ee8b23ada1424b8393edcb630bd55ef39e1d1a13432f2e16c90e719ec833a085a1bd373666e1a240ecb6421d8ab576106a34b9fd949551750315b5c1a8aaebdce290cd2f71827317301f13fcd73544a811f7d2751a10b0065453cef09f36c8f32c608b861dcf89bef3aca028016a19bb1c5c6a44d41b23ae30f7c0000010f000000077373682d72736100000100ba037a471c8c33ff7d46bcd274dac733ae5dbe85fe9280459a10d08e8c51958784e3cac8ec332e3a8430a10eb70e4d652f3e9c7538cb04ac2671d87e2a386fbfd9215ee2123526382e27b295351f56a5aef8d3a6de2d7beb60646020a03c43b97b41e45ba53bd078ce4f63cc8e32d4cb5418e27af74fe649a8d7576f6df84853737585a07224bc65045dcf89a0053f890cc46e143adb6a24a63d9841648d25df7810502e0e13c9683773fff5efea44fbab1fe6fb3b179eaec0601d6099eba418dd561cce5ddb107f17a1a8e508985c535a5ed743448efa7f5cf562ea78a1761677c25998651808749929166eb754da2d48a0cc040f3ce347c6c06750a2b193e9000000000000000000000c0a1500000000000000000000",
                                protocol: 6
                            },
                            {
                                payload: "5353482d322e302d4f70656e5353485f362e362e317031205562756e74752d327562756e7475322e31330d0a",
                                protocol: 6
                            }
                        ]
                    },
                    {
                        request: {
                            payload: "000001cc0414e7aa8c150e08a93a69e36a2284b8a13a0000007e6469666669652d68656c6c6d616e2d67726f7570312d736861312c6469666669652d68656c6c6d616e2d67726f757031342d736861312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d7368613235360000001365636473612d736861322d6e69737470323536000000576165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c6165733139322d6362632c6165733235362d6362632c6165733132382d6374722c6165733139322d6374722c6165733235362d637472000000576165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c6165733139322d6362632c6165733235362d6362632c6165733132382d6374722c6165733139322d6374722c6165733235362d63747200000021686d61632d6d64352c686d61632d736861312c686d61632d726970656d6431363000000021686d61632d6d64352c686d61632d736861312c686d61632d726970656d64313630000000046e6f6e65000000046e6f6e6500000000000000000000000000de53f1de",
                            protocol: 6
                        },
                        responses: [
                            {
                                payload: "0000066c0a140bf339616fa0c02bdf943e3e346e1739000000d4637572766532353531392d736861323536406c69627373682e6f72672c656364682d736861322d6e697374703235362c656364682d736861322d6e697374703338342c656364682d736861322d6e697374703532312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d7368613235362c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861312c6469666669652d68656c6c6d616e2d67726f757031342d736861312c6469666669652d68656c6c6d616e2d67726f7570312d736861310000002f7373682d7273612c7373682d6473732c65636473612d736861322d6e697374703235362c7373682d65643235353139000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e7365000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e736500000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d393600000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c",
                                protocol: 6
                            },
                            {
                                payload: "756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d3936000000156e6f6e652c7a6c6962406f70656e7373682e636f6d000000156e6f6e652c7a6c6962406f70656e7373682e636f6d0000000000000000000000000000000000000000000000",
                                protocol: 6
                            }
                        ]
                    },
                    {
                        request: {
                            payload: "0000008c071e0000007fa941993786bf6cc6acacf0f21789e4b49b719991879504a6fb2820b8431a671889fa6a1c65b621b172e568d8e77ef1a02e7e6b624fd3df64233199bec46d2eeaf3b497089807b8126641c079bcd27c5848e4bc3fb5121dc51d1edd3c5cc77be635f7391ee07937cd983513449b4355add396f0d4e6c135b50285f1d084492d4d19b50fff3512",
                            protocol: 6
                        },
                        responses: [
                            {
                                payload: "5353482d322e302d4f70656e5353485f362e362e317031205562756e74752d327562756e7475322e31330d0a",
                                protocol: 6
                            }
                        ]
                    },
                    {
                        request: {
                            payload: "000001cc0414e7ac2118fce79b8d391a9f428b4e56760000007e6469666669652d68656c6c6d616e2d67726f7570312d736861312c6469666669652d68656c6c6d616e2d67726f757031342d736861312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d7368613235360000001365636473612d736861322d6e69737470333834000000576165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c6165733139322d6362632c6165733235362d6362632c6165733132382d6374722c6165733139322d6374722c6165733235362d637472000000576165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c6165733139322d6362632c6165733235362d6362632c6165733132382d6374722c6165733139322d6374722c6165733235362d63747200000021686d61632d6d64352c686d61632d736861312c686d61632d726970656d6431363000000021686d61632d6d64352c686d61632d736861312c686d61632d726970656d64313630000000046e6f6e65000000046e6f6e65000000000000000000000000001f249755",
                            protocol: 6
                        },
                        responses: [
                            {
                                payload: "0000066c0a145fb0b6b25a29d670bd9f66f412303960000000d4637572766532353531392d736861323536406c69627373682e6f72672c656364682d736861322d6e697374703235362c656364682d736861322d6e697374703338342c656364682d736861322d6e697374703532312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d7368613235362c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861312c6469666669652d68656c6c6d616e2d67726f757031342d736861312c6469666669652d68656c6c6d616e2d67726f7570312d736861310000002f7373682d7273612c7373682d6473732c65636473612d736861322d6e697374703235362c7373682d65643235353139000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e7365000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e736500000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d393600000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c",
                                protocol: 6
                            },
                            {
                                payload: "756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d3936000000156e6f6e652c7a6c6962406f70656e7373682e636f6d000000156e6f6e652c7a6c6962406f70656e7373682e636f6d0000000000000000000000000000000000000000000000",
                                protocol: 6
                            },
                            {
                                payload: "5353482d322e302d4f70656e5353485f362e362e317031205562756e74752d327562756e7475322e31330d0a",
                                protocol: 6
                            }
                        ]
                    },
                    {
                        request: {
                            payload: "000001cc0414248b31bfebae1cb2766f6e4f39d4e3ba0000007e6469666669652d68656c6c6d616e2d67726f7570312d736861312c6469666669652d68656c6c6d616e2d67726f757031342d736861312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d7368613235360000001365636473612d736861322d6e69737470353231000000576165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c6165733139322d6362632c6165733235362d6362632c6165733132382d6374722c6165733139322d6374722c6165733235362d637472000000576165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c6165733139322d6362632c6165733235362d6362632c6165733132382d6374722c6165733139322d6374722c6165733235362d63747200000021686d61632d6d64352c686d61632d736861312c686d61632d726970656d6431363000000021686d61632d6d64352c686d61632d736861312c686d61632d726970656d64313630000000046e6f6e65000000046e6f6e6500000000000000000000000000c587a326",
                            protocol: 6
                        },
                        responses: [
                            {
                                payload: "0000066c0a14ad8d4b6af40a07cad9609703889154dd000000d4637572766532353531392d736861323536406c69627373682e6f72672c656364682d736861322d6e697374703235362c656364682d736861322d6e697374703338342c656364682d736861322d6e697374703532312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d7368613235362c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861312c6469666669652d68656c6c6d616e2d67726f757031342d736861312c6469666669652d68656c6c6d616e2d67726f7570312d736861310000002f7373682d7273612c7373682d6473732c65636473612d736861322d6e697374703235362c7373682d65643235353139000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e7365000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e736500000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d393600000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c",
                                protocol: 6
                            },
                            {
                                payload: "756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d3936000000156e6f6e652c7a6c6962406f70656e7373682e636f6d000000156e6f6e652c7a6c6962406f70656e7373682e636f6d0000000000000000000000000000000000000000000000",
                                protocol: 6
                            },
                            {
                                payload: "5353482d322e302d4f70656e5353485f362e362e317031205562756e74752d327562756e7475322e31330d0a",
                                protocol: 6
                            }
                        ]
                    },
                    {
                        request: {
                            payload: "000001c404144b26497294cf79108307668b5ed93cb70000007e6469666669652d68656c6c6d616e2d67726f7570312d736861312c6469666669652d68656c6c6d616e2d67726f757031342d736861312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d7368613235360000000b7373682d65643235353139000000576165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c6165733139322d6362632c6165733235362d6362632c6165733132382d6374722c6165733139322d6374722c6165733235362d637472000000576165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c6165733139322d6362632c6165733235362d6362632c6165733132382d6374722c6165733139322d6374722c6165733235362d63747200000021686d61632d6d64352c686d61632d736861312c686d61632d726970656d6431363000000021686d61632d6d64352c686d61632d736861312c686d61632d726970656d64313630000000046e6f6e65000000046e6f6e650000000000000000000000000053f24a04",
                            protocol: 6
                        },
                        responses: [
                            {
                                payload: "0000066c0a143affc51a85c23b45a9b3799b1b2073fd000000d4637572766532353531392d736861323536406c69627373682e6f72672c656364682d736861322d6e697374703235362c656364682d736861322d6e697374703338342c656364682d736861322d6e697374703532312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d7368613235362c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d736861312c6469666669652d68656c6c6d616e2d67726f757031342d736861312c6469666669652d68656c6c6d616e2d67726f7570312d736861310000002f7373682d7273612c7373682d6473732c65636473612d736861322d6e697374703235362c7373682d65643235353139000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e7365000000e96165733132382d6374722c6165733139322d6374722c6165733235362d6374722c617263666f75723235362c617263666f75723132382c6165733132382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d2c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c6165733132382d6362632c336465732d6362632c626c6f77666973682d6362632c636173743132382d6362632c6165733139322d6362632c6165733235362d6362632c617263666f75722c72696a6e6461656c2d636263406c797361746f722e6c69752e736500000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d393600000192686d61632d6d64352d65746d406f70656e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d726970656d643136302d65746d406f70656e7373682e636f6d2c686d61632d736861312d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352d39362d65746d406f70656e7373682e636f6d2c686d61632d6d64352c686d61632d736861312c756d61632d3634406f70656e7373682e636f6d2c",
                                protocol: 6
                            },
                            {
                                payload: "756d61632d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d736861322d3531322c686d61632d726970656d643136302c686d61632d726970656d64313630406f70656e7373682e636f6d2c686d61632d736861312d39362c686d61632d6d64352d3936000000156e6f6e652c7a6c6962406f70656e7373682e636f6d000000156e6f6e652c7a6c6962406f70656e7373682e636f6d0000000000000000000000000000000000000000000000",
                                protocol: 6
                            }
                        ]
                    }
                ]
            }
        ],
        update_interval: 1,
        whitelist_addrs: [    
            "192.168.42.54",
            "192.168.42.51",
            "192.168.42.52"
        ],
        whitelist_ports: [    
            "8082",
            "5000",
            "8443"
        ]
    }
]

// USERS

const defaultUsers = [
    {
        _id: 'SystemSuperUser',
        firstname: 'Super',
        lastname: 'User',
        username: 'superuser',
        password: 'bb44544f15e1c6efa2e3c20dd16b8d26e23f3684ee3675c4e5bdd14e0956340c',
        salt: 'himalayan',
        role: 'superUser',
        local: true,
        enabled: true,
        otp: false
    },
    {
        _id: 'userAdminDefault',
        firstname: 'Phil',
        lastname: 'Lanthripist',
        username: 'admin',
        password: 'bb44544f15e1c6efa2e3c20dd16b8d26e23f3684ee3675c4e5bdd14e0956340c',
        salt: 'himalayan',
        role: 'adminDefault',
        local: true,
        enabled: true,
        otp: false
    },
    {
        _id: 'userPlebDefault',
        firstname: 'Plebian',
        lastname: 'Solaris',
        username: 'pleb',
        password: 'bb44544f15e1c6efa2e3c20dd16b8d26e23f3684ee3675c4e5bdd14e0956340c',
        salt: 'himalayan',
        role: 'auditorDefault',
        local: true,
        enabled: true,
        otp: false
    },
    {
        _id: 'samlTestUserDefault',
        firstname: 'Richard',
        lastname: 'Cypher',
        username: 'samltestuser',
        password: 'THISISNEVERCHECKEDORUSED',
        salt: 'THISISNEVERCHECKEDORUSED',
        role: 'auditorDefault',
        local: false,
        enabled: true,
        otp: false
    },
]

// ROLES

const defaultRoles = [
    {
        _id: 'superUser',
        users: 2,
        roles: 2,
        adminLogs: 2,
        traffLogs: 2,
        devices: 2,
        metrics: 2,
        authGroupsMgmt: 2,
        configs: 2,
        alerts: 2,
        authGroupsList: [],
    },
    {
        _id: 'adminDefault',
        users: 2,
        roles: 2,
        adminLogs: 2,
        traffLogs: 2,
        devices: 2,
        metrics: 2,
        authGroupsMgmt: 2,
        configs: 2,
        alerts: 2,
        authGroupsList: [
            {
                id: 'Default-Aydindril',
                access: 2,
            },
        ],
    },
    {
        _id: 'editorDefault',
        users: 1,
        roles: 2,
        adminLogs: 2,
        traffLogs: 2,
        devices: 2,
        metrics: 2,
        authGroupsMgmt: 2,
        configs: 2,
        alerts: 0,
        authGroupsList: [
            {
                id: 'Default-Aydindril',
                access: 2,
            },
            {
                id: 'Default-Hartland',
                access: 1,
            },
        ],
    },
    {
        _id: 'auditorDefault',
        users: 1,
        roles: 2,
        adminLogs: 1,
        traffLogs: 1,
        devices: 1,
        metrics: 2,
        authGroupsMgmt: 1,
        configs: 1,
        alerts: 0,
        authGroupsList: [
            {
                id: 'Default-Aydindril',
                access: 1,
            },
        ],
    },
]

// AUTH GROUPS

const defaultAuthGroups = [
    {
        _id: 'Default-Aydindril',
    },
    {
        _id: 'Default-Hartland',
    },
]

// ADMIN LOGS

const defaultAdminLogs = [
    {
        _id: 'Default-AdminLog',
        timestamp: 1600914028,
        changedBy: 'userAdminDefault',
        message: 'This is a default log',
    },
    {
        _id: 'Default-AdminLogSecondary',
        timestamp: 1600914018,
        changedBy: 'userAdminDefault',
        message: 'This is a default log',
    }
]

// METRICS

const defaultMetrics = [
    {
        _id: 'metricDefault',
        uuid: '27d0635bf7244bf6adb1c6015ffc62da',
        hostname: 'alpha',
        timestamp: 1600914018,
        cpu: 8.1,
        ram: 77.1,
        storage: 157.00,
    },
    {
        _id: 'metricDefaultSecondary',
        uuid: '623bd7ad0b8b47678b033180ab7fbc62',
        hostname: 'beta',
        timestamp: 1600914028,
        cpu: 5.6,
        ram: 76.9,
        storage: 169.00,
    },
]


// HELPER FUNCTIONS

async function importAllIndexes() {
    const indexCreates = [
        // User sort indexes
        makeIndex(user, ["username"]),
        makeIndex(user, ["firstname"]),
        makeIndex(user, ["lastname"]),
        makeIndex(user, ["role"]),
        makeIndex(user, ["local"]),
        makeIndex(user, ["enabled"]),
        // Roles
        makeIndex(role, ["admin"]),
        makeIndex(role, ["_id"]),
        makeIndex(role, ["users"]),
        makeIndex(role, ["roles"]),
        makeIndex(role, ["devices"]),
        makeIndex(role, ["configs"]),
        // Honeypots
        makeIndex(honeypot, ["hostname"]),
        makeIndex(honeypot, ["ip_addr"]),
        makeIndex(honeypot, ["config_id"]),
        makeIndex(honeypot, ["auth_group_id"]),
        // Metrics
        makeIndex(metric, ["hostname"]),
        makeIndex(metric, ["timestamp"]),
        makeIndex(metric, ["cpu"]),
        makeIndex(metric, ["ram"]),
        makeIndex(metric, ["storage"]),
        // Alerts
        makeIndex(alert, ["timestamp"]),
        // Configs
        makeIndex(config, ["_id"]),
        // Auth Groups
        makeIndex(auth_group, ["_id"]),
        // Logs
        makeIndex(log, ["hostname"]),
        makeIndex(log, ["sourcePortNumber"]),
        makeIndex(log, ["sourceIPAddress"]),
        makeIndex(log, ["trafficType"]),
        makeIndex(log, ["destPortNumber"]),
        makeIndex(log, ["destIPAddress"]),

        // Admin Logs
        makeIndex(adminLog, ["_id"]),
        makeIndex(adminLog, ["timestamp"]),
        makeIndex(adminLog, ["changedBy"]),
        makeIndex(adminLog, ["message"])
    ]

    await Promise.all(indexCreates)
}

async function makeIndex(database, fields) {
    await database.createIndex({
        index: {
            fields: fields,
        },
    })
    console.log("Index created")
}

async function importAllDefaults() {
    // Helper
    async function deleteAndThenAdd(database, document, databaseName) {
        try {
            await deleteDocumentIfItExists(database, document._id, databaseName)
            try {
                const response = await database.put(document)
                console.log(
                    'Default ' +
                        databaseName +
                        ' object insert response: ' +
                        JSON.stringify(response)
                )
            } catch (err) {
                console.log(
                    'Default ' +
                        databaseName +
                        ' object insert error: ' +
                        JSON.stringify(err)
                )
            }
        } catch (err) {
            console.log(
                'Error while deleting ' +
                    databaseName +
                    ' default object: ' +
                    JSON.stringify(err)
            )
        }
    }
    // Import Configs
    for (let i = 0; i < defaultConfigs.length; i++) {
        await deleteAndThenAdd(config, defaultConfigs[i], 'Config')
    }
    // Import users
    for (let i = 0; i < defaultUsers.length; i++) {
        await deleteAndThenAdd(user, defaultUsers[i], 'User')
    }
    // Import roles
    for (let i = 0; i < defaultRoles.length; i++) {
        await deleteAndThenAdd(role, defaultRoles[i], 'Role')
    }
    // Import auth groups
    for (let i = 0; i < defaultAuthGroups.length; i++) {
        await deleteAndThenAdd(auth_group, defaultAuthGroups[i], 'Auth Group')
    }
    // Import metrics
    for (let i = 0; i < defaultMetrics.length; i++) {
        await deleteAndThenAdd(metric, defaultMetrics[i], 'Metric')
    }
    // Import Admin Logs
    for (let i = 0; i < defaultAdminLogs.length; i++) {
        await deleteAndThenAdd(adminLog, defaultAdminLogs[i], 'Admin Log')
    }
}

async function deleteDocumentIfItExists(database, docID) {
    try {
        const doc = await database.get(docID)
        await database.remove(doc)
    } catch (err) {
        if (err.error !== 'not_found') {
            throw err
        }
    }
}

async function runDesignDocumentSync(database, designDoc, databaseName) {
    // Helper
    async function deleteAndThenAdd(database, document, databaseName) {
        try {
            await deleteDocumentIfItExists(database, document._id)
            try {
                const response = await database.put(document)
                console.log(
                    databaseName + ' design doc response: ' + JSON.stringify(response)
                )
            } catch (err) {
                console.log(err)
                console.log(databaseName + ' design doc error: ' + JSON.stringify(err))
            }
        } catch (err) {
            console.log(
                'Error while deleting ' +
                    databaseName +
                    ' design doc: ' +
                    JSON.stringify(err)
            )
        }
    }
    await database.createIndex({
        index: {
            fields: ['timestamp'],
        },
    })
    // Sync all different docs
    await deleteAndThenAdd(database, designDoc, databaseName)
}

function setupDesignDocuments() {
    var promises = [
        runDesignDocumentSync(log, timeGroupingQueryDoc, 'Log'),
        runDesignDocumentSync(config, configValidateDoc, 'Config'),
        runDesignDocumentSync(honeypot, honeypotValidateDoc, 'Honeypot'),
        runDesignDocumentSync(honeypot, uniqueTagsView, 'Honeypot'),
        runDesignDocumentSync(role, roleValidateDoc, 'Role'),
        runDesignDocumentSync(auth_group, authGroupValidateDoc, 'Auth Group'),
        runDesignDocumentSync(user, userValidateDoc, 'User'),
        runDesignDocumentSync(metric, metricValidateDoc, 'Metric'),
        runDesignDocumentSync(metric, mostRecentMetricView, 'Metric'),
        runDesignDocumentSync(adminLog, adminLogValidateDoc, 'Admin Log')
    ]
    return Promise.all(promises)
}

module.exports = {
    alert,
    log,
    config,
    honeypot,
    role,
    user,
    tag,
    auth_group,
    metric,
    adminLog,
    setupDesignDocuments,
    importAllIndexes,
    importAllDefaults,
}
