<script setup>

</script>

<template>
  <div class="h-screen w-screen flex flex-col   bg-gray-100">
    <TheHeaderView class="h-50px w-full"></TheHeaderView>
    <div class="relative  flex h-[calc(100%-50px)] w-full">
      <TheLeftView class="h-full w-1/2" />
      <ThePdfView class="h-full w-1/2" />
    </div>
  </div>
</template>

<style lang="css">
/* 整个滚动条 */
::-webkit-scrollbar {
    width: 5px; /* 垂直滚动条宽度 */
    height: 12px; /* 水平滚动条高度 */
}

/* 滚动条轨道 */
::-webkit-scrollbar-track {
    background: #f1f1f1; /* 轨道背景色 */
    border-radius: 6px; /* 圆角 */
}

/* 滚动条滑块 */
::-webkit-scrollbar-thumb {
    background: #888; /* 滑块背景色 */
    border-radius: 6px; /* 圆角 */
}

/* 滚动条滑块悬停效果 */
::-webkit-scrollbar-thumb:hover {
    background: #555; /* 滑块悬停时的背景色 */
}


</style>
