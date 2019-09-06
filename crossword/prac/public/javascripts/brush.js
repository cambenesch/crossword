var img = new Image;
img.src = "/python/pic.jpg";
img.onload = function () {
	var imgW = this.width;
	var imgH = this.height;
	var svg = d3.select(".picture")
		.append("svg")
		.attr("width", imgW)
		.attr("height", imgH)
		.attr("id", "main");
	var points = [];
	svg.append("image")
		.attr("xlink:href", "/python/pic.jpg")
		.attr("width", imgW)
		.attr("height", imgH)
		.attr("id", "pic")
		.on("click", function () {
			var x = Math.floor(d3.event.pageX - document.getElementById("main").getBoundingClientRect().x - window.scrollX);
			var y = Math.floor(d3.event.pageY - document.getElementById("main").getBoundingClientRect().y - window.scrollY);
			svg.append("circle")
				.attr("cx", x)
				.attr("cy", y)
				.attr("r", 5)
				.style("fill", "red");
			points.push([x, y]);
			if (points.length == 4) {
				var pointsCSV = "data:text/csv;charset=utf-8," + points.map(e => e.join(",")).join("\n");
				var encodedUri = encodeURI(pointsCSV);
				var link = document.createElement("a");
				link.setAttribute("href", encodedUri);
				link.setAttribute("download", "points.csv");
				document.body.appendChild(link);
				link.click();
				const fs = require('fs');
			};
		});

    /*
    var b = d3.brush()
	.extent([[0, 0],[imgW, imgH]])
    .on("brush", brushed)
	.on("end", brushed);
    svg.append("g")
	.call(b);
    function brushed() {
	console.log(d3.event.selection);
    }
    */
}
