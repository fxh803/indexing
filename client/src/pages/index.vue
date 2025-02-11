<script setup>
import { storeToRefs } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePdfStore } from '~/stores/pdfStore'

const router = useRouter()
// 引入 store
const pdfStore = usePdfStore() // 获取 store 实例
const { pdfName, pdfUrl } = storeToRefs(pdfStore)
const fileInput = ref(null)
const ishovering = ref(false)
function selectFile() {
  fileInput.value.click()
}

function handleFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    pdfName.value = file.name
    const fileURL = URL.createObjectURL(file)
    pdfUrl.value = fileURL
    console.log('Selected file:', file)
    router.push('/home')
  }
}

function handleDrop(event) {
  const file = event.dataTransfer.files[0]
  if (file && file.type === 'application/pdf') {
    pdfName.value = file.name
    const fileURL = URL.createObjectURL(file)
    pdfUrl.value = fileURL
    console.log('Dropped file:', file)
    router.push('/home')
  }
  else {
    alert('请拖放一个 PDF 文件！')
  }
}
function handleOver() {
  ishovering.value = true
}
function handleLeave() {
  ishovering.value = false
}
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-100">
    <!-- 上传按钮 -->
    <div
      class="flex flex-col items-center border-2 border-gray-300 rounded-lg border-dashed bg-white p-50"
      @drop.prevent="handleDrop" @dragover.prevent="handleOver"
      @dragleave="handleLeave"
    >
      <button
        class="rounded-lg bg-gray-800 px-4 py-2 text-white shadow-md transition duration-300 hover:bg-gray-500"
        @click="selectFile"
      >
        选择一个PDF文件
      </button>
      <input ref="fileInput" type="file" accept="application/pdf" class="hidden" @change="handleFileChange">
      <p class="mt-4 text-gray-500">
        或者把PDF文件拖动到这里
      </p>
    </div>
  </div>
  <div v-if="ishovering" class="pointer-events-none absolute left-0 top-0 h-full w-full bg-black opacity-50" />
</template>

<style scoped>
body {
  margin: 0;
  font-family: Arial, sans-serif;
}
</style>
