<script setup>
import { useInteractionStore } from '~/stores/interaction'
import { storeToRefs } from 'pinia'
const interactionStore = useInteractionStore()
const { isHighlighting, isInitialized, isHighlightSentence, highlightDetail } = storeToRefs(interactionStore)
const isShowPanel = ref(false)
const lastScroll = ref('')
function showPanel() {
  isShowPanel.value = !isShowPanel.value
}
function scrollToElement(className) {

  const element = document.querySelector(className);
  if (element) {
    // 使用scrollIntoView方法，设置行为为平滑滚动
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
  } else {
    console.warn(`未找到元素`);
  }
  if(lastScroll.value){
    document.querySelectorAll(lastScroll.value).forEach((div) => {
      div.classList.remove('flowing-border');
    });
  }
  const elements = document.querySelectorAll(className);
  elements.forEach((div) => {
    div.classList.add('flowing-border');
  });
  lastScroll.value = className;
}

</script>
<template>
  <div v-if="highlightDetail.length > 0" class="absolute top-80px right-30px">
    <button
      class="rounded-full bg-white p-2 text-black scale-90  transition-transform transform hover:scale-100 active:scale-90 border-2"
      @click="showPanel">
      <div class="i-bi:justify-right"></div>
    </button>
    <div v-if="isShowPanel"
      class="panel p-5 absolute top-0px right-0px max-h-200px rounded-lg transform translate-x--50px bg-white overflow-y-scroll"
      :style="{ width: isHighlightSentence ? '400px' : '200px' }">
      <ul>
        <li v-for="(item, index) in highlightDetail" :key="index" class="list-item"
          @click="scrollToElement(`.${item[0]}`)">
          <!-- 小圆点 -->
          <span class="dot" :style="{ backgroundColor: item[2] }"></span>
          <!-- 内容 -->
          <span>{{ item[1] }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.panel{
  box-shadow: 0px 0px 4px 3px rgba(0,0,0,0.2); /* xoffset, yoffset, blur, spread, color */
}
.list-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  margin-top: 10px;
  cursor: pointer;
  position: relative;
}

.list-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 1px;
  /* 底边高度 */
  background: linear-gradient(to right,
      transparent 0%,
      #dddddd 20%,
      #dddddd 80%,
      transparent 100%);
}

.dot {
  min-width: 10px;
  min-height: 10px;
  border-radius: 50%;
  margin-right: 10px;
}

/* 整个滚动条 */
::-webkit-scrollbar {
  display: none;
}
</style>
<style>
/* 定义流动动画 */
/* @keyframes flowBorder {
  0% {
    border-bottom: 3px dashed rgb(49, 139, 255);
  }
  50% {
    border-bottom: 3px dashed rgb(255, 93, 93);
  }
  100% {
    border-bottom: 3px dashed rgb(49, 139, 255);
  }
} */
.flowing-border {
  border-bottom: 3px dashed rgb(80, 80, 80);
  animation: flowBorder 1s infinite;
}</style>
