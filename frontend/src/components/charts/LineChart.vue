<template>
  <div ref="el" class="chart"></div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue"
import * as echarts from "echarts"

const props = defineProps({
  rounds: Array,
  scores: Array
})

const el = ref(null)
let chart

onMounted(() => {
  chart = echarts.init(el.value)

  chart.setOption({
    title: { text: "优化趋势（总分变化）" },
    xAxis: { type: "category", data: [] },
    yAxis: { max: 100 },
    series: [
      {
        type: "line",
        data: [],
        smooth: true
      }
    ]
  })
})

watch(
    () => [props.rounds, props.scores],
    ([rounds, scores]) => {
      chart.setOption({
        xAxis: { data: rounds },
        series: [{ data: scores }]
      })
    },
    { deep: true }
)
</script>

<style scoped>
.chart {
  height: 300px;
  margin-top: 20px;
  background: white;
  border-radius: 10px;
}
</style>