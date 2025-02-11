<script setup>
import { storeToRefs } from 'pinia'
// import { onBeforeUnmount, ref } from 'vue'
import { sendFlowChartApi, sendPdfTextApi } from '~/services/server.ts' // 引入 sendFlowChartApi 方法
import { useFlowChartStore } from '~/stores/flowChartStore'

const flowChartStore = useFlowChartStore() // 获取 store 实例
const { img } = storeToRefs(flowChartStore)
const isDragging = ref(false)
const fileInput = ref(null)

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

// 处理文件拖放
function handleDrop(event) {
  const file = event.dataTransfer.files[0] // 获取拖放的文件
  if (file && file.type.startsWith('image/')) {
    const reader = new FileReader()

    reader.onload = (e) => {
      img.value = e.target.result // 设置图片的 URL
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
      img.value = e.target.result // 设置图片的 URL
    }

    reader.readAsDataURL(file) // 将文件读取为 Data URL
  }
  else {
    alert('请选择有效的图片文件。')
  }
}

// 清除图片
function clearImage() {
  img.value = null // 清空图片
}
// 在组件卸载前清空图片
onBeforeUnmount(() => {
  clearImage()
})
// 添加一个方法来调用 sendFlowChartApi
async function sendImage() {
  console.log('sendImage called')
  if (img.value) {
    await sendFlowChartApi()
    await sendPdfTextApi()
  }
  else {
    alert('请先上传图片。')
  }
}
</script>

<template>
  <div class="p-5">
    <div class="relative h-full w-full flex items-center justify-center overflow-hidden rounded-lg bg-white p-5 shadow-md" @drop.prevent="handleDrop" @dragover.prevent="handleOver" @dragleave="handleLeave">
      <div v-if="!img" class="h-full w-full flex items-center justify-center border-2 border-gray-300 rounded-lg border-dashed">
        <button
          class="rounded-lg bg-gray-800 px-4 py-2 text-white shadow-md transition duration-300 hover:bg-gray-500"
          @click="selectFile"
        >
          选择流程图
        </button>
        <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handleFileChange">
      </div>
      <!-- 显示上传的图片 -->
      <div v-if="img" class="image-preview">
        <img :src="img" alt="Uploaded Image">

        <button class="absolute right--10px top--10px border-2 rounded-full bg-white p-2 text-black" @click="clearImage">
          <div i-bi-x-lg />
        </button>
        <!-- 添加一个按钮来发送图片 -->
        <button v-if="img" class="mt-4 rounded-lg bg-blue-500 px-4 py-2 text-white shadow-md transition duration-300 hover:bg-blue-700" @click="sendImage">
          发送图片
        </button>
      </div>
      <div v-if="isDragging" class="pointer-events-none absolute left-0 top-0 h-full w-full bg-black opacity-50" />
    </div>
  </div>
</template>

<style scoped>
.image-preview {
  margin-top: 20px;
  position: relative;
}

.image-preview img {
  max-width: 100%;
  border-radius: 8px;
  border: 2px solid #ddd;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
</style>
