//var selectedAttribute = null;
$(document).ready(function(){
  $("#attribute-slct").change(function(){
    var selectedAttribute = $(this).val();
    var kernelNode = {};
    var kernelLink = {};
    d3Constraint.selectAll("#svg-box > *").remove();
    var svg = d3Constraint.select("#svg-box"), // fixme: d3Constraint���޸İ汾 d3��ԭ��
        width = +svg.attr("width"),
        height = +svg.attr("height");
    // 选择属性事件定义

    var color = d3.scaleOrdinal(d3.schemeCategory20);

    var simulationCommunity = d3.forceSimulation() // fixme: ����ȷ����������
    //    .force("link", d3.forceLink().id(function(d) { return d.id; }).distance(150))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));
    
    // simpleGraph sample_keyword  sample_DataMining
    // sample_MachineLearning  sample_Visualization  sample_HumanComputerInteraction
//    co-authorship_586652_1_num_citation_[(0, 70, 13), (70, 326, 13), (326, 653, 13)]_0
// co-authorship_586652_1_interests_['data mining', 'data set']_1
    var dataName = "citation_ad2284d6-dd1d-46cf-b8d9-3d50a672bf0e_1_keywords_['graph drawing', 'computer graphics', 'information visualization', 'network visualization', 'dynamic graph visualization']_0"
    var dataPath = "../data/" + dataName +  ".json"
d3.json(dataPath, function(error, graph) {
      if (error) throw error;
      var attr_list = Object.keys(graph.nodes[0])
      var exist = 0
      for (i in attr_list) {
        if (selectedAttribute == attr_list[i]) {
          exist = 1
          break
        }
      }
      if (exist == 0) {console.log('not have this attribute: ', selectedAttribute, attr_list); throw error;}
      
      for (i in graph.nodes){
        graph.nodes[i]['attribute1'] = graph.nodes[i][selectedAttribute].attribute
        graph.nodes[i]['same'] = graph.nodes[i][selectedAttribute].same
        graph.nodes[i]['unsame'] = graph.nodes[i][selectedAttribute].unsame
      }
      // graph = {links: [{source: x, target: x}, ...], nodes: [{}, ...]}
      // collect community center nodes information
      /*
      kernelNode: {a: {id: xx, member:[xx, ...], num: xx, x: xx, y: xx }, c: {��}, b: {��}}
      kernelLink: {ac:{source: {...}, target: {...}, ...}, ab: {��}, bc: {��}}
      */
      for (i in graph.nodes){
    //    console.log("i");console.log(i);
        if (!kernelNode[graph.nodes[i].attribute1]) {
          kernelNode[graph.nodes[i].attribute1] = {id: graph.nodes[i].attribute1, num: 1, member: [graph.nodes[i].id]};
        }
        else {
          kernelNode[graph.nodes[i].attribute1].num += 1;
          kernelNode[graph.nodes[i].attribute1].member.push(graph.nodes[i].id);
        }
      }
      // collect inter community links information
      for (i in graph.links){
        var source = graph.links[i].source;
        var target = graph.links[i].target;
        var label,
            sourceAttr,
            targetAttr;
        for (j in graph.nodes) {
          if (source == graph.nodes[j].id) { sourceAttr = graph.nodes[j].attribute1 };
          if (target == graph.nodes[j].id) { targetAttr = graph.nodes[j].attribute1 };
        }

        if (sourceAttr < targetAttr) {
          label = sourceAttr + targetAttr;
        }
        else if (sourceAttr > targetAttr) {
          label = targetAttr + sourceAttr;
        }
        if (label && !kernelLink[label]) {
          kernelLink[label] = {source: sourceAttr, target: targetAttr};
        }
      }
      // console.log("kernelNode");console.log(kernelNode);
      // console.log("kernelLink");console.log(kernelLink);

      // Calculate how many nodes each community contains
      console.log(kernelNode)
      graph.communityCount = {}
      for (i in kernelNode) {
        graph.communityCount[i] = kernelNode[i].num
      }

      // expand graph with kernelNode and kernelLink
      graph.kernelNodes = [];
      for (i in kernelNode) {
        graph.kernelNodes.push(kernelNode[i])
      }
      graph.kernelLinks = [];
      for (i in kernelLink) {
        graph.kernelLinks.push(kernelLink[i])
      }
    //  console.log("graph");console.log(graph)
      /*
      graph = {nodes: [{}, ...], links: [{}, ...], kernelNodes: [{id: xx, ...}, ...], kernelLinks: [{source: xx, target: xx, ...}]}
      */

      simulationCommunity
          .nodes(graph.kernelNodes)
          .force("link", d3.forceLink(graph.kernelLinks).id(function(d) { return d.id; }).distance(100))
    //       .links(graph.kernelLinks)
          .on("tick", function() {
    //          console.log("simulationCommunity tick");
          })
          .on("end", function(){ // TODO: ��ִ�����������֣�Ȼ���������ִ�нڵ�Լ�����֡�
              console.log("simulationCommunity end......");
              console.log(graph);
              var kJ = {}
              var total = 0;
              for (i in graph.kernelNodes) {
                kJ[graph.kernelNodes[i].id] = {}
                kJ[graph.kernelNodes[i].id].x = graph.kernelNodes[i].x;
                kJ[graph.kernelNodes[i].id].y = graph.kernelNodes[i].y;
                kJ[graph.kernelNodes[i].id].count = graph.communityCount[graph.kernelNodes[i].id];
                total = total + graph.communityCount[graph.kernelNodes[i].id];
              }
              console.log(kJ)
              for (i in graph.nodes) {
                var nodeNow = graph.nodes[i]
                nodeNow.kx = kJ[nodeNow.attribute1].x
                nodeNow.ky = kJ[nodeNow.attribute1].y
                nodeNow.count = kJ[nodeNow.attribute1].count
                nodeNow.total = total
                nodeNow.communityR = Math.sqrt(kJ[nodeNow.attribute1].count / total)* 500
              }
              console.log(graph.nodes)
              // draw community positions
              // console.log(graph.kernelNodes)
              var comNode = svg.append("g")
                         .attr("class", "com-nodes")
                         .selectAll("g")
                         .data(graph.kernelNodes)
                         .enter().append("g");
              comNode.attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")";
              });
              var comCircles = comNode.append("circle")
                              .attr("r", 15)
                              .attr("fill", function(d) { return color(d.id); });

              //
              var simulationGraph = d3Constraint.forceSimulation()  // fixme�����ڻ�������ͼ
                                    .force("link", d3Constraint.forceLink().id(function(d) { return d.id; }).distance(100))
                                    .force("charge", d3Constraint.forceManyBody())
                                    // .force("center", d3Constraint.forceCenter(width / 2, height / 2));
                  console.log("Now, start graph layout......");
                  simulationGraph
                      .nodes(graph.nodes)
                      .on("tick", ticked)
                      .on("end", function() {
                        console.log("get graph data");
                        console.log(graph);
                        graph['filename'] = [dataName, selectedAttribute, 'our method']
                        var saveName = dataName + '_' + selectedAttribute + '_' + 'our method'
                        var savePath = '../result/' + saveName + '.json'
//                        saveJSON(graph, savePath)
                      });

                  simulationGraph.force("link")
                      .links(graph.links);
                  function dragstarted(d) {
                    if (!d3Constraint.event.active) simulationGraph.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                  }

                  function dragged(d) {
                    d.fx = d3Constraint.event.x;
                    d.fy = d3Constraint.event.y;
                  }

                  function dragended(d) {
                    if (!d3Constraint.event.active) simulationGraph.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                  }
                  var link = svg.append("g")
                            .attr("class", "links")
                            .selectAll("line")
                            .data(graph.links)
                            .enter().append("line")
                            .attr("stroke-width", function(d) { return Math.sqrt(d.value); });

                  var node = svg.append("g")
                      .attr("class", "nodes")
                    .selectAll("g")
                    .data(graph.nodes)
                    .enter().append("g")

                  var circles = node.append("circle")
                      .attr("r", 5)
                      .attr("fill", function(d) { return color(d.attribute1); })
                      .call(d3Constraint.drag()
                          .on("start", dragstarted)
                          .on("drag", dragged)
                          .on("end", dragended));

                  var lables = node.append("text")
                      .text(function(d) {
                        return d.label;
                      })
                      .attr('x', 6)
                      .attr('y', 3);

                  node.append("title")
                      .text(function(d) { return d.label; });

                  function ticked() {
    //                console.log("simulationGraph tick");
                    link.attr("x1", function(d) { return d.source.x; })
                        .attr("y1", function(d) { return d.source.y; })
                        .attr("x2", function(d) { return d.target.x; })
                        .attr("y2", function(d) { return d.target.y; });

                    node.attr("transform", function(d) {
                          return "translate(" + d.x + "," + d.y + ")";
                        });
                  }
           });

    });


  });
});

function saveJSON(data, filename) {
  if (!data) {
      alert('保存的数据为空');
      return;
  }
  if (!filename)
      filename = 'json.json'
  if (typeof data === 'object') {
      data = JSON.stringify(data, undefined, 4)
  }
  var blob = new Blob([data], {type: 'text/json'}),
      e = document.createEvent('MouseEvents'),
      a = document.createElement('a')
  a.download = filename
  a.href = window.URL.createObjectURL(blob)
  a.dataset.downloadurl = ['text/json', a.download, a.href].join(':')
  e.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null)
  a.dispatchEvent(e)
}

