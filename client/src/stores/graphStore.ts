// src/stores/counterStore.js
import { defineStore } from 'pinia'

export const useGraphStore = defineStore('graphStore', {
  state: () => ({
    graph_nodes:null,
    graph_edges:null,
    other_edges:null,
    myChart:null,
  }),
  getters: {
  },
  actions: {
  },
})
