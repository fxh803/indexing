import axios from 'axios'
import { storeToRefs } from 'pinia'
import { useFlowChartStore } from '~/stores/flowChartStore'
import { useGraphStore } from '~/stores/graphStore'
import { usePdfStore } from '~/stores/pdfStore'
import { useInteractionStore } from '~/stores/interaction'
const pdfStore = usePdfStore()
const interactionStore = useInteractionStore()
const flowChartStore = useFlowChartStore() // 获取 store 实例
const graphStore = useGraphStore()
const { selectElement,selectedSentence } = storeToRefs(interactionStore)
const {graph_edges, graph_nodes,other_edges } = storeToRefs(graphStore)
const { flowchartSvg, ocr_result ,uni_ocr_result, rects,flowchartImg,canvas_height, canvas_width ,offsetHeight,offsetWidth,img_height,img_width } = storeToRefs(flowChartStore)
const { pdfContent, keywordsSentence,keywords,ai_output } = storeToRefs(pdfStore)
export async function sendFlowChartApi() {
  try {
    const response = await axios.post('http://localhost:4444/uploadFlowChartApi', {
      svg: flowchartSvg.value,
      canvas_width: canvas_width.value,
      canvas_height: canvas_height.value,
    })
    console.log(response.data)
    ocr_result.value = response.data.ocr_message
    uni_ocr_result.value = response.data.uni_ocr_message
    rects.value = response.data.rects
    flowchartImg.value = response.data.img
    offsetHeight.value = response.data.offsetHeight
    offsetWidth.value = response.data.offsetWidth
    img_width.value = response.data.img_width
    img_height.value = response.data.img_height
  }
  catch (error) {
    console.error('Error sending image:', error)
  }
}
export async function generateKnowledgeGraphApi() {
  try {
    const response = await axios.post('http://localhost:4444/generateKnowledgeGraphApi', {
      pdf_text: pdfContent.value,
      keywords: keywords.value,
    })
    graph_edges.value = response.data.edges
    graph_nodes.value = response.data.nodes
    console.log(response.data)
  }
  catch (error) {
    console.error('Error sending image:', error)
  }
}
export async function generateIntrodutionApi() {
  try {
    const response = await axios.post('http://localhost:4444/generateIntrodutionApi', {
      sentences: selectedSentence.value,
      keyword: selectElement.value,
    })
    ai_output.value = response.data.response
  }
  catch (error) {
    console.error('Error sending image:', error)
  }
}

export async function findEntitiesApi() {
  try {
    const response = await axios.post('http://localhost:4444/findEntitiesApi', {
      sentences: keywordsSentence.value,
      keywords: keywords.value,
    })
    console.log(response.data)
    other_edges.value = response.data.edges
  }
  catch (error) {
    console.error('Error sending image:', error)
  }
}

