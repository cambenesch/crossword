var currentBlock = 0;							// current location 0->dimension*dimension
var acrossclues = "";							// HTML string of clues
var downclues = "";								// HTML string of clues
var dimension = 0;								// crossword grid size
var emptyBlocks;								// how many empty squares left
var totalEmpty;									// how many empty squares at start
var autocheck = false;							// goes true when emptyBlocks = 0
var blocks = [];								// multidimensional array with solution characters and blacks
var cluenums = [];								// multidimensional array with clue numbers for building svg
var cluenum = 1;								// 
var clues = {									// object storing the clues
  across: {},
  down: {}
};
var characters;

d3.csv('/python/cluedata.csv', getClues);

function getClues(cluesrc) {
  for (k = 0; k < cluesrc.length; k++) {
    if (cluesrc[k].dir === 'across') {
      clues.across[cluesrc[k].key] = cluesrc[k].clue.replace('&#44;', ',');
    }
    else if (cluesrc[k].dir === 'down') {
      clues.down[cluesrc[k].key] = cluesrc[k].clue.replace('&#44;', ',');
    }
    else if (cluesrc[k].dir === 'size') {
      dimension = parseInt(cluesrc[k].clue);
      emptyBlocks = dimension * dimension;
      totalEmpty = emptyBlocks;
    }
    else if (cluesrc[k].dir === 'letters') {
      characters = cluesrc[k].clue;
    }
  }

  for (i = 0; i < Object.entries(clues.across).length; i++) {
    acrossclues += "<p id='a" + Object.entries(clues.across)[i][0] + "' style='font-size: 13px; color: white; margin: 0.25em 0; line-height: 1.25em;' onclick='clueSelect(this.id, \"cluelist\")'>" + Object.entries(clues.across)[i][0] + ". " + Object.entries(clues.across)[i][1] + "</p>";
  }
  document.getElementById('cluesacross').innerHTML = acrossclues;

  for (i = 0; i < Object.entries(clues.down).length; i++) {
    downclues += "<p id='d" + Object.entries(clues.down)[i][0] + "' style='font-size: 13px; color: white; margin: 0.25em 0; line-height: 1.25em;' onclick='clueSelect(this.id, \"cluelist\")'>" + Object.entries(clues.down)[i][0] + ". " + Object.entries(clues.down)[i][1] + "</p>";
  }
  document.getElementById('cluesdown').innerHTML = downclues;

  buildGrid();
}

function buildGrid() {
  // convert characters string into multidimensional array
  // spaces are used to indicate black squares in crossword
  for (i = 0; i < dimension; i++) {
    blocks.push([]);
    for (j = i * dimension; j < (i * dimension) + dimension; j++) {
      blocks[i].push(characters.slice(j, j + 1));
    }
  }

  // fill cluenums array with numbers
  for (i = 0; i < dimension; i++) {
    cluenums.push([]);
    for (j = 0; j < dimension; j++) {
      if (i === 0) {
        if (blocks[i][j] !== " ") {
          cluenums[i].push(cluenum);
          cluenum++;
        }
        else {
          cluenums[i].push("");
        }
      }
      else {
        if (j === 0 && blocks[i][j] !== " ") {
          cluenums[i].push(cluenum);
          cluenum++;
        }
        else if (blocks[i][j - 1] === " " && blocks[i][j] !== " ") {
          cluenums[i].push(cluenum);
          cluenum++;
        }
        else if (blocks[i - 1][j] === " " && blocks[i][j] !== " ") {
          cluenums[i].push(cluenum);
          cluenum++;
        }
        else {
          cluenums[i].push("");
        }
      }
    }
  }
  var crossword = d3.select("#crossword");

  for (i = 0; i < dimension; i++) {
    for (j = 0; j < dimension; j++) {
      var block = crossword.append('g')
        .attr('id', 'r' + i + 'c' + j);
      var cell = block.append('rect')
        .attr('value', i + j)
        .attr('class', 'letterbox')
        .attr('x', j * 40 + 1)
        .attr('y', i * 40 + 1)
        .attr('width', 40)
        .attr('height', 40)
        .attr('style', 'stroke-width: 1; stroke: rgb(55,55,55); fill: rgb(255,255,255);');
      if (blocks[i][j] === " ") {
        emptyBlocks--;
        cell.attr('style', 'stroke-width: 1; stroke: rgb(55,55,55); fill:rgb(0,0,0);')
          .attr('class', 'blackbox');
      }
      else {
        if (cluenums[i][j] !== "") {
          block.append('text')
            .attr('x', j * 40 + 4)
            .attr('y', i * 40 + 12)
            .attr('style', 'fill: black; font-size: 10px;')
            .attr('id', 'clue' + cluenums[i][j])
            .text(cluenums[i][j]);
        }
      }
      var curr = characters.slice(i * dimension + j, i * dimension + j + 1);
      block.append('text')
        .attr('class', 'inputText')
        .attr('x', j * 40 + 20)
        .attr('y', i * 40 + 35)
        .attr('text-anchor', 'middle')
        .text(curr)
        .attr('style', 'fill: black; font-size: 30px;');
    }
  }
}