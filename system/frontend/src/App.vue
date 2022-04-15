<template>
  <div id="app">   
   <!-- App.vue作为页面入口文件 -->
    <div id="system-interface-box">
     <el-row class="entire-sys" :gutter="1"> <!--system div-->
      <el-row class="head-sys" :gutter="1"> <!--header div-->
        <div id="navg-div">
          <div class="app-setting">           
             <div class="setting-box">
                <selectdataset></selectdataset>
             </div>             
          </div>
          <div id="us-help">
             <div class="rt-text">About Us</div>             
          </div>
        </div>        
      </el-row>
      <el-row class="body-sys" :gutter="1"> <!--body div-->        
        <splitpanes watch-slots @resized="listenResized('resized', $event)" class="default-theme"> <!-- watch-slots 使用resize组件-->
          <pane :maxSize="leftBoxSplitSize" class="left-div"> <!--left side-->
            <div id="filterview">              
              <filterview></filterview>
            </div>
            <div id="semanticview">              
              <semanticview></semanticview>
            </div>
          </pane>        
          <pane :minSize="rightBoxSplitSize" class="right-div"> <!--right side-->                 
            <div id="layoutview">
              <layoutview></layoutview>
            </div>            
          </pane>
        </splitpanes>
      </el-row>       
     </el-row>
    </div>    
  </div>
</template>

<script>
  // eslint-disable-next-line
  /* eslint-disable */
  import Vue from 'vue' 
  import * as d3 from '../static/js/d3.v4.min.js' 
  import bus from './eventbus.js' // 事件总线.  
  import {vueFlaskRouterConfig} from './flaskRouter'
  import * as $ from "../static/js/jquery.min.js"  
  import axios from 'axios'
  import qs from 'qs'
  import {Splitpanes, Pane} from 'splitpanes' // splitter/resizer  
  import selectdataset from '@/components/selectDataset'  
  import {jBox} from "../static/js/jBox.js"
  import filterview from '@/components/filterView'
  import layoutview from '@/components/layoutView'
  import semanticview from '@/components/semanticView'    
  
  axios.interceptors.request.use(function (config) { // 只在App.vue中设置axios.interceptors.request.use就可以了,这样可避免跨域问题.切记:在flask中要用methods=["POST", "GET"],否则会出错的.
    if (config.method == 'post') {
      config.data = qs.stringify(config.data)
    }
    return config;
  }, function (error) {
    return Promise.reject(error);
  });

  export default {
    name: 'App',
    data(){
      return {
       // methodNorm: ["Z-Score", "Min-Max", "None"], // 原来, ["None", "Min-Max", "Z-Score"],
       leftBoxSplitSize: 29,
       rightBoxSplitSize: 71,                  
      
      }
    },
    created(){ 
      let this_ = this;     
      console.log("App.vue created");
      // datasetList
      let path = vueFlaskRouterConfig.dbnames;
      axios.get(path) // 用get的速度大于用post.
      .then((res) => {                        
          let data = res.data; // 获得指定数据库表格中的字段.            
          let dbnamelist = data.dbnamelist; // data = {dbnamelist: [x, ...]}
          console.log("dbnamelist"); console.log(dbnamelist);      
          this_.$store.commit("changedatasetList", dbnamelist);         
        })
      .catch((error) => {            
        console.error(error);
      }); 
           
    },
    methods: {       
            
            
    },

    components:{  // TODO: 注册组件后,就可以在template中像普通HTML元素一样使用,如<mainview></mainview>      
      Splitpanes, 
      Pane,
      selectdataset,
      // searchbox,
      filterview,
      layoutview,
      semanticview    
    },
    computed: {
      
    },
    watch:{
      rightBoxSplitSize:function(curVal, oldVal){
        if(curVal < 98){ // 右边视图扩大
           this.leftBoxSplitSize = 29;           
           this.rightBoxSplitSize = 71; // 右边
        }
      }      
    },
    mounted(){
      let this_ = this;
      console.log("App.vue mounted");

    },
    updated(){
      console.log("App updated");
    },
    beforeDestroy(){      
      console.log("APP beforeDestroy");
      
    }
  }
</script>
<style>
  @import 'splitpanes/dist/splitpanes.css';
  @import "../static/css/frontend.css";
  @import "../static/css/jBox.css";  
</style>