import { onMounted, onUnmounted } from "vue"
import * as echarts from "echarts"

export function useEcharts(elRef, option) {

    let chart = null

    const init = () => {
        if (!elRef.value) return
        chart = echarts.init(elRef.value)
        chart.setOption(option)
    }

    const resize = () => {
        chart?.resize()
    }

    onMounted(() => {
        init()
        window.addEventListener("resize", resize)
    })

    onUnmounted(() => {
        window.removeEventListener("resize", resize)
        chart?.dispose()
    })

    return {
        getChart: () => chart
    }
}