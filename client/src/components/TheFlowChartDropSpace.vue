<script setup>
import { storeToRefs } from 'pinia'
import { useFlowChartStore } from '~/stores/flowChartStore'

const flowChartStore = useFlowChartStore()
const { flowchartSvg } = storeToRefs(flowChartStore)
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
  if (file && file.type.startsWith('image/svg+xml')) {
    fileOperation(file);
  }
  else {
    alert('请选择有效的图片文件。')
  }
  isDragging.value = false
}

// 处理文件选择
function handleFileChange(event) {
  const file = event.target.files[0] // 获取用户选择的文件
  if (file && file.type.startsWith('image/svg+xml')) {
    fileOperation(file);
  }
  else {
    alert('请选择有效的图片文件。')
  }
}

 function fileOperation(file) {
  const reader = new FileReader()
  reader.onload = (e) => {
    flowchartSvg.value = e.target.result // 设置图片的 URL
  }
  reader.readAsText(file) // 将文件读取为 Data URL
}
</script>
<template>
  <div v-if="!flowchartSvg" @drop.prevent="handleDrop" @dragover.prevent="handleOver" @dragleave="handleLeave"
    class="h-full w-full flex items-center justify-center border-2 border-gray-300 rounded-lg border-dashed">
    <button class="rounded-lg bg-gray-800 px-4 py-2 text-white shadow-md transition duration-300 hover:bg-gray-500"
      @click="selectFile">
      选择流程图
    </button>
    <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handleFileChange">
    <div v-if="isDragging" class="pointer-events-none absolute left-0 top-0 h-full w-full bg-black opacity-50" />
  </div>
</template>
