// src/stores/counterStore.js
import { defineStore } from 'pinia'
import { off } from 'process'

export const useFlowChartStore = defineStore('flowChart', {
  state: () => ({
    flowchartSvg: null,
    ocr_result: null,
    uni_ocr_result:null,
    rects: null,
    flowchartImg:null,
    canvas_height:0,
    canvas_width:0,
    offsetWidth:0,
    offsetHeight:0,
    img_height:0,
    img_width:0,
  }),
  getters: {
  },
  actions: {
  },
})
