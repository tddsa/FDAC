import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex); // 使用vue插件, vue.use(插件)

const store = new Vuex.Store({  // 用const意味着地址不变,而对象的键值对是可以更改的.
  state: {  
    selectDataset: {
      datasetList: [], // database name , e.g., ["enron", ...]
      selectedDataset: null, // 'enron'
    },
    searchBox: {
      fieldList: [],
      fieldType: null // {attr1: type, attr2: type, ...}
    }    
  },
  getters: {  // 读取state的值,简化组件中读取state的代码.类似于computed属性,调用的时不用加(),e.g. state.xxx, 而非state.xxx()
    getfieldList(state){ // this_.$store.getters.getfieldList
      return state.searchBox.fieldList;
    },
    getdatasetList(state){
      return state.selectDataset.datasetList;
    },
    getselectedDataset(state){  // 在组件中的调用方式:this_.$store.getters.getselectedDataset
      return state.selectDataset.selectedDataset;
    },
    getfieldType(state){ // this_.$store.getters.getfieldType
      return state.searchBox.fieldType;
    }

  },
  mutations: {  // 对state中的状态进行修改.简化组件中对state的修改. 调用方式: this.$store.commit('changeSelection', mao); 
    changedatasetList(state, newdatasetList){ // newdatasetList=[x, x, ...]
      state.selectDataset.datasetList.splice(0, state.selectDataset.datasetList.length);
      for(let i=0; i < newdatasetList.length; i++){
         let item = newdatasetList[i];
         state.selectDataset.datasetList.push(item);
      }      
    },
    changeselectedDataset(state, newState){ // this_.$store.commit('changeselectedDataset', mao);      
      state.selectDataset.selectedDataset = newState;
    }, 
    changefieldList(state, newState){ // this_.$store.commit("changefieldList", newState)
      state.searchBox.fieldList.splice(0, state.searchBox.fieldList.length);
      for(let i=0; i < newState.length; i++){
         let item = newState[i];
         state.searchBox.fieldList.push(item);
      }
    },
    changefieldType(state, newState){ // this_.$store.commit("changefieldType", newState)
      state.searchBox.fieldType = newState; //  
    }
    
  },
  actions: { // 对state进行异步修改,mutations的升级,用于异步,提高效率.
    
  }
 
});

// 外部接口,外部使用时,格式如:import {xx, xx} from "xxx"
export {
    store // 在main.js中引用.
}