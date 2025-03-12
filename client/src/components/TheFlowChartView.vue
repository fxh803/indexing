<script setup>
import { storeToRefs } from 'pinia'
import { generateIntrodutionApi, sendFlowChartApi } from '~/services/server.ts'
import { useFlowChartStore } from '~/stores/flowChartStore'
import { usePdfStore } from '~/stores/pdfStore'
import { useInteractionStore } from '~/stores/interaction'
import { useGraphStore } from '~/stores/graphStore'
import paper from 'paper'
const flowChartStore = useFlowChartStore()
const pdfStore = usePdfStore()
const interactionStore = useInteractionStore()
const graphStore = useGraphStore()
const { myChart } = storeToRefs(graphStore)
const { flowchartSvg, ocr_result, uni_ocr_result, flowchartImg, rects, canvas_width, canvas_height, offsetHeight, offsetWidth, img_width, img_height } = storeToRefs(flowChartStore)
const { loadedPage, totalPage, ai_output, color_dist } = storeToRefs(pdfStore)
const { selectElement } = storeToRefs(interactionStore)
const elementAreas = ref([])
const showedKeywords = ref([])
watch(flowchartSvg, async () => {
  if (flowchartSvg.value) {
    await new Promise(resolve => setTimeout(resolve, 500));
    // 初始化 Paper.js 画布
    const paperCanvas = document.getElementById('paperCanvas');
    paper.setup(paperCanvas);

    const canvasContainer = document.querySelector('.canvas-container');
    const computedStyle = window.getComputedStyle(canvasContainer);
    const container_width = parseInt(computedStyle.width);
    const container_height = parseInt(computedStyle.height);
    paper.view.viewSize = new paper.Size(container_width, container_height);
    canvas_width.value = container_width;
    canvas_height.value = container_height;
    await sendFlowChartApi()
    // 加载图像
    const image = new paper.Raster('data:image/png;base64,' + flowchartImg.value);  // 图片的路径可以是相对路径或 URL
    // 图片加载完毕后进行操作
    image.onLoad = () => {
      // 将图片居中显示
      image.position = paper.view.center;
      image.size = new paper.Size(img_width.value, img_height.value);
    };
  }
});
watch(color_dist, () => {
  if (Object.keys(color_dist.value).length === uni_ocr_result.value.length) {
    //先加rect的
    rects.value.forEach(rect => {
      const leftTop = rect[0]
      const rightBottom = rect[1]
      const text = rect[2]
      const final_leftTop = [leftTop[0] + offsetWidth.value, leftTop[1] + offsetHeight.value]
      const final_rightBottom = [rightBottom[0] + offsetWidth.value, rightBottom[1] + offsetHeight.value]
      if (text) {
        elementAreas.value.push({
          x: final_leftTop[0],
          y: final_leftTop[1],
          width: final_rightBottom[0] - final_leftTop[0],
          height: final_rightBottom[1] - final_leftTop[1],
          content: text,
          borderColor: 'rgba(150, 150, 150, 0.5)',
          shadowColor: changeOpacity(color_dist.value[text.toLowerCase()], 0.7),
        })
        showedKeywords.value.push(text)
      }
    })
    //再加rect没有的ocr结果
    ocr_result.value.forEach(value => {
      const padding = 3
      const rect = value[0]
      const leftTop = [rect[0][0] + offsetWidth.value, rect[0][1] + offsetHeight.value]
      const rightBottom = [rect[1][0] + offsetWidth.value, rect[1][1] + offsetHeight.value]
      const text = value[1]
      if (!showedKeywords.value.includes(text)) {
        elementAreas.value.push({
          x: leftTop[0] - padding,
          y: leftTop[1] - padding,
          width: rightBottom[0] - leftTop[0] + 2*padding,
          height: rightBottom[1] - leftTop[1] + 2*padding,
          content: value[1],
          borderColor: 'rgba(150, 150, 150, 0.5)',
          shadowColor: changeOpacity(color_dist.value[text.toLowerCase()], 0.7),
        })
      }


    });
  }
}, { deep: true })

watch(selectElement, value => {
  if (selectElement.value) {
    elementAreas.value.forEach(area => {
      if (area.content.toLowerCase() != selectElement.value) {
        area.shadowColor = 'rgba(0, 0, 0, 0)'
      }
      else {
        area.shadowColor = changeOpacity(color_dist.value[area.content.toLowerCase()], 0.7)
      }
    });
  }
})
function elementAreaClick(area) {
  if (area.content) {
    selectElement.value = area.content.toLowerCase()
  }

}


// 清除图片
function clearImage() {
  if (myChart.value) {
    myChart.value.dispose()
  }
  myChart.value = null
  flowchartSvg.value = null // 清空图片
  elementAreas.value = []
  ocr_result.value = null
  uni_ocr_result.value = null
}
// 在组件卸载前清空图片
onBeforeUnmount(() => {
  clearImage()
})
function changeOpacity(rgbaString, newOpacity) {
  if (!rgbaString) {
    return;
  }
  const match = rgbaString.match(/rgba?\((\d+),\s*(\d+),\s*(\d+),?\s*([\d.]*)\)/);
  if (match) {
    const r = parseInt(match[1], 10); // 红色值
    const g = parseInt(match[2], 10); // 绿色值
    const b = parseInt(match[3], 10); // 蓝色值
    return `rgba(${r}, ${g}, ${b}, ${newOpacity})`;
  }else{
    return rgbaString
  }
}
</script>

<template>
  <div class="p-5 pb-0">
    <div :class="{ 'p-5': !flowchartSvg }"
      class="overflow-hidden relative h-full w-full flex items-center  flex-col rounded-lg bg-white shadow-md">
      <TheFlowChartDropSpace />
      <!-- 显示上传的图片 -->
      <div v-if="flowchartSvg" class="w-full h-full flex flex-col ">
        <!-- 顶部栏 -->
        <div class="relative z-10  h-50px w-full flex justify-center items-center bg-#2a2a33 shadow-md">
          <div class="absolute left-10px flex items-center">
            <div class="i-fa6-solid:table color-white w-20px h-20px"></div>
            <div class="ml-5px font-size-4 color-white">FlowChart</div>
          </div>
          <button
            class="scale-80 transform translate--50% absolute right-0px top-50% border-2 rounded-full bg-white p-2 text-black  transition-transform transform hover:scale-90 active:scale-80"
            @click="clearImage">
            <div i-bi-x-lg />
          </button>
        </div>
        <!-- 下部空间 -->
        <div class="canvas-container relative w-full h-full flex justify-center items-center">

          <!-- <img :src="flowchartSvg" alt="Uploaded Image" class="flowchartImage object-contain"> -->
          <canvas ref="paperCanvas" id="paperCanvas"></canvas>
          <div v-for="(area, index) in elementAreas" :key="index"
            class="absolute bg-white bg-opacity-0 cursor-pointer rounded transition-transform transform hover:scale-105 active:scale-95"
            :style="{
              left: area.x + 'px',
              top: area.y + 'px',
              border: '3px solid ' + area.borderColor,
              width: area.width + 'px',
              height: area.height + 'px',
              boxShadow: '4px 4px 4px 1px ' + area.shadowColor, /* xoffset, yoffset, blur, spread, color */
            }" @click="elementAreaClick(area)"></div>

        </div>
      </div>
      <!-- <div v-if="flowchartSvg" class="w-full h-1/4 relative flex justify-center ">
        <div class="overflow-auto w-full h-full">{{ ai_output }}</div>
      </div> -->


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
