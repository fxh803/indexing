<script setup>

import { storeToRefs } from 'pinia'
import { onMounted, ref, watch } from 'vue'
import { usePdfStore } from '~/stores/pdfStore'
import { useInteractionStore } from '~/stores/interaction'

const pdfStore = usePdfStore()
const interactionStore = useInteractionStore()
const { isHighlighting,isHighlightSentence,isInitialized,switchColor } = storeToRefs(interactionStore)
const { loadedPage, totalPage,scale,bestScale,fitParent } = storeToRefs(pdfStore)

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
</script>

<template>
  <div class="relative p-5 pl-0">
    <div class="relative h-full w-full flex flex-col overflow-hidden rounded-lg shadow-md">
      <!-- header -->
      <div class="z-10 h-47px w-full flex justify-center items-center bg-#2a2a33 shadow-md">

        <div class="absolute left-10px flex items-center">
          <div class="i-bxs:file-pdf  color-white w-25px h-30px"></div>
          <div class="ml-5px font-size-4 color-white">PDF View</div>
        </div>

        <el-switch v-if="isInitialized" v-model="isHighlightSentence" class="absolute right-120px ml-2 switch-btn"
          inline-prompt active-text="sentence" inactive-text="word" :style="{ '--action-bg-color': switchColor }" />

        <div class="absolute right-0 flex justify-center p-2 text-white space-x-4">
          <button
            class="rounded-full bg-white p-2 text-black scale-90 transition-transform transform hover:scale-100 active:scale-90"
            @click="zoomIn">
            <div i-bi-zoom-in />
          </button>
          <button
            class="rounded-full bg-white p-2 text-black scale-90  transition-transform transform hover:scale-100 active:scale-90"
            @click="zoomOut">
            <div i-bi-zoom-out />
          </button>
        </div>
        <div v-if="loadedPage < totalPage"
          class="z-10 absolute top-100px left-1/2 bg-#fdf6ec p-2 rounded-3 color-#e8a94a transform -translate-x-1/2 -translate-y-1/2 flex justify-center items-center">
          <div class="i-line-md:loading-twotone-loop"></div>{{ loadedPage }} page loaded
        </div>
        <div v-if="isHighlighting"
          class="z-10 absolute top-100px left-1/2 bg-#fdf6ec p-2 rounded-3 color-#e8a94a transform -translate-x-1/2 -translate-y-1/2 flex justify-center items-center">
          <div class="i-line-md:loading-twotone-loop"></div>searching keyword...
        </div>
        <ThePdfDataView/>
      </div>
<ThePdf/>

    </div>
  </div>
</template>

<style scoped>


.switch-btn {
  --el-switch-on-color: #ffffff;
  --el-switch-off-color: #ffffff;
  --el-switch-border-color: #000000;

}

.switch-btn ::v-deep(.el-switch__core .el-switch__inner .is-text) {
  color: #000000;
}

.switch-btn ::v-deep(.el-switch__core .el-switch__action) {
  background-color: var(--action-bg-color, green);
}


</style>
