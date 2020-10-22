
var headers = {
    'Authorization': 'Bearer demo',
    'Accept': 'application/json'
  };
  var url = 'https://api.humanapi.co/v1/human/test_results?limit=1'
  
  request({
    method: 'GET',
    uri : url,
    headers : headers
    }, function (error, res, body) {
      var parsedResponse;
      if (error) {
        callback(new Error('Unable to connect to the Human API endpoint.'));
      } else {
        if(res.statusCode == 401) {
          logger.debug("Unauthorized request, validate access token");
          callback(null, { status: 'unauthorized' });
        } else {
          try {
            parsedResponse = JSON.parse(body);
          } catch (error) {
            return callback(new Error('Error parsing JSON response from Human API.'));
          }
          // At this point you can use the JSON object to access the results
          console.log("Latest test result name");
          console.log(parsedResponse[0]["name"]);
          return callback(null, parsedResponse);
        }
      }
  });