<script setup>
import { usePDF, VuePDF } from '@tato30/vue-pdf'
import * as pdfjsLib from 'pdfjs-dist'
// 用于渲染文本的样式和canvas上的字体一一对应
// import 'pdfjs-dist/web/pdf_viewer.css'
import '@tato30/vue-pdf/style.css'
import { storeToRefs } from 'pinia'
import { onMounted, ref, watch } from 'vue'
import { usePdfStore } from '~/stores/pdfStore'
import { useFlowChartStore } from '~/stores/flowChartStore'
import { useInteractionStore } from '~/stores/interaction'

const flowChartStore = useFlowChartStore()
const pdfStore = usePdfStore()
const interactionStore = useInteractionStore()
const { selectElement, selectedSentence, isHighlighting, isInitialized, isHighlightSentence, switchColor, highlightDetail } = storeToRefs(interactionStore)
const { ocr_result, uni_ocr_result } = storeToRefs(flowChartStore)
const { pdfUrl, pdfContent, loadedPage, totalPage, keywordsSentence, keywords, color_dist, scale, bestScale, fitParent } = storeToRefs(pdfStore)

const highlightText = ref([])
const highlightedPages = ref([])
const highlightOptions = ref({
  completeWords: true,// 仅匹配完整单词
  ignoreCase: true, // 忽略大小写
})
const { pdf, pages } = usePDF(pdfUrl.value)
const end_page = ref(-1)
const end_index = ref(-1)
const color_list = [
  'rgba(166, 206, 227, 0.5)',
  'rgba(31, 120, 180, 0.5)',
  'rgba(178, 223, 138, 0.5)',
  'rgba(51, 160, 44, 0.5)',
  'rgba(251, 154, 153, 0.5)',
  'rgba(227, 26, 28, 0.5)',
  'rgba(253, 191, 111, 0.5)',
  'rgba(255, 127, 0, 0.5)',
  'rgba(202, 178, 214, 0.5)',
  'rgba(106, 61, 154, 0.5)',
  'rgba(255, 255, 153, 0.5)',
  'rgba(177, 89, 40, 0.5)'
];
let resolvePromise;
const allPagesLoaded = new Promise((resolve) => {
  resolvePromise = resolve;
});
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
watch(isHighlightSentence, () => {

  isHighlighting.value = true
  highlightDetail.value = []
  highlightedPages.value = []
  switchColor.value = isHighlightSentence.value ? 'rgb(95,158,160)' : 'green';
  //重新渲染
  const temp = highlightText.value
  highlightText.value = []
  setTimeout(() => {
    highlightText.value = temp
  }, 500)
})
watch(selectElement, value => {
  selectedSentence.value = [];
  highlightedPages.value = [];
  highlightText.value = [selectElement.value]
  isHighlighting.value = true
  highlightDetail.value = []
})
watch(uni_ocr_result, async () => {
  if (uni_ocr_result.value) {
    if (loadedPage.value < totalPage.value) {
      console.log("等待")
      await allPagesLoaded;
      console.log("等待结束，开始")
    }
    highlightText.value = []
    keywords.value = []
    keywordsSentence.value = [];
    highlightedPages.value = [];
    highlightDetail.value = []
    isHighlighting.value = true;
    find_REFERENCES()
    uni_ocr_result.value.forEach((value, i) => {
      const word = value.toLowerCase();
      color_dist.value[word] = color_list[i % color_list.length];
      if (!highlightText.value.includes(word)) {
        highlightText.value.push(word);
        keywords.value.push(word)
      }
    });
  }
})
watch(highlightedPages, () => {//监听高亮是否完成
  if (highlightedPages.value.length >= totalPage.value) {
    isHighlighting.value = false;
    console.log('highlighting finished')
    if (!isInitialized.value) {
      setTimeout(() => {
        isInitialized.value = true;
      }, 2000);
    }
    if (selectElement.value) {
      scrollToElement()
    }
  }
}, { deep: true })
//找出高亮单词的对应句子
function findHighlightSentence(match, textBlocks) {
  const { start, end } = match;
  let startIdx = start.idx;
  let endIdx = end.idx;
  let startOffset = start.offset;
  let endOffset = end.offset;
  const endNote = ['.', '?', '!', '[', ']']
  let startBlock = textBlocks[startIdx];
  let endBlock = textBlocks[endIdx];

  if (startIdx === endIdx && endNote.some(symbol => startBlock.includes(symbol))) {//如果在同一块文字中，并且有句子结束符号，则需要处理
    const _idx = startBlock.split('').findIndex(char => endNote.includes(char));
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
  while (endIdx < textBlocks.length && !endNote.some(symbol => endBlock.includes(symbol))) {
    endIdx += 1;
    endBlock = textBlocks[endIdx];
  }
  // 向前查找句子开始边界
  while (startIdx >= 0 && !endNote.some(symbol => startBlock.includes(symbol))) {
    startIdx -= 1;
    startBlock = textBlocks[startIdx];
  }
  if (startIdx < 0 || endIdx >= textBlocks.length) { //不正常
    return [-1, -1, -1, -1, null];
  }
  startOffset = startBlock.split('').findLastIndex(char => endNote.includes(char)) + 1;
  endOffset = endBlock.split('').findIndex(char => endNote.includes(char)) + 1;

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
function highlightSentence(textDivs, s_startIdx, s_endIdx, s_startOffset, s_endOffset, word, newClass) {
  if (s_startIdx == -1 || s_endIdx == -1) {
    return;
  }
  const highlightColor = color_dist.value[word]
  if (s_startIdx == s_endIdx) {//如果在同一个文本块，只需扩展原有的span
    const div = textDivs[s_startIdx];
    const text = div.innerText.slice(s_startOffset, s_endOffset).trim();
    const span = div.querySelector('span');
    span.className = 'highlight appended sentence';
    span.classList.add(newClass);
    div.innerText = div.innerText.replace(text, '').trim();
    span.innerText = text;
    span.style.backgroundColor = highlightColor;

  } else {//多个块进行处理
    for (let i = s_startIdx; i <= s_endIdx; i++) {
      const div = textDivs[i];
      if (i == s_startIdx) {//头文本块

        const span = document.createElement('span');
        span.className = 'highlight appended sentence';
        span.classList.add(newClass);
        const text = div.innerText.slice(s_startOffset).trim();

        //特殊情况是有可能有已经处理好的进行合并
        const oldspan = div.querySelector('.sentence')
        if (oldspan && !oldspan.textContent.includes(text)) {
          console.log("已经有" + oldspan.textContent + "但后面要加上" + text)
          span.innerText = oldspan.textContent + text;
          div.textContent = '';
          oldspan.remove();
        } else if (oldspan && oldspan.textContent.includes(text)) {
          console.log("前部出现信息重叠", oldspan.textContent, text)
          if (oldspan.textContent == text) {
            span.innerText = oldspan.textContent;
            oldspan.remove();
          }
        }
        //否则就新建插入
        else {
          span.innerText = text;
          div.innerText = div.innerText.slice(0, s_startOffset).trim();
        }
        div.appendChild(span);
        span.style.backgroundColor = highlightColor;
      }
      else if (i == s_endIdx) {//尾文本块
        const span = document.createElement('span');
        span.className = 'highlight appended sentence';
        span.classList.add(newClass);
        const text = div.innerText.slice(0, s_endOffset).trim();
        //特殊情况是有可能有已经处理好的进行合并
        const oldspan = div.querySelector('.sentence')
        if (oldspan && !oldspan.textContent.includes(text)) {
          console.log("已经有" + oldspan.textContent + "但前面要加上" + text)
          span.innerText = text + oldspan.textContent;
          div.textContent = '';
          oldspan.remove();
        } else if (oldspan && oldspan.textContent.includes(text)) {
          console.log("后部出现信息重叠", text, oldspan.textContent)
          if (oldspan.textContent == text) {
            span.innerText = oldspan.textContent;
            oldspan.remove();
          }
        }
        //否则就新建插入
        else {
          div.innerText = div.innerText.slice(s_endOffset).trim();
          span.innerText = text;
        }
        div.prepend(span);
        span.style.backgroundColor = highlightColor;
      }
      else {//中间文本块
        const span = document.createElement('span');
        span.className = 'highlight appended sentence';
        span.classList.add(newClass);
        const text = div.innerText;
        div.innerText = '';
        span.innerText = text;
        div.appendChild(span);
        span.style.backgroundColor = highlightColor;
      }
    }
  }
}
function highlightWord(textDivs, startIdx, endIdx, startOffset, endOffset, word, newClass) {
  for (let i = startIdx; i <= endIdx; i++) {
    const div = textDivs[i];
    const spans = div.querySelectorAll('span');
    spans.forEach(span => {
      if (word.includes(span.textContent.toLowerCase().replace(/-/g, ''))) {
        span.className = 'highlight appended word';
        span.classList.add(newClass);
        span.style.backgroundColor = color_dist.value[word];
      }
    });
  }
}
function onHighlight(value) {
  if (highlightText.value.length == 0) {
    return;
  }

  //将已经高亮的页面记录下来,否则跳出
  if (!highlightedPages.value.includes(value.page)) {
    //   return;
    // } else {
    highlightedPages.value.push(value.page);
  }
  console.log(value)
  value.matches.forEach(match => {

    //判断是否是正文，通过REFERENCE检查
    if (match.start.idx > end_index.value && value.page >= end_page.value && end_index.value != -1) {
      return;
    }

    const matchWord = match.str.toLowerCase()
    const textBlocks = value.textContent.items.map(block => block.str); // 提取所有文本块的字符串内容
    const [s_startIdx, s_endIdx, s_startOffset, s_endOffset, sentence] = findHighlightSentence(match, textBlocks);
    if (sentence == null) { //句子找不到或无效
      return;
    }
    if (sentence.includes('Fig')) {//句子是图片引用句或图片内句子
      return;
    }
    if (/\s{4,}/.test(sentence)) {//句子是乱码啥的
      return;
    }

    if (isHighlightSentence.value) {//如果是要高亮句子
      const newClass = `sentence-${value.page}-${s_startIdx}`;
      if (!highlightDetail.value.some(item => item[0] === newClass)) {
        highlightDetail.value.push([newClass, sentence, color_dist.value[matchWord]]);
      }
      highlightSentence(value.textDivs, s_startIdx, s_endIdx, s_startOffset, s_endOffset, matchWord, newClass)
    } else {//如果是要高亮词语
      const newClass = `word-${value.page}-${match.start.idx}`;
      if (!highlightDetail.value.some(item => item[0] === newClass)) {
        highlightDetail.value.push([newClass, matchWord, color_dist.value[matchWord]]);
      }
      highlightWord(value.textDivs, match.start.idx, match.end.idx, match.start.offset, match.end.offset, matchWord, newClass)
    }

    if (!isInitialized.value) {//如果未初始化
      const existingItem = keywordsSentence.value.find(item => item[0] == matchWord);
      if (existingItem) {
        if (!existingItem[1].includes(sentence) && !/\s{3,}/.test(sentence)) {
          existingItem[1].push(sentence)
        }
      } else {
        keywordsSentence.value.push([matchWord, [sentence]]);
      }
    }

    if (selectElement.value) {//如果是用户点击选择
      //对selectedSentence进行操作
      console.log("selectedSentence", selectedSentence.value)
      if (!selectedSentence.value.includes(sentence)) {
        selectedSentence.value.push(sentence)
      }
    }
  });
}
function onPageLoaded() {
  loadedPage.value += 1;
  if (loadedPage.value === totalPage.value && totalPage.value > 0) {
    console.log("加载完成")
    resolvePromise(); // 触发全局 Promise 的 resolve

  }
}


// 页面加载时渲染 PDF
onMounted(() => {
  setTimeout(() => {
    readPDF()
  }, 1000);
})

function scrollToElement() {
  let element;
  if (isHighlightSentence.value) {
    element = document.querySelector('.sentence');
  }
  else {
    element = document.querySelector('.word');
  }
  if (element) {
    // 使用scrollIntoView方法，设置行为为平滑滚动
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
  } else {
    console.warn(`未找到元素`);
  }
}


</script>

<template>
  <div class="pdf-container">
    <div class="pdf-page-container" v-for="page in pages" :key="page">
      <VuePDF :id="'page' + page" class="pdf-page" :pdf="pdf" :fit-parent="fitParent" :page="page" :text-layer="true"
        v-model:scale="scale" :highlight-text="highlightText" :highlight-options="highlightOptions"
        @highlight="onHighlight" @loaded="onPageLoaded" />
    </div>
  </div>
</template>
<style lang="css" scoped>
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

::v-deep(.textLayer .highlight) {
  --highlight-bg-color: transparent;
}
</style>
