// src/stores/counterStore.js
import { defineStore } from 'pinia'

export const usePdfStore = defineStore('pdf', {
  state: () => ({
    pdfName: null,
    pdfContent: null,
    pdfUrl: null,
  }),
  getters: {
  },
  actions: {
  },
})
