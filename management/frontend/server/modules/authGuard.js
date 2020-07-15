/**
 * Middleware to check if the request is authenticated and possibly do some fancy redirection
 */
module.exports = options => {
    if (typeof options == 'string') {
        options = { redirectTo: options }
    }
    options = options || {}

    var url = options.redirectTo || '/login'
    var setReturnTo = options.setReturnTo === undefined ? true : options.setReturnTo

    return function (req, res, next) {
        if (!req.isAuthenticated || !req.isAuthenticated()) {
            if (setReturnTo && req.session) {
                req.session.returnTo = req.originalUrl || req.url
            }
            // TODO: decide if we want status codes or redirects
            return res.status(401).send('You are not authenticated')
            // return res.redirect(url);
        }
        next()
    }
}
