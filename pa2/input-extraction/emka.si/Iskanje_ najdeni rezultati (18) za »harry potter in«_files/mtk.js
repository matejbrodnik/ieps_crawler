"use strict";

var mtkGetParams = function(custom_params) {
    var query_string = {},
        query = custom_params ? custom_params : window.location.search.substring(1),
        vars = query.split('&');

    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split('=');
        if (typeof query_string[pair[0]] === 'undefined') {
            query_string[pair[0]] = pair[1];
        } else if (typeof query_string[pair[0]] === 'string') {
            var arr = [ query_string[pair[0]], pair[1] ];
            query_string[pair[0]] = arr;
        } else {
            query_string[pair[0]].push(pair[1]);
        }
    }

    return query_string;
}

/**
 * Cookie helper method.
 */
var mtkCookie = function(name, value, ms) {
    if (arguments.length < 2) {
        // read cookie
        var cookies = document.cookie.split(';')
        for(var i=0; i < cookies.length; i++) {
            var c = cookies[i].replace(/^\s+/, '')
            if(c.indexOf(name+'=') == 0) {
                return decodeURIComponent(c.substring(name.length+1).split('+').join(' '))    
            }
        }
        return null
    }

    // write cookie
    var date = new Date()
    date.setTime(date.getTime()+ms)
    document.cookie = name+"=" + encodeURIComponent(value) + (ms ? ";expires="+date.toGMTString() : '') + ";path=/"
}

/**
 * Keys to process.
 */
const mtkKeys = [
    'mtke',
    'utm_campaign',
    'utm_source',
    'utm_medium',
    'utm_term',
    'utm_content',
    'utm_id',
];

/**
 * Go through each key.
 */
var mtkCartAttributes = {};
mtkKeys.forEach(function (key) {
    var cookieKey = 'mtk_' + key;
    var noteKey = '_metorik_' + key;

    /**
     * Continue if cookie not set and key exists.
     */
    if (! mtkCookie(cookieKey) && key in mtkGetParams()) {
        /**
         * Set in cart attributes to POST.
         */
        mtkCartAttributes[noteKey] = mtkGetParams()[key];

        /**
         * Set a cookie for 12 hours so we don't store again.
         */
        mtkCookie(
            cookieKey,
            true,
            1000 * 60 * 60 * 12 // 12 hours
        );
    }
});

/**
 * Track the referring site if not from this site.
 */
if (!mtkCookie('mtk_referer') && document.referrer && ! (document.referrer.indexOf(location.protocol + "//" + location.host) === 0)) {
    /**
     * Set in cart attributes to POST.
     */
    mtkCartAttributes['_metorik_referer'] = document.referrer;

    /**
     * Set a cookie for 1 day so we don't store again.
     */
    mtkCookie(
        'mtk_referer',
        true,
        1000 * 60 * 60 * 24 // 1 day
    );
};

/**
 * If have cart attributes to process, API request to set cart.
 */
if (Object.keys(mtkCartAttributes).length) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/cart/update.json', true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify({ attributes: mtkCartAttributes }));
}