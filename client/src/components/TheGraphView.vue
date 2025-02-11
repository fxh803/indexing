<script setup>
import * as echarts from 'echarts'
import { storeToRefs } from 'pinia'
import { useGraphStore } from '~/stores/graphStore'

const graphStore = useGraphStore()
const { graph_data, node_list, centers } = storeToRefs(graphStore)
let myChart = null
const custom_nodes = []
const custom_links = []
const custom_categories = []
const containerWidth = ref(0)
const containerHeight = ref(0)
const renderEnabled = ref(false)
// function getRandomNumberInRange(min, max) {
//   return Math.random() * (max - min) + min
// }
function createGraph() {
  const chartDom = document.getElementById('echarts-container')
  if (chartDom) {
    myChart = echarts.init(chartDom)
    myChart.showLoading()
    // 直接使用 graph_data
    myChart.hideLoading()
    const option = {
      title: {
        text: 'Knowledge Graph',
        top: 'bottom',
        left: 'right',
      },
      tooltip: {},
      animationDuration: 1500,
      animationEasingUpdate: 'quinticInOut',

      series: [
        // {
        //   name: 'Knowledge Graph',
        //   type: 'graph',
        //   legendHoverLink: false,
        //   layout: 'force',
        //   data: custom_nodes,
        //   force: {
        //     edgeLength: 5,
        //     repulsion: 20,
        //     gravity: 0.2,
        //   },
        //   edges: custom_links,
        //   roam: true,
        //   label: {
        //     position: 'right',
        //     formatter: '{b}',
        //   },
        //   lineStyle: {
        //     color: 'source',
        //     curveness: 0.3,
        //   },
        //   emphasis: {
        //     focus: 'adjacency',
        //     lineStyle: {
        //       width: 10,
        //     },
        //   },
        // },
        {
          type: 'graph',
          layout: 'force',
          animation: true,
          label: {
            position: 'right',
            formatter: '{b}',
          },
          draggable: true,
          data: custom_nodes,
          categories: custom_categories,
          force: {
            edgeLength: 170,
            repulsion: 100,
            gravity: 0.2,
          },
          edges: custom_links,
        },
      ],
    }
    myChart.setOption(option)
  }
  else {
    console.error('ECharts container not found')
  }
}
watch(node_list, (list) => {
  if (list) {
    custom_nodes.value = []
    list.forEach((item) => {
      // const randomX = Math.floor(getRandomNumberInRange(-containerWidth.value / 2, containerWidth.value / 2))
      // const randomY = Math.floor(getRandomNumberInRange(-containerHeight.value / 2, containerHeight.value / 2))
      custom_nodes.push({
        id: `${item[0]}`,
        name: `${item[1]}`,
        symbolSize: item[2] * 2 + 15,
        category: Number.parseInt(item[3], 10),
        // x: randomX,
        // y: randomY,
        value: null,
        label: { show: true },
      })
    })
    if (!renderEnabled.value) {
      renderEnabled.value = true
    }
  }
})
watch(graph_data, (data) => {
  if (data) {
    custom_links.value = []
    data.forEach((item) => {
      custom_links.push({
        source: `${item[0]}`,
        target: `${item[1]}`,
      })
    })
    if (!renderEnabled.value) {
      renderEnabled.value = true
    }
  }
})
watch(centers, (centers) => {
  if (centers) {
    custom_categories.value = []
    centers.forEach((center) => {
      custom_categories.push({
        name: `${center[0]}`,
        keyword: {},
      })
    })
  }
})
watch(renderEnabled, (enabled) => {
  if (enabled) {
    createGraph()
  }
})
onMounted(() => {
  nextTick(() => {
    const chartDom = document.getElementById('echarts-container')
    if (chartDom) {
      const rect = chartDom.getBoundingClientRect()
      containerHeight.value = rect.height
      containerWidth.value = rect.width
    }
    else {
      console.error('ECharts container not found')
    }
  })
})
</script>

<template>
  <div class="p-5">
    <div class="relative h-full w-full flex items-center justify-center overflow-hidden rounded-lg bg-white shadow-md">
      <div id="echarts-container" class="h-full w-full" />
    </div>
  </div>
</template>
