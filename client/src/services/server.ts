import axios from 'axios'
import { storeToRefs } from 'pinia'
import { useFlowChartStore } from '~/stores/flowChartStore'
import { useGraphStore } from '~/stores/graphStore'
import { usePdfStore } from '~/stores/pdfStore'

const pdfStore = usePdfStore()
const flowChartStore = useFlowChartStore() // 获取 store 实例
const graphStore = useGraphStore()
const { graph_data, node_list, centers } = storeToRefs(graphStore)
const { img, ocr_result } = storeToRefs(flowChartStore)
const { pdfContent } = storeToRefs(pdfStore)
// 添加一个方法来发送 imgbase64 到 localhost:4444
export async function sendFlowChartApi() {
  try {
    const response = await axios.post('http://localhost:4444/uploadFlowChartApi', {
      image_base64: img.value,
    })
    console.log(response.data.ocr_message)
    ocr_result.value = response.data.ocr_message
  }
  catch (error) {
    console.error('Error sending image:', error)
  }
}
export async function sendPdfTextApi() {
  try {
    const response = await axios.post('http://localhost:4444/uploadPdfTextApi', {
      pdf_text: pdfContent.value,
      ocr_result: ocr_result.value,
    })
    console.log(response.data)
    graph_data.value = response.data.graph_data
    node_list.value = response.data.node_list
    centers.value = response.data.centers
  }
  catch (error) {
    console.error('Error sending image:', error)
  }
}
