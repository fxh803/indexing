// src/stores/counterStore.js
import { defineStore } from 'pinia'

export const useInteractionStore = defineStore('interaction', {
  state: () => ({
     selectElement:null,
     selectedSentence:[],
     isHighlighting:false,
     isHighlightSentence:false,
     isInitialized:false,
     switchColor:'green',
     highlightDetail:[]
  }),
  getters: {
  },
  actions: {
  },
})
