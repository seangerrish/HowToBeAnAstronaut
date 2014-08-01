function jobMetadata(prettyName, cluster) {
  this.prettyName = prettyName;
  this.cluster = cluster;
}

/**
 * Stores information about a single job.
 *
 *
**/
function jobDatum(roleId, startTime, weight) {
  this.roleId = roleId;
  this.startTime = startTime;

  this.weight = weight;
}

/**
 *
**/
function edge(startJobNode, endJobNode, weight) {
  this.startJobNode = startJobNode;
  this.endJobNode = endJobNode;
  this.weight = weight;
}

/**
 * clusterNode is a perfectly legitimate node.
 *
**/
function clusterNode(clusterDatum, jobs) {
  this.cluster = clusterDatum;
  jobs = jobs;
  this.render = function(d) {
  };
};

/**
 * jobNode is a node for D3.
**/
function jobNode(jobDatum) {
  this.job = jobDatum;
  this.sourceLinks = [];
  this.targetLinks = [];
  this.render = function(d) {
  
  };
  this.id = jobDatum.roleId + ":" + jobDatum.startTime;
};
