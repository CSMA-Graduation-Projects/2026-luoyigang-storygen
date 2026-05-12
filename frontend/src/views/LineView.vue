<template>
  <div class="page">
    <div class="header">
      <router-link to="/" class="back-btn">← 返回对话</router-link>
      <h2>优化趋势分析</h2>
    </div>

    <div v-if="LineData.length === 0" class="empty-state">
      <p>暂无数据，请先在对话中生成用户故事</p>
      <router-link to="/" class="start-btn">开始对话</router-link>
    </div>

    <div v-else class="chart-container">
      <div ref="el" class="chart"></div>

      <div class="stats">
        <div class="stat-item">
          <span class="label">子需求数:</span>
          <span class="value">{{ subRequirements.length }} 个</span>
        </div>
        <div class="stat-item">
          <span class="label">优化轮次:</span>
          <span class="value">{{ maxRound }} 轮</span>
        </div>
        <div class="stat-item">
          <span class="label">平均初始分:</span>
          <span class="value">{{ avgFirstScore }}/60</span>
        </div>
        <div class="stat-item">
          <span class="label">平均最终分:</span>
          <span class="value">{{ avgLastScore }}/60</span>
        </div>
      </div>

      <div class="data-table">
        <h3>详细数据</h3>
        <table>
          <thead>
          <tr>
            <th>子需求</th>
            <th v-for="round in maxRound" :key="round">第{{ round }}轮</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(subReq, index) in subRequirements" :key="index">
            <td class="sub-req-name">{{ subReq }}</td>
            <td v-for="round in maxRound" :key="round" class="score-cell">
                <span
                    v-if="getScoreBySubAndRound(index + 1, round) !== null"
                    :class="getScoreClass(getScoreBySubAndRound(index + 1, round))"
                >
                  {{ getScoreBySubAndRound(index + 1, round) }}
                </span>
              <span v-else class="no-data">-</span>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, watch, computed} from "vue"
import * as echarts from "echarts"
import {useChat} from "@/composables/useChat"

const {LineData, subRequirements} = useChat()

const el = ref(null)
let chart = null

const lineData = computed(() => LineData.value || [])

const maxRound = computed(() => {
  if (lineData.value.length === 0) return 0
  return Math.max(...lineData.value.map(item => item.round))
})

const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316']

const getColorByIndex = (index) => {
  return colors[index % colors.length]
}

const getScoreBySubAndRound = (subReqIndex, round) => {
  const item = lineData.value.find(d => d.subRequirement === subReqIndex && d.round === round)
  return item ? item.score : null
}

const getScoreClass = (score) => {
  if (score >= 50) return 'score-high'
  if (score >= 40) return 'score-medium'
  return 'score-low'
}

const avgFirstScore = computed(() => {
  if (subRequirements.value.length === 0) return 0
  let total = 0
  let count = 0
  subRequirements.value.forEach((_, index) => {
    const firstScore = getScoreBySubAndRound(index + 1, 1)
    if (firstScore !== null) {
      total += firstScore
      count++
    }
  })
  return count > 0 ? (total / count).toFixed(1) : 0
})

const avgLastScore = computed(() => {
  if (subRequirements.value.length === 0) return 0
  let total = 0
  let count = 0
  subRequirements.value.forEach((_, index) => {
    const lastScore = getScoreBySubAndRound(index + 1, maxRound.value)
    if (lastScore !== null) {
      total += lastScore
      count++
    }
  })
  return count > 0 ? (total / count).toFixed(1) : 0
})

onMounted(() => {
  if (!el.value) {
    console.error('图表容器未找到')
    return
  }

  chart = echarts.init(el.value)
  updateChart()

  window.addEventListener('resize', () => {
    chart?.resize()
  })
})

const updateChart = () => {
  console.log('更新折线图，当前数据:')
  console.log('lineData:', lineData.value)
  console.log('subRequirements:', subRequirements.value)

  if (!chart || !lineData.value || lineData.value.length === 0) {
    console.log('数据为空，跳过更新')
    return
  }

  const rounds = Array.from(new Set(lineData.value.map(item => item.round))).sort((a, b) => a - b)

  const series = subRequirements.value.map((subReq, index) => {
    const subReqIndex = index + 1
    const data = rounds.map(round => {
      const item = lineData.value.find(d => d.subRequirement === subReqIndex && d.round === round)
      return item ? item.score : null
    })

    return {
      name: subReq.length > 15 ? subReq.substring(0, 15) + '...' : subReq,
      type: 'line',
      data: data,
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        width: 2,
        color: getColorByIndex(index)
      },
      itemStyle: {
        color: getColorByIndex(index),
        borderWidth: 2,
        borderColor: '#fff'
      },
      emphasis: {
        focus: 'series',
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: getColorByIndex(index)
        }
      }
    }
  })

  const option = {
    title: {
      text: '子需求优化趋势',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#1f2937'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        let result = `第${params[0].name}轮<br/>`
        params.forEach(param => {
          if (param.value !== null && param.value !== undefined) {
            result += `${param.marker}${param.seriesName}: ${param.value}/60<br/>`
          }
        })
        return result
      }
    },
    legend: {
      data: subRequirements.value.map(subReq =>
          subReq.length > 15 ? subReq.substring(0, 15) + '...' : subReq
      ),
      top: 30,
      type: 'scroll',
      textStyle: {
        fontSize: 12
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '80px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: rounds.map(r => `第${r}轮`),
      boundaryGap: false,
      axisLabel: {
        rotate: 0,
        interval: 0,
        fontSize: 12
      },
      axisLine: {
        lineStyle: {
          color: '#e5e7eb'
        }
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 60,
      axisLabel: {
        formatter: '{value}'
      },
      splitLine: {
        lineStyle: {
          color: '#f3f4f6'
        }
      }
    },
    series: series
  }

  chart.setOption(option, true)
  console.log('折线图更新完成')
}

watch(
    [LineData, subRequirements],
    ([newLineData, newSubReqs]) => {
      console.log('数据变化触发更新')
      console.log('新 lineData:', newLineData)
      console.log('新 subRequirements:', newSubReqs)

      if (newLineData && newLineData.length > 0 && newSubReqs && newSubReqs.length > 0) {
        updateChart()
      }
    },
    {deep: true}
)
</script>

<style scoped>
.page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.back-btn {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  transition: 0.2s;
}

.back-btn:hover {
  background: #2563eb;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
  background: white;
  border-radius: 12px;
}

.empty-state p {
  font-size: 16px;
  margin-bottom: 20px;
}

.start-btn {
  display: inline-block;
  padding: 10px 24px;
  background: #3b82f6;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  transition: 0.2s;
}

.start-btn:hover {
  background: #2563eb;
}

.chart-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart {
  width: 100%;
  height: 500px;
  margin-bottom: 20px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
  margin-bottom: 30px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 6px;
}

.label {
  color: #6b7280;
  font-size: 14px;
}

.value {
  color: #1f2937;
  font-weight: 600;
  font-size: 16px;
}

.data-table {
  margin-top: 30px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  overflow-x: auto;
}

.data-table h3 {
  margin-bottom: 15px;
  color: #1f2937;
  font-size: 16px;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 6px;
  overflow: hidden;
}

thead {
  background: #3b82f6;
  color: white;
}

th {
  padding: 12px 8px;
  text-align: center;
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
}

td {
  padding: 10px 8px;
  text-align: center;
  border-bottom: 1px solid #e5e7eb;
  font-size: 13px;
}

tbody tr:hover {
  background: #f3f4f6;
}

.sub-req-name {
  text-align: left;
  font-weight: 500;
  color: #1f2937;
  max-width: 200px;
  word-wrap: break-word;
}

.score-cell {
  font-weight: 600;
}

.score-high {
  color: #10b981;
  font-weight: 700;
}

.score-medium {
  color: #f59e0b;
  font-weight: 600;
}

.score-low {
  color: #ef4444;
  font-weight: 700;
}

.no-data {
  color: #9ca3af;
}
</style>

