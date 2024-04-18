const express = require('express');
const path = require('path');
const app = express();
app.use(express.static(path.join(__dirname, 'public')));

port = process.env.PORT || 4000
app.listen(port, () => console.info(`App listening on port ${port}`))