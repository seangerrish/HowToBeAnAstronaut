var roleMetadata = {
  "role:1": new jobMetadata("Software Engineer", 1),
  "role:2": new jobMetadata("Software Engineer II", 1),
  "role:3": new jobMetadata("Mad Scientist", 2),
  "role:4": new jobMetadata("Normal Scientist", 2),
};

var roleNodes = [
  new jobNode(new jobDatum("role:1", -20, 0.2)),
  new jobNode(new jobDatum("role:2", -20, 0.1)),
  new jobNode(new jobDatum("role:3", -20, 0.8)), 
  new jobNode(new jobDatum("role:1", -10, 0.2)),
  new jobNode(new jobDatum("role:2", -10, 0.3)),
  new jobNode(new jobDatum("role:3", -10, 0.5)), 
  new jobNode(new jobDatum("role:1", -5, 0.2)),
  new jobNode(new jobDatum("role:2", -5, 0.1)),
  new jobNode(new jobDatum("role:4", -5, 0.2)),
];

var edges = [
  new edge(roleNodes[0], roleNodes[3], 0.1),
  new edge(roleNodes[0], roleNodes[4], 0.5),
  new edge(roleNodes[0], roleNodes[5], 0.2),
  new edge(roleNodes[1], roleNodes[3], 0.3),
  new edge(roleNodes[1], roleNodes[4], 0.4),
  new edge(roleNodes[1], roleNodes[5], 0.44),
  new edge(roleNodes[2], roleNodes[3], 0.4),
  new edge(roleNodes[2], roleNodes[4], 0.2),
  new edge(roleNodes[2], roleNodes[5], 0.4),
  new edge(roleNodes[3], roleNodes[6], 0.7),
  new edge(roleNodes[3], roleNodes[7], 0.4),
  new edge(roleNodes[3], roleNodes[8], 0.2),
  new edge(roleNodes[4], roleNodes[6], 0.4),
  new edge(roleNodes[4], roleNodes[7], 0.1),
  new edge(roleNodes[4], roleNodes[8], 0.4),
  new edge(roleNodes[5], roleNodes[6], 0.02),
  new edge(roleNodes[5], roleNodes[7], 0.3),
  new edge(roleNodes[5], roleNodes[8], 0.2),
];
