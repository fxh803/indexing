// src/stores/counterStore.js
import { defineStore } from 'pinia'

export const usePdfStore = defineStore('pdf', {
  state: () => ({
    pdfName: null,
    pdfContent: null,
    pdfUrl: null,
    totalPage:0,
    loadedPage:0,
    keywordsSentence:[],
    keywords:[],
    ai_output:'',
    color_dist:{},
    scale:1,
    bestScale:1,
    fitParent:true,
  }),
  getters: {
  },
  actions: {
  },
})
