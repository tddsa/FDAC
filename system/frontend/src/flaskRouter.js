// eslint-disable-next-line
/* eslint-disable */
const backPort = 'http://127.0.0.1:5000';
const vueFlaskRouterConfig = {	
	dbnames: backPort + "/selectdataset/dbnames",
	getFieldAllVal:	backPort + "/search/getFieldAllVal",
	selectdataset: backPort + "/selectdataset/whichdb",
	getQueryResults: backPort + "/search/getQueryResults",
	getGraphSC: backPort + "/semantic/graph"
};
// let searchFlag=false; // 搜索点击标志位.
export {	
	vueFlaskRouterConfig
	// searchFlag,
}