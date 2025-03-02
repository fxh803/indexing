<script setup>
import * as echarts from 'echarts'
import { storeToRefs } from 'pinia'
import { useGraphStore } from '~/stores/graphStore'
import { useInteractionStore } from '~/stores/interaction'
import { usePdfStore } from '~/stores/pdfStore'
import { generateKnowledgeGraphApi, findEntitiesApi } from '~/services/server.ts'
import { useFlowChartStore } from '~/stores/flowChartStore'
const flowChartStore = useFlowChartStore()
const interactionStore = useInteractionStore()
const pdfStore = usePdfStore()
const graphStore = useGraphStore()
const { selectElement, isHighlighting } = storeToRefs(interactionStore)
const { graph_edges, graph_nodes, other_edges,myChart } = storeToRefs(graphStore)
const { loadedPage, totalPage } = storeToRefs(pdfStore)
const { flowchartImg,uni_ocr_result } = storeToRefs(flowChartStore)
let custom_nodes = []
let custom_links = []
const containerWidth = ref(0)
const containerHeight = ref(0)
// 保存节点默认颜色
const defaultColors = ref({});
const isGenerating = ref(false)
const defaultNodeColor = '#5c7bd9'

async function generateKnowledgeGraph() {
  isGenerating.value = true;
  await generateKnowledgeGraphApi();
  await findEntitiesApi();
  isGenerating.value = false;
}

function createGraph() {
  const chartDom = document.getElementById('echarts-container')
  if (chartDom) {
    myChart.value = echarts.init(chartDom)
    myChart.value.showLoading()
    // 直接使用 graph_data

    const option = {
      title: {
        text: 'Knowledge Graph',
        top: 'bottom',
        left: 'right',
      },
      tooltip: {
        trigger: 'item', // 触发方式为 'item'，表示悬浮在单个元素上时显示
        formatter: function (params) {
          // // params 包含了当前悬浮元素的信息
          if (params.dataType === 'edge') { // 判断是否是边
            const sourceNode = custom_nodes.find(node => node.id === params.data.source);
            const targetNode = custom_nodes.find(node => node.id === params.data.target);
            const relationship = params.data.value;
            return `relationship：${sourceNode.name} ${relationship} ${targetNode.name}`;
          }
          else if (params.dataType === 'node') { // 判断是否是节点
            return `${params.data.name}`;
          }
          else {
            return '';
          }

        },
      },
      animationDuration: 1500,
      animationEasingUpdate: 'quinticInOut',

      series: [
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
          // categories: custom_categories,
          force: {
            edgeLength: 120,
            repulsion: 200,
            gravity: 0.1,
            boundingBox: 'all', // 限制节点在图表区域内
          },
          edges: custom_links,
          lineStyle: {
            color: 'source', // Use the source node's color for the edge
            curveness: 0.2, // Add a slight curve to the edges
          },
          edgeSymbol: ['none', 'arrow'], // Add an arrow to the end of the edge
          edgeSymbolSize: 10, // Size of the arrow
        },
      ],
    }
    myChart.value.setOption(option)
    myChart.value.hideLoading()
    option.series[0].data.forEach(node => {
      defaultColors.value[node.name] = node.itemStyle.color;
    });
  }
  else {
    console.error('ECharts container not found')
  }
}
watch(graph_nodes, (node) => {
  if (node) {
    custom_nodes = []
    node.forEach((item) => {
      custom_nodes.push({
        id: `${item['id']}`,
        name: `${item['label']}`,
        symbolSize: 15,
        itemStyle: { color: defaultNodeColor },
        // category: Number.parseInt(item[3], 10),
        // x: randomX,
        // y: randomY,
        value: null,
        label: { show: true },
      })
    })
  }
})
watch(graph_edges, (edge) => {
  if (edge) {
    custom_links = []
    edge.forEach((item) => {
      custom_links.push({
        source: `${item['source_id']}`,
        target: `${item['target_id']}`,
        value: `${item['label']}`,
        label: {
          show: true,
          formatter: `${item['label']}`, // Display the relationship as the edge label
          fontSize: 12,
          color: '#333',
        },
      })
    })
  }
})
watch(other_edges, (edge) => {
  if (edge) {
    const nodes_already_in = graph_nodes.value
    edge.forEach((item, i) => {
      const keyword = item['keyword']
      const source_node = nodes_already_in.find(node => node['label'].toLowerCase() == keyword.toLowerCase())
      if (source_node) {
        const source_id = source_node['id'];
        custom_links.push({
          source: source_id,
          target: `${nodes_already_in.length + i}`,
          value: `${item['label']}`,
          label: {
            show: true,
            formatter: `${item['label']}`,
            fontSize: 12,
            color: '#333',
          },
        })

        custom_nodes.push({
          id: `${nodes_already_in.length + i}`,
          name: `${item['contextual word']}`,
          symbolSize: 8,
          itemStyle: { color: defaultNodeColor },
          // category: Number.parseInt(item[3], 10),
          // x: randomX,
          // y: randomY,
          value: null,
          label: { show: true },
        })
      } else {
        console.log('Source node not found for keyword:', keyword);
      }

    })
    createGraph()
  }
})

watch(selectElement, value => {
  // 获取当前图数据
  if (!myChart.value) {
    return;
  }
  const currentOption = myChart.value.getOption();
  const graphSeries = currentOption.series[0];

  // 恢复之前高亮节点的默认颜色
  const prevNodeIndex = graphSeries.data.findIndex(node => node.itemStyle.color != defaultNodeColor);
  if (prevNodeIndex !== -1) {
    graphSeries.data[prevNodeIndex].itemStyle = {
      color: defaultNodeColor
    };
  }

  // 查找节点
  const nodeIndex = graphSeries.data.findIndex(node => node.name === selectElement.value);
  if (nodeIndex !== -1) {
    // 更新节点样式
    graphSeries.data[nodeIndex].itemStyle = {
      color: 'rgba(144, 238, 144)'
    };
  }
  // 重新渲染图
  myChart.value.setOption(currentOption);
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
      <button v-if="!myChart&&flowchartImg" :disabled="isHighlighting||!uni_ocr_result"
        class="absolute top-1/2 left-1/2 transform translate--50%  flex justify-center items-center h-30px w-180px font-size-3 disabled:bg-gray-400 disabled:cursor-not-allowed mt-4 rounded-lg bg-blue-500 px-4 py-2 text-white shadow-md transition duration-300 hover:bg-blue-700"
        @click="generateKnowledgeGraph()">
        <div v-if="!isGenerating">generateKnowledgeGraph</div>
        <div v-if="isGenerating" class="i-line-md:loading-twotone-loop"></div>
      </button>
    </div>
  </div>
</template>
