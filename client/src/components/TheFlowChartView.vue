<script setup>
import { storeToRefs } from 'pinia'
import { sendFlowChartApi, generateIntrodutionApi } from '~/services/server.ts' // 引入 sendFlowChartApi 方法
import { useFlowChartStore } from '~/stores/flowChartStore'
import { usePdfStore } from '~/stores/pdfStore'
import { useInteractionStore } from '~/stores/interaction'
import { useGraphStore } from '~/stores/graphStore'
const flowChartStore = useFlowChartStore()
const pdfStore = usePdfStore()
const interactionStore = useInteractionStore()
const graphStore = useGraphStore()
const { myChart } = storeToRefs(graphStore)
const { flowchartImg, ocr_result, img_width, img_height, uni_ocr_result } = storeToRefs(flowChartStore)
const { loadedPage, totalPage, ai_output } = storeToRefs(pdfStore)
const { selectElement } = storeToRefs(interactionStore)
const isDragging = ref(false)
const fileInput = ref(null)
const elementAreas = ref([])
watch(flowchartImg, async (value) => {
  if (value) {
    await sendFlowChartApi();
  }
});
watch(ocr_result, value => {
  if (ocr_result.value) {
    ocr_result.value.forEach(value => {
      const leftTop = value[0][0]
      const rightBottom = value[0][1]
      const original_width = img_width.value
      const original_height = img_height.value
      const flowchartImage = document.querySelector('.flowchartImage');
      const computedStyle = window.getComputedStyle(flowchartImage);
      const now_width = parseInt(computedStyle.width); // 实际宽度
      const now_height = parseInt(computedStyle.height); // 实际高度
      // 计算缩放比例
      const scaleX = now_width / original_width;
      const scaleY = now_height / original_height;
      // 重新计算坐标
      const newLeftTop = [leftTop[0] * scaleX, leftTop[1] * scaleY]
      const newRightBottom = [rightBottom[0] * scaleX, rightBottom[1] * scaleY]
      // console.log(leftTop, rightBottom, original_width, original_height, now_width, now_height, scaleX, scaleY,newLeftTop, newRightBottom)
      elementAreas.value.push({
        x: newLeftTop[0],
        y: newLeftTop[1],
        width: newRightBottom[0] - newLeftTop[0],
        height: newRightBottom[1] - newLeftTop[1],
        content: value[1],
        borderColor: 'gray'
      })

    });
  }

})

// 选择文件
function selectFile() {
  fileInput.value.click()
}

// 拖动悬浮效果
function handleOver() {
  isDragging.value = true
}

// 拖动离开效果
function handleLeave() {
  isDragging.value = false
}
function elementAreaClick(area) {
  selectElement.value = area.content
  elementAreas.value.forEach(area => {
    if (area.borderColor === 'rgba(144, 238, 144)') {
      area.borderColor = 'gray'
    }
  });
  area.borderColor = 'rgba(144, 238, 144)'
}
// 处理文件拖放
function handleDrop(event) {
  const file = event.dataTransfer.files[0] // 获取拖放的文件
  if (file && file.type.startsWith('image/')) {
    const reader = new FileReader()

    reader.onload = (e) => {
      flowchartImg.value = e.target.result // 设置图片的 URL
    }

    reader.readAsDataURL(file) // 将文件读取为 Data URL
  }
  else {
    alert('请选择有效的图片文件。')
  }
  isDragging.value = false
}

// 处理文件选择
function handleFileChange(event) {
  const file = event.target.files[0] // 获取用户选择的文件
  if (file && file.type.startsWith('image/')) {
    const reader = new FileReader()

    reader.onload = (e) => {
      flowchartImg.value = e.target.result // 设置图片的 URL
    }

    reader.readAsDataURL(file) // 将文件读取为 Data URL
  }
  else {
    alert('请选择有效的图片文件。')
  }
}

// 清除图片
function clearImage() {
  myChart.value.dispose()
  myChart.value = null
  flowchartImg.value = null // 清空图片
  elementAreas.value = []
  ocr_result.value = null
  uni_ocr_result.value = null
}
// 在组件卸载前清空图片
onBeforeUnmount(() => {
  clearImage()
})

</script>

<template>
  <div class="p-5">
    <div class="relative h-full w-full flex items-center  flex-col rounded-lg bg-white p-5 shadow-md"
      @drop.prevent="handleDrop" @dragover.prevent="handleOver" @dragleave="handleLeave">
      <div v-if="!flowchartImg"
        class="h-full w-full flex items-center justify-center border-2 border-gray-300 rounded-lg border-dashed">
        <button class="rounded-lg bg-gray-800 px-4 py-2 text-white shadow-md transition duration-300 hover:bg-gray-500"
          @click="selectFile">
          选择流程图
        </button>
        <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handleFileChange">
      </div>
      <!-- 显示上传的图片 -->
      <div v-if="flowchartImg" class="w-full h-3/4 justify-center items-center flex">
        <div class="relative w-auto h-auto">
          <img :src="flowchartImg" alt="Uploaded Image" class="flowchartImage object-contain">

          <div v-for="(area, index) in elementAreas" :key="index"
            class="absolute bg-white bg-opacity-50 cursor-pointer p-2" :style="{
              left: area.x + 'px',
              top: area.y + 'px',
              transform: 'translate(-2px,-2px)',
              border: '2px solid ' + area.borderColor,
              width: area.width + 'px',
              height: area.height + 'px'
            }" @click="elementAreaClick(area)">
          </div>


          <button class="absolute right--20px top--20px border-2 rounded-full bg-white p-2 text-black"
            @click="clearImage">
            <div i-bi-x-lg />
          </button>
        </div>
      </div>
      <div v-if="flowchartImg" class="w-full h-1/4 relative flex justify-center ">
        <div class="overflow-auto w-full h-full">{{ ai_output }}</div>
      </div>

      <div v-if="isDragging" class="pointer-events-none absolute left-0 top-0 h-full w-full bg-black opacity-50" />
    </div>
  </div>
</template>

<style scoped>
.flowchartImage {
  max-width: 100%;
  border-radius: 8px;
  border: 2px solid #ddd;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
</style>
