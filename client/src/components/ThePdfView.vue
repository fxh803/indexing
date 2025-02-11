<script setup>
import { usePDF, VuePDF } from '@tato30/vue-pdf'
import * as pdfjsLib from 'pdfjs-dist'
import { storeToRefs } from 'pinia'
import { onMounted, ref, watch } from 'vue'
import { usePdfStore } from '~/stores/pdfStore'
// 用于渲染文本的样式和canvas上的字体一一对应
// import 'pdfjs-dist/web/pdf_viewer.css'
import '@tato30/vue-pdf/style.css'

const pdfStore = usePdfStore() // 获取 store 实例
const { pdfUrl, pdfContent } = storeToRefs(pdfStore)
const { pdf } = usePDF(pdfUrl)
const highlightText = ref('')
const highlightOptions = ref({
  completeWords: false,
  ignoreCase: true,
})

// 定义响应式变量
const currentPage = ref(1) // 当前页面
const totalPages = ref(0) // 总页面数
const scale = ref(1)
// 初始化 PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = '~/../node_modules/pdfjs-dist/build/pdf.worker.mjs'
// 渲染 PDF
async function readPDF() {
  try {
    const pdfData = await pdfjsLib.getDocument(pdfUrl.value).promise
    totalPages.value = pdfData.numPages

    // 遍历每一页并提取文本
    let allText = ''
    for (let pageNumber = 1; pageNumber <= totalPages.value; pageNumber++) {
      const page = await pdfData.getPage(pageNumber)
      const content = await page.getTextContent()
      const textItems = content.items
      const pageText = textItems.map(item => item.str).join(' ')
      allText += `${pageText}\n`
    }
    pdfContent.value = allText
  }
  catch (error) {
    console.error('Error loading PDF: ', error)
  }
}

function onHighlight(value) {
  console.log(value)
}
function zoomIn() {
  if (scale.value < 5) { // 添加条件判断
    scale.value += 0.1
  }
}
function zoomOut() {
  if (scale.value > 1) { // 添加条件判断
    scale.value -= 0.1
  }
}
// 下一页
function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

// 上一页
function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

// 页面加载时渲染 PDF
onMounted(() => {
  readPDF()
})
</script>

<template>
  <div class="relative p-5">
    <div class="relative h-full w-full flex flex-col overflow-hidden rounded-lg shadow-md">
      <div class="z-10 h-50px w-full flex justify-center bg-gray-800">
        <div class="flex justify-center p-2 text-white space-x-4">
          <button
            :disabled="currentPage === 1" :style="{ opacity: currentPage === 1 ? 0.5 : 1 }"
            class="rounded-full bg-white p-2 text-black" @click="prevPage"
          >
            <div i-bi:chevron-left />
          </button>
          <div>{{ currentPage }} - {{ totalPages }}</div>
          <button
            :disabled="currentPage === totalPages" :style="{ opacity: currentPage === totalPages ? 0.5 : 1 }"
            class="rounded-full bg-white p-2 text-black" @click="nextPage"
          >
            <div i-bi:chevron-right />
          </button>
        </div>
        <div class="absolute right-0 flex justify-center p-2 text-white space-x-4">
          <button class="rounded-full bg-white p-2 text-black" @click="zoomIn">
            <div i-bi-zoom-in />
          </button>
          <button class="rounded-full bg-white p-2 text-black" @click="zoomOut">
            <div i-bi-zoom-out />
          </button>
        </div>
      </div>

      <div class="relative h-full w-full flex justify-center overflow-auto bg-white">
        <VuePDF class="absolute" :pdf="pdf" :text-layer="true" :page="currentPage" :scale="scale" :highlight-text="highlightText" :highlight-options="highlightOptions" @highlight="onHighlight" />
      </div>
    </div>
  </div>
</template>
