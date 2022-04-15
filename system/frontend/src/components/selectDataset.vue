<template>		    
	 <div id=select-dataset>
    <span class="md-name">Dataset:</span>     
    <el-select 
      v-model="selectedDataset"
      size="mini" 
      filterable
      @visible-change="dropDownBoxVisible" 
      placeholder="Select">
      <el-option
          v-for="(item, index) in $store.getters.getdatasetList"
          :key="item"
          :label="item"
          :value="item">
      </el-option>
    </el-select>
   </div>		
</template>

<script>
  // eslint-disable-next-line
  /* eslint-disable */
  import * as d3 from '../../static/js/d3.v4.min.js'
  import {vueFlaskRouterConfig} from '../flaskRouter'
  import bus from '../eventbus.js' // 事件总线.
  import axios from 'axios'
  import $ from 'jquery'
  // import { mapState } from 'vuex'

  export default {  
    data(){
      return {
        selectedDataset: null        
      }
    },
    computed: {
       
    },
    watch: {
      selectedDataset: function(curVal, oldVal){
        let this_ = this;        
        this_.$store.commit('changeselectedDataset', curVal); // 将选中的数据集的名字保存在store.js
        let param = {dbname: curVal};
        axios.post(vueFlaskRouterConfig.selectdataset, {
          param: JSON.stringify(param)
        })
        .then((res) => { 
                let data = res.data;
                // console.log("get data");
                // console.log(data);
                this_.$store.commit("changefieldList", data.attrs); // [{value: x, label: x}, ...]
                this_.$store.commit("changefieldType", data.attrTypes); // e.g., {'year': 'integer', 'n_citation': 'integer', 'keywords': 'text', 'public_venue': 'text'}
          })
        .catch((error) => {            
          console.error(error);
        });                
      }
    },
    components: {
     
    },
    methods:{      
      dropDownBoxVisible(){
        let this_ = this;
        console.log("selecting dataset");
      }
    },
    created(){
      console.log("created");      
    },
    mounted(){
      console.log("mounted");
      let this_ = this;
    },
    updated(){
      console.log("selectDataset updated");
    },
    beforeDestroy(){
      console.log("selectdataset beforeDestroy");
    }   
  }
</script>

<style>


</style>