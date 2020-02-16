const express = require('express')
const app = express()
const port = 3000

const scheduler = require('./scheduler');


scheduler();
app.get('/', (req, res) => res.send('Hello World!'));


app.listen(port, () => console.log(`Campus Outlook Event Scraper listening on ${port}!`))