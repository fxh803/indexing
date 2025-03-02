<script setup>
import { usePDF, VuePDF } from '@tato30/vue-pdf'
import * as pdfjsLib from 'pdfjs-dist'
import { storeToRefs } from 'pinia'
import { onMounted, ref, watch } from 'vue'
import { usePdfStore } from '~/stores/pdfStore'
import { useFlowChartStore } from '~/stores/flowChartStore'
import { useInteractionStore } from '~/stores/interaction'
// 用于渲染文本的样式和canvas上的字体一一对应
// import 'pdfjs-dist/web/pdf_viewer.css'
import '@tato30/vue-pdf/style.css'
const flowChartStore = useFlowChartStore()
const pdfStore = usePdfStore()
const interactionStore = useInteractionStore()
const { selectElement, selectedSentence,isHighlighting } = storeToRefs(interactionStore)
const { ocr_result, uni_ocr_result } = storeToRefs(flowChartStore)
const { pdfUrl, pdfContent, loadedPage, totalPage, keywordsSentence, keywords } = storeToRefs(pdfStore)
const { pdf, pages } = usePDF(pdfUrl)
const highlightText = ref([])
const fitParent = ref(true)
const isHighlightSentence = ref(true)
const end_page = ref(-1)
const end_index = ref(-1)
const color_dist = ref({})
const highlightedPages = ref([])
const highlightOptions = ref({
  completeWords: true,// 仅匹配完整单词
  ignoreCase: true, // 忽略大小写
})
const bestScale = ref(1)
// 定义响应式变量
const scale = ref(1)
// 初始化 PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = '~/../node_modules/pdfjs-dist/build/pdf.worker.mjs'
// 渲染 PDF
async function readPDF() {
  totalPage.value = pages.value;
  try {
    const pdfData = await pdfjsLib.getDocument(pdfUrl.value).promise
    // 遍历每一页并提取文本
    let allText = ''
    for (let pageNumber = 1; pageNumber <= pages.value; pageNumber++) {
      const page = await pdfData.getPage(pageNumber)
      const content = await page.getTextContent()
      const textItems = content.items
      let pageText = '';
      for (let i = 0; i < textItems.length; i++) {
        const currentText = textItems[i].str.replace(/\n/g, ''); // 去掉换行符
        // 如果上一个 item 的最后字符是连接符，则不加空格
        if (i > 0 && textItems[i - 1].str.endsWith('-')) {
          pageText += currentText; // 直接连接
        } else {
          pageText += ' ' + currentText; // 默认加空格
        }
      }
      allText += `${pageText} `
    }
    pdfContent.value = allText
  }
  catch (error) {
    console.error('Error loading PDF: ', error)
  }
}
function find_REFERENCES() {
  // 获取所有 textLayer 中的 <span> 元素
  const pages = document.querySelectorAll('.pdf-page');
  pages.forEach(page => {
    const textLayer = page.querySelector('.textLayer');
    const spans = textLayer.querySelectorAll('span[dir="ltr"]');
    // 遍历 <span> 元素，查找目标单词
    for (let i = 0; i < spans.length; i++) {
      if (spans[i].textContent.includes('REFERENCES')) {
        const page_num = page.id.match(/\d+/)[0];
        end_index.value = i;
        end_page.value = parseInt(page_num);
      }
    }
  });
}
watch(selectElement, value => {
  isHighlightSentence.value = true;
  selectedSentence.value = [];
  highlightedPages.value = [];
  highlightText.value = [selectElement.value]
  isHighlighting.value = true
})
watch(uni_ocr_result, () => {
  if (uni_ocr_result.value) {
    isHighlightSentence.value = false;
    highlightText.value = []
    keywords.value = []
    keywordsSentence.value = [];
    highlightedPages.value = [];
    isHighlighting.value = true;
    find_REFERENCES()
    uni_ocr_result.value.forEach((value, i) => {
      const word = value[1].toLowerCase();
      const randomR = Math.floor(Math.random() * 256);
      const randomG = Math.floor(Math.random() * 256);
      const randomB = Math.floor(Math.random() * 256);
      color_dist.value[word] = `rgba(${randomR}, ${randomG}, ${randomB}, 0.5)`;
      if (!highlightText.value.includes(word)) {
        highlightText.value.push(word);
        keywords.value.push(word)
      }
    });
  }
})
watch(highlightedPages, () => {
  console.log(highlightedPages.value,totalPage.value)
  if (highlightedPages.value.length >= totalPage.value) {
    isHighlighting.value = false;
    console.log('highlighting finished')
  }
},{deep:true})
//找出高亮单词的对应句子
function findHighlightSentence(match, textBlocks) {
  const { start, end } = match;
  let startIdx = start.idx;
  let endIdx = end.idx;
  let startOffset = start.offset;
  let endOffset = end.offset;

  let startBlock = textBlocks[startIdx];
  let endBlock = textBlocks[endIdx];

  if (startIdx === endIdx && ['.', '?', '!'].some(symbol => startBlock.includes(symbol))) {//如果在同一块文字中，并且有句子结束符号，则需要处理
    const _idx = startBlock.split('').findIndex(char => ['.', '?', '!'].includes(char));
    if (_idx < startOffset) {
      // 向后查找句子结束边界
      endIdx += 1;
      endBlock = textBlocks[endIdx];
    }
    else if (_idx >= endOffset) {
      // 向前查找句子开始边界
      startIdx -= 1;
      startBlock = textBlocks[startIdx];
    }
  }

  // 向后查找句子结束边界
  while (endIdx < textBlocks.length && !['.', '?', '!'].some(symbol => endBlock.includes(symbol))) {
    endIdx += 1;
    endBlock = textBlocks[endIdx];
  }
  // 向前查找句子开始边界
  while (startIdx >= 0 && !['.', '?', '!'].some(symbol => startBlock.includes(symbol))) {
    startIdx -= 1;
    startBlock = textBlocks[startIdx];
  }
  if (startIdx < 0 || endIdx >= textBlocks.length) { //不正常
    return [-1, -1, -1, -1, null];
  }
  startOffset = startBlock.split('').findLastIndex(char => ['.', '?', '!'].includes(char)) + 1;
  endOffset = endBlock.split('').findIndex(char => ['.', '?', '!'].includes(char)) + 1;

  // 拼接完整句子
  let sentence = '';
  if (startIdx === endIdx) {
    // 匹配词在同一文本块中
    sentence = startBlock.slice(startOffset, endOffset).trim();
  } else {
    // 匹配词跨越多块文本
    sentence += startBlock.slice(startOffset).trim(); // 第一块文本的剩余部分
    for (let i = startIdx + 1; i < endIdx; i++) {
      sentence += ' ' + textBlocks[i].trim(); // 中间文本块
    }
    sentence += ' ' + endBlock.slice(0, endOffset).trim(); // 最后一块文本的前半部分
  }
  return [startIdx, endIdx, startOffset, endOffset, sentence]
}
//高亮句子
function highlightSentence(textDivs, s_startIdx, s_endIdx, s_startOffset, s_endOffset,highlightColor) {
  if (s_startIdx == -1 || s_endIdx == -1) {
    return;
  }
  const defaultColors = 'rgba(144, 238, 144, 0.5)'
  if (s_startIdx == s_endIdx) {//如果在同一个文本块，只需扩展原有的span
    const div = textDivs[s_startIdx];
    const text = div.innerText.slice(s_startOffset, s_endOffset).trim();
    const span = div.querySelector('span');
    div.innerText = div.innerText.replace(text, '').trim();
    span.innerText = text;
    span.style.backgroundColor = highlightColor? highlightColor:defaultColors;
  } else {//多个块进行处理
    for (let i = s_startIdx; i <= s_endIdx; i++) {
      const div = textDivs[i];
      if (i == s_startIdx) {//头文本块

        const span = document.createElement('span');
        span.className = 'highlight append sentence';
        const text = div.innerText.slice(s_startOffset).trim();
        //特殊情况是有可能有已经处理好的进行合并
        const oldspan = div.querySelector('.sentence')
        if (oldspan && oldspan.textContent != text) {
          span.innerText = oldspan.textContent + text;
          div.textContent = '';
          oldspan.remove();
        }
        //否则就新建插入
        else {
          span.innerText = text;
          div.innerText = div.innerText.slice(0, s_startOffset).trim();
        }
        div.appendChild(span);
        span.style.backgroundColor = highlightColor? highlightColor:defaultColors;
      }
      else if (i == s_endIdx) {//尾文本块
        const span = document.createElement('span');
        span.className = 'highlight append sentence';
        const text = div.innerText.slice(0, s_endOffset).trim();
        div.innerText = div.innerText.slice(s_endOffset).trim();
        span.innerText = text;
        div.prepend(span);
        span.style.backgroundColor = highlightColor? highlightColor:defaultColors;
      }
      else {//中间文本块
        const span = document.createElement('span');
        span.className = 'highlight append sentence';
        const text = div.innerText;
        div.innerText = '';
        span.innerText = text;
        div.appendChild(span);
        span.style.backgroundColor = highlightColor? highlightColor:defaultColors;
      }
    }
  }
}
function highlightWord(textDivs, startIdx, endIdx, startOffset, endOffset, word,highlightColor) {
  for (let i = startIdx; i <= endIdx; i++) {
    const div = textDivs[i];
    const span = div.querySelector('span');
    span.style.backgroundColor = highlightColor? highlightColor:color_dist.value[word];
  }
}
function onHighlight(value) {
  if (highlightText.value.length == 0) {
    return;
  }
  //将已经高亮的页面记录下来
  if (!highlightedPages.value.includes(value.page)) {
    highlightedPages.value.push(value.page);
    console.log("push",value.page)
  }
  //判断是否是正文，通过REFERENCE检查
  let highlightColor = null;
  value.matches.forEach(match => {
    if (match.start.idx > end_index.value && value.page >= end_page.value && end_index.value != -1) {
      highlightColor = 'rgba(255, 255, 255, 0)';//不高亮
    }
    const matchWord = match.str.toLowerCase()
    const textBlocks = value.textContent.items.map(block => block.str); // 提取所有文本块的字符串内容
    const [s_startIdx, s_endIdx, s_startOffset, s_endOffset, sentence] = findHighlightSentence(match, textBlocks);
    if (sentence == null) {
      console.log('句子找不到或无效')
      return;
    }
    if (isHighlightSentence.value) {//如果是要高亮句子
      if (!selectedSentence.value.includes(sentence) && !/\s{3,}/.test(sentence)) {
        selectedSentence.value.push(sentence)
      }
      highlightSentence(value.textDivs, s_startIdx, s_endIdx, s_startOffset, s_endOffset,highlightColor)
    }
    else {//如果是要高亮单词
      const existingItem = keywordsSentence.value.find(item => item[0] == matchWord);
      if (existingItem) {
        if (!existingItem[1].includes(sentence) && !/\s{3,}/.test(sentence)) {
          existingItem[1].push(sentence)
        }
      } else {
        keywordsSentence.value.push([matchWord, [sentence]]);
      }
      highlightWord(value.textDivs, match.start.idx, match.end.idx, match.start.offset, match.end.offset, matchWord,highlightColor)
    }
  });
}
function onPageLoaded() {
  loadedPage.value += 1;
}

function startScale() {
  if (fitParent.value) {
    fitParent.value = false;//解锁
    const page = document.querySelector('.pdf-page'); // 根据类名查找
    const scaleFactor = window.getComputedStyle(page).getPropertyValue('--scale-factor');
    bestScale.value = parseFloat(scaleFactor);
    scale.value = bestScale.value;
  }
}
function zoomIn() {
  startScale()
  if (scale.value < 5) { // 添加条件判断
    scale.value += 0.1
  }
}
function zoomOut() {
  startScale()
  if (scale.value > bestScale.value) { // 添加条件判断
    scale.value -= 0.1
  }
}
// 页面加载时渲染 PDF
onMounted(() => {
  setTimeout(() => {
    readPDF()
  }, 1000);
})
</script>

<template>
  <div class="relative p-5">
    <div class="relative h-full w-full flex flex-col overflow-hidden rounded-lg shadow-md">
      <div class="z-10 h-50px w-full flex justify-center items-center bg-gray-800">
        <div class="absolute right-0 flex justify-center p-2 text-white space-x-4">
          <button class="rounded-full bg-white p-2 text-black scale-90" @click="zoomIn">
            <div i-bi-zoom-in />
          </button>
          <button class="rounded-full bg-white p-2 text-black scale-90" @click="zoomOut">
            <div i-bi-zoom-out />
          </button>
        </div>
        <div v-if="loadedPage < pages"
          class="z-10 absolute top-100px left-1/2 bg-#fdf6ec p-2 rounded-3 color-#e8a94a transform -translate-x-1/2 -translate-y-1/2 flex justify-center items-center">
          <div class="i-line-md:loading-twotone-loop"></div>{{ loadedPage }} page loaded
        </div>
        <div v-if="isHighlighting"
          class="z-10 absolute top-100px left-1/2 bg-#fdf6ec p-2 rounded-3 color-#e8a94a transform -translate-x-1/2 -translate-y-1/2 flex justify-center items-center">
          <div class="i-line-md:loading-twotone-loop"></div>searching keyword...
        </div>
      </div>

      <div class="pdf-container">
        <div class="pdf-page-container" v-for="page in pages" :key="page">
          <VuePDF :id="'page' + page" class="pdf-page" :pdf="pdf" :fit-parent="fitParent" :page="page"
            :text-layer="true" v-model:scale="scale" :highlight-text="highlightText"
            :highlight-options="highlightOptions" @highlight="onHighlight" @loaded="onPageLoaded" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pdf-container {
  position: relative;
  height: 100%;
  width: 100%;
  display: flex;
  /* align-items: center; */
  overflow: auto;
  flex-direction: column;
}

.pdf-page-container {
  margin-bottom: 20px;
}

.pdf-page {
  width: 100%;
}
</style>
