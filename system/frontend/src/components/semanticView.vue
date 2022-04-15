<template>
  <div id="semantic-view-box">
    <div id="attr-search-box">    
      <div id="attr-search-div">      
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
    <div id="select-attr-div">
      <!-- <el-checkbox :indeterminate="isIndeterminate" v-model="checkAll" @change="handleCheckAllChange">Select All</el-checkbox> -->
      <!-- <div style="margin: 5px 0;"></div> -->
      <el-checkbox-group v-model="checkedItems" @change="handleCheckedChange">
        <el-checkbox v-for="item in AllItemList" :label="item" :key="item">{{item}}</el-checkbox>
      </el-checkbox-group>
    </div> 
    <div id="semantic-community">
      <el-tag
        v-for="tag in checkedItems"
        :key="tag"
        :disable-transitions="false"
        closable
        @close="handleCloseTag(tag)"
        :type="tag">
        {{tag}}
      </el-tag>
    </div>
    <div id="ok-div">
      <div id="ok-SC-div">Run</div>
    </div> 	
  </div>
</template>
<script>  
  /* eslint-disable */
  import * as d3 from '../../static/js/d3.v4.min.js'
  import {vueFlaskRouterConfig} from '../flaskRouter'
  import bus from '../eventbus.js' // 事件总线.
  import axios from 'axios'
  import {jBox} from "../../static/js/jBox.js"  

  export default {    
    data(){
      return {
      	checkAll: false,
        checkedItems: [],
        AllItemList: [],        
        selectedAttr: "",
        topN: 10,
        returnDataList: [] // [X, X, X, ...]
      }
    },
    computed: {       
    },
    watch: {
      selectedAttr: function(curVal, oldVal){
        let this_ = this;
        console.log("selectedAttr", this_.selectedAttr);
        // let fieldVal = this_.$store.getters.getfieldList[parseInt(curVal)];       
        let param = {dbname: this_.$store.getters.getselectedDataset, field: curVal, attrType: this_.$store.getters.getfieldType[curVal]};
        axios.post(vueFlaskRouterConfig.getFieldAllVal, { // getGraphSC
          param: JSON.stringify(param)
        })
        .then((res) => {
            this_.returnDataList.splice(0, this_.returnDataList.length);
            for(let i=0; i < res.data.length; i++){
               let item = res.data[i];
               this_.returnDataList.push(item.value);
            }
            // console.log("selectedAttr", this_.returnDataList);
            this_.AllItemList = this_.returnDataList.slice(0, this_.topN);                
        })
        .catch((error) => {            
          console.error(error);
        });
      }
      
    },
    components: {
     
    },
    methods:{
      clickOkEvent(){
        let this_ = this;
        d3.select("#ok-SC-div").on("click", function(){
          let param = {dbname: this_.$store.getters.getselectedDataset, field: this_.selectedAttr, SCList: this_.checkedItems};
          axios.post(vueFlaskRouterConfig.getGraphSC, { // getGraphSC
            param: JSON.stringify(param)
          })
          .then((res) => {
              console.log("res clickOkEvent", res.data);               
          })
          .catch((error) => {            
            console.error(error);
          });
        });
      },
      handleCheckAllChange(val) {
        let this_ = this;
        this_.checkedItems = val ? this_.AllItemList : [];
        this_.isIndeterminate = false;
      },
      handleCheckedChange(value) {
        let this_ = this;
        let checkedCount = value.length;
        // this_.checkAll = checkedCount === this_.AllItemList.length;
        // this_.isIndeterminate = checkedCount > 0 && checkedCount < this_.AllItemList.length;
      },
      handleCloseTag(tag){
        let this_ = this;
        this_.checkedItems.splice(this_.checkedItems.indexOf(tag), 1);
      }      
    },
    created(){
      let this_ = this;
      console.log("filterView created");
      // vueFlaskRouterConfig.getStackedGraph
      // bus.$on('startStackedG', function (data){            
      //   if(data){
      //     this_.getStackedData();
      //   }
      // });      
    },
    mounted(){
      console.log("filterView mounted");
      let this_ = this;
      // this_.featureOptions = Object.keys(this_.$store.getters.getfilterIterms); // [x, x, ...]
      this_.clickOkEvent();
    },
    updated(){
      console.log("filterView updated");
    },
    beforeDestroy(){
      console.log("filterView beforeDestroy");
      // bus.$off("filterView");
    }   
  };
</script>