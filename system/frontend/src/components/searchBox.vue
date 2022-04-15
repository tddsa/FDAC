<template>
  <div id="node-search-box">    
    <div id="node-search-div">	    
      <el-select v-model="selectedAttr" placeholder="select">
        <el-option          
          v-for="item in $store.getters.getfieldList"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
      </el-select>
    </div>    
  </div>  
</template>

<script>
  import * as d3 from '../../static/js/d3.v4.min.js'
  import {vueFlaskRouterConfig} from '../flaskRouter'
  import bus from '../eventbus.js' // 事件总线.  
  import axios from 'axios'
  import {jBox} from "../../static/js/jBox.js" 
  import $ from 'jquery'
  import "../../static/js/jquery.contextMenu.js"
  import "../../static/js/jquery.ui.position.js"
    
  export default {
    data() {
      return {           
          searchKeywords: '',
          selectField: null,
          tableHeight: 250,
          returnDataList: [], // 用于存储后他返回的数据                   
          fieldList: [],
          dataAttrList: [],
          selectedAttr: ""   
          
      }
    },
    computed: {
      
    },
    watch: {
      searchKeywords: function(curVal, oldVal){
      	console.log(curVal);
      },
      selectField: function(curVal, oldVal){
      	let this_ = this;
      	let fieldVal = this_.$store.getters.getfieldList[parseInt(curVal)];      	
      	let param = {dbname: this_.$store.getters.getselectedDataset, field: fieldVal, attrType: this_.$store.getters.getfieldType[fieldVal]};
        axios.post(vueFlaskRouterConfig.getFieldAllVal, {
          param: JSON.stringify(param)
        })
        .then((res) => {
            this_.returnDataList.splice(0, this_.returnDataList.length);
            for(let i=0; i < res.data.length; i++){
		           let item = res.data[i];
		           this_.returnDataList.push(item.value);
		        }                 
        })
        .catch((error) => {            
          console.error(error);
        });
      }      
    },
    methods: {
     tableRowClassName({row, rowIndex}) {
        let rowClass = "row-" + row.ego.replace(/\./g, "-");
        return rowClass;
     },
     
     hoverCellHandle(row, column, cell, event){
        let this_ = this;
        
     },
     hoverCellLeaveHandle(row, column, cell, event){
        let this_ = this;
     },
  	 fuzzyQuery(list, keyWord) { // 模糊查询,从字符串中匹配出含有查询项的字符串.  	    
          let lowerCasekeyWord = keyWord.toLowerCase(); // 先转换成小写.
          let reg =  new RegExp(lowerCasekeyWord);
          let arr = [];
          if(list){
              for (let i = 0; i < list.length; i++) {
                let newStr = list[i].toLowerCase(); // 先转换成小写.
                if (reg.test(newStr)) {
                  let tempObj = {};
                  tempObj["value"] = list[i];                  
                  arr.push(tempObj);
                }
              }
          }                   
          return arr;        
  	 },
     querySearch(queryString, cb) { // 模糊匹配
        let this_ = this;        
        let allFieldData = this_.returnDataList; // [x, x, ...]        
        let results = this_.fuzzyQuery(allFieldData, queryString); // queryString实时输入的字符串, results必须是这种格式: [{value: x}, ...]        
        cb(results);
      },           
      handleSearch(item) { //当从下拉菜单选中某个值之后,触发该事件.
      	// console.log("selected k");
       //  console.log(item);
      },
      handleSelectField(item){
        // console.log("selected Field");
        // console.log(item);
      },
      creatEvent(){
          let this_ = this;
          
      },      
      minIndex(values, valueof) { // 数组最小值的索引
        let min;
        let minIndex = -1;
        let index = -1;
        if (valueof === undefined) {
          for (const value of values) {
            ++index;
            if (value != null
                && (min > value || (min === undefined && value >= value))) {
              min = value, minIndex = index;
            }
          }
        } else {
          for (let value of values) {
            if ((value = valueof(value, ++index, values)) != null
                && (min > value || (min === undefined && value >= value))) {
              min = value, minIndex = index;
            }
          }
        }
        return minIndex;
      },
      findIndexOfTopN(array, topN){
          let this_ = this;
          let indexOfArr = [];
          if(array.length <= topN){
             for(let i=0;i<array.length;i++){
                indexOfArr.push(i);
             }

          }
          else{
            let maxVal = d3.max(array); // 获得数组最大值.
            for(let i=0; i<topN; i++){
              let idx = this_.minIndex(array); // 找出数组最小值的索引
              indexOfArr.push(idx)
              array[idx]=maxVal; // 注意,这里改变了数组值.
            }
          }    
                   
          return indexOfArr;
      },
      computeDistancePoints(u, v, disMetric){ // todo: 核心:计算向量之间的相似性,使用余弦相似性.
          let len = u.length;
          // Canberra
          let distance = 0;
          if(disMetric == "canberra"){
            for ( let i = 0; i < len; i++ ) {
              let dif = u[i] - v[i];
              let difAbs = ( dif < 0 ) ? -dif : dif;
              let denom = ( ( u[i] < 0 ) ? -u[i] : u[i] ) + ( ( v[i] < 0 ) ? -v[i] : v[i] );
              distance += difAbs / denom;
            }
          }
          // Euclidean
          if(disMetric == "euclidean"){
              let sum = 0;
              for (let i = 0; i < len; i++) {
                  sum += Math.pow(u[i] - v[i], 2)
              }
              distance = Math.sqrt(sum);
          }
          return distance;
        
      }
    },
    created(){

    },
    mounted(){
      let this_ = this;
      this_.creatEvent();             
    },
    updated(){
      console.log("searchBox updated");
    }
  }
</script>
<style>
@import "../../static/css/jquery.contextMenu.css"; 
#ego-search-box #search-result-box td > div{
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}    
</style>>