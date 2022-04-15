<template>
  <div id="layout-view-box">
    	
  </div>
</template>
<script>
  // eslint-disable-next-line
  /* eslint-disable */
  import * as d3 from '../../static/js/d3.v4.min.js'
  import {vueFlaskRouterConfig} from '../flaskRouter'
  import bus from '../eventbus.js' // 事件总线.
  import axios from 'axios'
  import {jBox} from "../../static/js/jBox.js"
  // import { mapState } from 'vuex'

  export default {    
    data(){
      return {
      	
      }
    },
    computed: {       
    },
    watch: {
      
    },
    components: {
     
    },
    methods:{      
      
    },
    created(){
      let this_ = this;
      console.log("layoutView created");
      // vueFlaskRouterConfig.getStackedGraph
      // bus.$on('startStackedG', function (data){            
      //   if(data){
      //     this_.getStackedData();
      //   }
      // }); 
      
    },
    mounted(){
      console.log("layoutView mounted");
      let this_ = this;
      // this_.featureOptions = Object.keys(this_.$store.getters.getfilterIterms); // [x, x, ...]       
      
    },
    updated(){
      console.log("layoutView updated");
    },
    beforeDestroy(){
      console.log("layoutView beforeDestroy");
      // bus.$off("filterView");
    }   
  }
</script>