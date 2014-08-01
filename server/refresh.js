
function redraw(data, layout) {

  roleMetadata = data.roleMetadata;
  edges = data.edges;
  roleNodes = data.roleNodes;

var params = {
 "dom": "chart",
 "width":    860,
 "height":    500,
"nodeWidth":     250,
"nodePadding":     10,
"nodeMargin":     10,
"layout":     32,
"id": "chart" 
};

params.units ? units = " " + params.units : units = "";

//hard code these now but eventually make available
var formatNumber = d3.format("0,.0f"),    // zero decimal places
    format = function(d) { return formatNumber(d) + units; },
    color = d3.scale.category20();

var sankey = d3.sankey()
    .nodeWidth(params.nodeWidth)
    .nodePadding(params.nodePadding)
    .nodeMargin(params.nodeMargin)
    .layout(params.layout)
    .size([params.width,params.height]);
var path = sankey.link();
    
var links = [],
    nodes = [];

////////// TODO(gerrish): move this to sankey.js. /////////////

/*
// get all source and target into nodes
// will reduce to unique in the next step
// also get links in object form
data.source.forEach(function (d, i) {
    nodes.push({ "name": data.source[i] });
    nodes.push({ "name": data.target[i] });
    links.push({ "source": data.source[i], "target": data.target[i], "value": +data.value[i] });
});
*/

// Populate the list of edges.
edges.forEach(function(e, i) {
    nodes.push({ "name": e.startJobNode });
    nodes.push({ "name": e.endJobNode });
    links.push({ "index": i, "source": e.startJobNode, "target": e.endJobNode, "value": +e.weight });
});

// Now get nodes based on links data
// thanks Mike Bostock https://groups.google.com/d/msg/d3-js/pl297cFtIQk/Eso4q_eBu1IJ
// this handy little function returns only the distinct / unique nodes
nodes = d3.keys(d3.nest()
                .key(function (d) { return d.name.id; })
                .map(nodes));

//sfsdf
//  it appears d3 with force layout wants a numeric source and target
//  so loop through each link replacing the text with its index from node
links.forEach(function (d, i) {
    links[i].source = nodes.indexOf(links[i].source.id);
    links[i].target = nodes.indexOf(links[i].target.id);
});

// Now loop through each node to make nodes an array of objects rather than an array of strings
nodes.forEach(function (d, i) {
    nodes[i] = { "name": d };
//    alert(d);
});

var nodesData = {};
roleNodes.forEach(function(d) {
  nodesData[d.id] = d;
});


/////////////

sankey
  .nodes(nodes)
  .links(links)
  .layout(params.layout);

var svg = d3.select('#' + params.id).selectAll("svg")
    .attr("style", "padding: 10px 10px 10px 10px;")
    .attr("width", params.width)
    .attr("height", params.height);
  
var node = svg.append("g").selectAll(".input")
  .data([ "link1" ])
  .enter().append("rect")
  .attr("class", "node")
  .attr("id", function(d) { return d })
  .attr("size", "14")
  .attr("type", "text")
  .attr("x", 10)
  .attr("height", "50")
  .attr("width", "50")
  .attr("fill", "rgb(103,201,101);")
  .attr("y", 100);

node.append("input").append("text")
  .attr("x", 10)
  .attr("y", function (d) { return 0; })
  .attr("transform", null)
  .attr("class", "job-text")
  .attr("style", "font-size: 20px; font-family: \"Open Sans\",\"Helvetica Neue\",Arial,sans-serif; font-weight: 500;")
//  .text(function (d) { return "Pretty print job:" + roleMetadata[d.job.roleId].prettyName; });
//  .attr("size", "14")
//  .attr("id", "moo");

var link = svg.append("g").selectAll(".link")
  .data(links)
.enter().append("path")
  .attr("class", "link")
  .attr("d", path)
  .style("stroke-width", function (d) { return Math.max(0.5, d.dy); })
  .sort(function (a, b) { return b.dy - a.dy; });

link.append("title")
  .text(function (d) { return format(d.value * 100) + " percent of people in the role " + d.source.name + " were eventualy in the role " + d.target.name + "."; });

var node = svg.append("g").selectAll(".node")
    .data(nodes, function(d) { return d.name; })
  .enter().append("g")
    .attr("class", "node button")
    .attr("href", "#")
    .attr("transform", function (d) { return "translate(" + d.x + "," + d.y + ")"; });

var STROKE_WIDTH = 6;

node.append("rect")
    // Node height is a maximum of 100, a minimum of 50 (not yet, but eventually).
    .attr("height", function (d) { return d.dy; return Math.max(200, Math.min(100, d.dy)); })
    .attr("width", sankey.nodeWidth())
    .text(function(d) { return "foo"; })
    .attr("ry", 10)
    .attr("rx", 10)
    .style("fill", function (d) { return d3.rgb(d.color = color(d.name)).darker(-.5); })
    // .replace(/ .*/, "")); })
    .style("stroke", function (d) { return d3.rgb(d.color).darker(-.1);
                     })
    .style("stroke-width", STROKE_WIDTH)
    .style("stroke-opacity", 1)
    .on("click", function(d) {
                   handleNodeClick(d);
                 }) 
    .on("mouseover", function(d) {
                   handleNodeHover(this, d);
                 })
    .on("mouseout", function(d) {
                   handleNodeHoverEnd(this, d);
   //                var n = d3.select(this);
// n.style("fill", function(d) { return d3.rgb(d.color).darker(-1; });
                 })

// Append information to display on hover.
  .append("title")
    .text(function (d) { return "Name: " + d.name + "\n" + "Value: " + format(d.value); });

node.append("title")
  .attr("center", "true")
  .attr("text-anchor", "end")
  .text(function (d) { return "name: " + d.name; })
  .attr("text-anchor", "start");

node.append("text")
  .attr("x", 10)
  .attr("y", function (d) { return d.dy / 2 - 10; })
  .attr("dy", ".35em")
  .attr("transform", null)
  .attr("class", "job-text")
  .attr("style", "font-size: 18px; font-family: \"Open Sans\",\"Helvetica Neue\",Arial,sans-serif; font-weight: 500;")
  .text(function (d) { return roleMetadata[nodesData[d.name].job.roleId].prettyName; })
node.append("text")
  .attr("x", 10)
  .attr("y", function (d) { return d.dy / 2 + 10; })
  .attr("dy", ".35em")
  .attr("class", "job-text")
  .attr("transform", null)
  .attr("style", "font-size: 16px; font-family: \"Open Sans\",\"Helvetica Neue\",Arial,sans-serif; font-weight: 500;")
  .text(function (d) { return "text:" + format(d.value * 100, 0); })

// This drag handler is disabled for now.
  // the function for moving the nodes
  function dragmove(d) {
    d3.select(this).attr("transform", 
        "translate(" + (
                   d.x = Math.max(0, Math.min(params.width - d.dx, d3.event.x))
                ) + "," + (
                   d.y = Math.max(0, Math.min(params.height - d.dy, d3.event.y))
                ) + ")");
        sankey.relayout();
        link.attr("d", path);

  }
}

function handleNodeHover(t, node) {
  var n = d3.select(t);
  n.style("fill", function(d) {
    return d3.rgb(d.color).darker(-.9);
  });

  n.transition().attr("height", function(d) {
                    return Math.max(40, d.dy);
                  })
//                .attr("y", function(d) {
  //                 return d.y; - (Math.max(40, d.dy) - d.dy) / 2.0;
    //             })
                  .duration(200);

  texts = n.selectAll("text");
  texts.transition().attr("style", "font-size: 20x; font-weight:800;").duration(40);
}

function handleNodeClick(node) {
  alert("click: " + node);
}
  
function handleNodeHoverEnd(t, node) {
  var n = d3.select(t);
  n.style("fill", function(d) {
  return d3.rgb(d.color).darker(-.5); });
  n.transition().attr("height", function(d) {
                    return d.dy;
                  })
                .duration(200);
}

// s = svg.input.text(18, 18, "Apples\nBananas\nSparrows\nStars", {width: '200'});
