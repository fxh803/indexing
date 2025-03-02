// src/stores/counterStore.js
import { defineStore } from 'pinia'

export const useInteractionStore = defineStore('interaction', {
  state: () => ({
     selectElement:null,
     selectedSentence:null,
     isHighlighting:false,
  }),
  getters: {
  },
  actions: {
  },
})
