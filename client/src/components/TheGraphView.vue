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
const { graph_edges, graph_nodes, other_edges, myChart } = storeToRefs(graphStore)
const { loadedPage, totalPage,color_dist } = storeToRefs(pdfStore)
const { flowchartSvg, uni_ocr_result } = storeToRefs(flowChartStore)
let custom_nodes = []
let custom_links = []
const containerWidth = ref(0)
const containerHeight = ref(0)
const isGenerating = ref(false)
const nodePrepared = ref(false)
const edgePrepared = ref(false)
const defaultNodeColor = '#5c7bd9'
function changeOpacity(rgbaString, newOpacity) {
  if (!rgbaString) {
    return;
  }
  const match = rgbaString.match(/rgba?\((\d+),\s*(\d+),\s*(\d+),?\s*([\d.]*)\)/);
  if (match) {
    const r = parseInt(match[1], 10); // 红色值
    const g = parseInt(match[2], 10); // 绿色值
    const b = parseInt(match[3], 10); // 蓝色值
    return `rgba(${r}, ${g}, ${b}, ${newOpacity})`;
  }else{
    return rgbaString
  }
}
async function generateKnowledgeGraph() {
  isGenerating.value = true;
  await generateKnowledgeGraphApi();
  // await findEntitiesApi();
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
        // text: 'Knowledge Graph',
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
      graphic: {
        type: 'group',
        position: [0, 0],  // 保证图表的原点位置
        size: [5000, 5000],  // 设置适当的大小来确保缩放后不被限制
      },

      series: [
        {
          type: 'graph',
          layout: 'force',
          animation: true,
          label: {
            position: 'right',
            formatter: '{b}',
          },
          roam: true,  // 允许平移和缩放
          center: ['50%', '50%'],
          draggable: true,
          emphasis: {
            focus: 'adjacency',
          },
          data: custom_nodes,
          // categories: custom_categories,
          force: {
            edgeLength: 120,
            repulsion: 200,
            gravity: 0.1,
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

    myChart.value.on('click', function (params) {
      // 只有点击节点时才会触发
      if (params.dataType === 'node') {
        const nodeId = params.data.id;
        const nodeName = params.data.name;
        selectElement.value = nodeName
        console.log(`Node clicked: ${nodeName} (ID: ${nodeId})`);
      }
      else if (params.dataType === 'edge') {
        const evidence = params.data.evidence;
        console.log(evidence);
      }
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
        name: `${item['label'].toLowerCase()}`,
        symbolSize: 15,
        itemStyle: { color: defaultNodeColor },
        // category: Number.parseInt(item[3], 10),
        // x: randomX,
        // y: randomY,
        value: null,
        label: { show: true },
      })
    })
    nodePrepared.value = true
    if (edgePrepared.value) {
      createGraph()
    }
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
        evidence: `${item['evidence']}`,
        label: {
          show: true,
          formatter: `${item['label']}`, // Display the relationship as the edge label
          fontSize: 12,
          color: '#333',
        },
        lineStyle: {
          width: 5, // 设置边的粗细，可以根据需要调整
        },
      })
    })
    edgePrepared.value = true
    if (nodePrepared.value) {
      createGraph()
    }
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
          evidence: `${item['evidence']}`,
          label: {
            show: true,
            formatter: `${item['label']}`,
            fontSize: 12,
            color: '#333',
          },
        })

        custom_nodes.push({
          id: `${nodes_already_in.length + i}`,
          name: `${item['contextual word'].toLowerCase()}`,
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
    // createGraph()
  }
})
watch(selectElement, value => {//如果有人选择了
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
      color: changeOpacity(color_dist.value[selectElement.value.toLowerCase()], 0.7),
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
      <div class="absolute left-10px top-10px flex items-center">
        <div class="i-bxs:network-chart w-25px h-25px"></div>
        <div class="ml-5px font-size-4">Knowledge Graph</div>
      </div>

      <button v-if="!myChart" :disabled="isHighlighting || !uni_ocr_result"
        class="absolute top-1/2 left-1/2 transform translate--50%  flex justify-center items-center h-30px w-180px font-size-3 disabled:bg-gray-400 disabled:cursor-not-allowed mt-4 rounded-lg bg-blue-500 px-4 py-2 text-white shadow-md transition duration-300 hover:bg-blue-700"
        @click="generateKnowledgeGraph()">
        <div v-if="!isGenerating">generateKnowledgeGraph</div>
        <div v-if="isGenerating" class="i-line-md:loading-twotone-loop"></div>
      </button>
    </div>
  </div>
</template>
