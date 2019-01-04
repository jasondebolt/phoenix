var http = require('http');

let containerId;

String.prototype.supplant = function (o) {
    return this.replace(/{([^{}]*)}/g,
        function (a, b) {
            var r = o[b];
            return typeof r === 'string' || typeof r === 'number' ? r : a;
        }
    );
};

exports.handler = function(event, context, callback) {
    // setup request options and parameters
    console.log("EVENT:");
    console.log(event);

    if (!containerId) {
        containerId = context.awsRequestId;
    }
    console.log('containerId', containerId);

    // If this a schedule pre-warming ping request, respond and exit function.
    // https://read.acloud.guru/how-to-keep-your-lambda-functions-warm-9d7e1aa6e2f0
    if (event.name  == 'pinger') {
        console.log('Request from pinger');
        return callback(null, {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Pong',
            })
        })
    }

    var options = {
      host: event.requestParams.hostname,
      port: event.requestParams.port,
      path: event.requestParams.path.supplant(event.params.path),
      method: event.requestParams.method
    };

    // if I have headers set them otherwise set the property to an empty map
    if (event.params && event.params.header && Object.keys(event.params.header).length > 0) {
        options.headers = event.params.header
    } else {
        options.headers = {};
    }

    // force the user agent and the forwaded for headers forcefully because we want to
    // take them from the API Gateway context rather than letting Node.js set the Lambda ones
    options.headers["User-Agent"] = event.context["user-agent"];
    options.headers["X-Forwarded-For"] = event.context["source-ip"];
    // if I don't have a content type I force it application/json
    // Test invoke in the API Gateway console does not pass a value
    if (!options.headers["Content-Type"]) {
        options.headers["Content-Type"] = "application/json";
    }
    // build the query string
    if (event.params && event.params.querystring && Object.keys(event.params.querystring).length > 0) {
        var queryString = generateQueryString(event.params.querystring);

        if (queryString !== "") {
            options.path += "?" + queryString;
        }
    }

    // define my callback to read the reponse and generate a json output for API Gateway.
    // The json output is parsed by the mapping templates
    callback = function(response) {
        var responseString = '';

        //another chunk of data has been recieved, so append it to `str`
        response.on('data', function (chunk) {
            responseString += chunk;
        });

        //the whole response has been recieved, so we just print it out here
        response.on('end', function () {
            // parse response to json
            var jsonResponse = JSON.parse(responseString);

            var output = {
                status: response.statusCode,
                bodyJson: jsonResponse,
                headers: response.headers
            };
            console.log("OUTPUT");
            console.log(output);

            // if the response was a 200 we can just pass the entire JSON back to
            // API Gateway for parsing.
            if (response.statusCode == 200) {
                context.succeed(output);
            } else {
                // set the output JSON as a string inside the body property
                output.bodyJson = responseString;
                // stringify the whole thing again so that we can read it with
                // the $util.parseJson method in the mapping templates
                context.fail(JSON.stringify(output));
            }
        });
    }

    console.log("OPTIONS:");
    console.log(options);
    var req = http.request(options, callback);

    if (event.bodyJson && event.bodyJson !== "") {
        console.log("BODY_JSON:");
        console.log(event.bodyJson);
        req.write(JSON.stringify(event.bodyJson));
    }

    req.on('error', function(e) {
        console.log('problem with request: ' + e.message);
        context.fail(JSON.stringify({
            status: 500,
            bodyJson: JSON.stringify({ message: "Internal server error" })
        }));
    });

    req.end();
}

function generateQueryString(params) {
    var str = [];
    for(var p in params) {
        if (params.hasOwnProperty(p)) {
            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(params[p]));
        }
    }
    return str.join("&");
}
