const fs = require('fs');
const https = require('https');

const file = fs.createWriteStream('get-pip.py');
https.get('https://bootstrap.pypa.io/get-pip.py', function(response) {
  response.pipe(file);
  file.on('finish', function() {
    file.close();
  });
});