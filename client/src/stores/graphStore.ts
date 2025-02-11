// src/stores/counterStore.js
import { defineStore } from 'pinia'

export const useGraphStore = defineStore('graphStore', {
  state: () => ({
    graph_data: null,
    node_list: null,
    centers: null,
  }),
  getters: {
  },
  actions: {
  },
})
