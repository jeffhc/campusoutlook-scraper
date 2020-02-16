var cron = require('node-cron');
 
function scrape() {
  var spawn = require("child_process").spawn; 
  var process = spawn('python',["./hello.py", 
                          req.query.firstname, 
                          req.query.lastname] ); 

  // Takes stdout data from script which executed 
  // with arguments and send this data to res object 
  process.stdout.on('data', function(data) { 
      console.log('>>> ' + data.toString());
  }) 
}

module.exports = () => {
  console.log('test');
  scrape();
  // cron.schedule('* * * * *', () => {
  //   console.log('Scraping every minute');
  //   scrape();
  // });
}