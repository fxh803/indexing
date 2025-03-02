// src/stores/counterStore.js
import { defineStore } from 'pinia'

export const useFlowChartStore = defineStore('flowChart', {
  state: () => ({
    flowchartImg: null,
    ocr_result: null,
    img_width:null,
    img_height:null,
    uni_ocr_result:null
  }),
  getters: {
  },
  actions: {
  },
})
