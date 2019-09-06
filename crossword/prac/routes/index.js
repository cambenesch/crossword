var express = require('express');
var router = express.Router();

// export our router to be mounted by the parent application
module.exports = router;

router.get('/', async (req, res) => {
  res.render('index', { title: 'This' });
});

router.get('/generate', async (req, res) => {
  // launches python child process for ml stuff after image is uploaded
  const { spawn } = require('child_process');
  const pyProg = spawn('python', ['./public/python/Solver.py']);

  pyProg.stdout.on('data', function (data) {

    console.log(data.toString());
  });

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  await sleep(60000);

  res.render('landing_answer', { title: 'Answer' });
});

router.post('/upload', async (req, res) => {
  if (req.files.length == 0) {
    return res.status(400).send('No files were uploaded.');
  }

  // The name of the input field (i.e. "inspectionSheet") is used to retrieve the uploaded file
  let inspectionSheet = req.files.image;

  console.log(inspectionSheet);

  // Use the mv() method to place the file somewhere on your server
  inspectionSheet.mv('./public/python/pic.jpg', function (err) {
    if (err)
      return res.status(500).send(err);

    res.render('landing_draw', { title: 'draw' });

  });
});