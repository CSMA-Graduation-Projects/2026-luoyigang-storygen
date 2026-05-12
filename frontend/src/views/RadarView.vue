<template>
  <div class="page">
    <div class="header">
      <router-link to="/" class="back-btn">← 返回对话</router-link>
      <h2>INVEST雷达图分析</h2>
    </div>

    <div v-if="groupedRadarData.size === 0" class="empty-state">
      <p>暂无数据，请先在对话中生成用户故事</p>
      <router-link to="/" class="start-btn">开始对话</router-link>
    </div>

    <div v-else class="content">
      <div class="summary-stats">
        <div class="stat-card">
          <span class="stat-label">子需求数</span>
          <span class="stat-value">{{ groupedRadarData.size }} 个</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">总优化轮次</span>
          <span class="stat-value">{{ maxRound }} 轮</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">平均提升</span>
          <span class="stat-value">{{ avgImprovement }}</span>
        </div>
      </div>

      <div class="radar-grid">
        <div v-for="[subReqIndex, data] in groupedRadarData" :key="subReqIndex" class="radar-card">
          <div class="radar-header">
            <h3>{{ getSubReqName(subReqIndex) }}</h3>
            <span class="round-badge">{{ data.length }} 轮优化</span>
          </div>
          <div :ref="el => setRadarRef(el, subReqIndex)" class="radar-chart"></div>
          <div class="radar-stats">
            <div class="mini-stat">
              <span class="mini-label">初始分:</span>
              <span class="mini-value">{{ calculateFirstScore(data) }}/60</span>
            </div>
            <div class="mini-stat">
              <span class="mini-label">最终分:</span>
              <span class="mini-value">{{ calculateLastScore(data) }}/60</span>
            </div>
            <div class="mini-stat">
              <span class="mini-label">提升:</span>
              <span class="mini-value">{{ calculateImprovement(data) }}</span>
            </div>
          </div>
        </div>
      </div>


      <div class="data-table-section">
        <h3>INVEST详细数据</h3>
        <div class="table-container">
          <table>
            <thead>
            <tr>
              <th>子需求</th>
              <th>轮次</th>
              <th>I - 独立性</th>
              <th>N - 可协商性</th>
              <th>V - 有价值性</th>
              <th>E - 可估算性</th>
              <th>S - 小尺寸</th>
              <th>T - 可测试性</th>
              <th>总分</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(item, index) in sortedRadarData" :key="index">
              <td class="sub-req-cell">{{ getSubReqName(item.subRequirement) }}</td>
              <td class="round-cell">第{{ item.round }}轮</td>
              <td :class="getScoreClass(item.I)">{{ item.I }}</td>
              <td :class="getScoreClass(item.N)">{{ item.N }}</td>
              <td :class="getScoreClass(item.V)">{{ item.V }}</td>
              <td :class="getScoreClass(item.E)">{{ item.E }}</td>
              <td :class="getScoreClass(item.S)">{{ item.S }}</td>
              <td :class="getScoreClass(item.T)">{{ item.T }}</td>
              <td class="total-score">{{ calculateTotal(item) }}/60</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useChat } from "@/composables/useChat"
import { onMounted, watch, ref, computed } from "vue"
import * as echarts from "echarts"

const { radarData, subRequirements } = useChat()


const radarRefs = ref({})
const radarCharts = ref({})

const currentRadarData = computed(() => radarData.value)
const currentSubRequirements = computed(() => subRequirements.value)

const groupedRadarData = computed(() => {
  const grouped = new Map()
  currentRadarData.value.forEach(item => {
    if (!grouped.has(item.subRequirement)) {
      grouped.set(item.subRequirement, [])
    }
    grouped.get(item.subRequirement).push(item)
  })
  return grouped
})

const sortedRadarData = computed(() => {
  return [...currentRadarData.value].sort((a, b) => {
    if (a.subRequirement !== b.subRequirement) {
      return a.subRequirement - b.subRequirement
    }
    return a.round - b.round
  })
})

const maxRound = computed(() => {
  if (currentRadarData.value.length === 0) return 0
  return Math.max(...currentRadarData.value.map(item => item.round))
})

const avgImprovement = computed(() => {
  if (groupedRadarData.value.size === 0) return '0%'
  let totalImprovement = 0
  let count = 0

  groupedRadarData.value.forEach((data) => {
    if (data.length >= 2) {
      const first = calculateTotal(data[0])
      const last = calculateTotal(data[data.length - 1])
      if (first > 0) {
        totalImprovement += ((last - first) / first * 100)
        count++
      }
    }
  })

  return count > 0 ? `${(totalImprovement / count).toFixed(1)}% ↑` : '0%'
})

const getSubReqName = (index) => {
  const names = currentSubRequirements.value
  return names[index - 1] || `子需求 ${index}`
}

const setRadarRef = (el, subReqIndex) => {
  if (el) {
    radarRefs.value[subReqIndex] = el
  }
}

const calculateTotal = (item) => {
  return (item.I + item.N + item.V + item.E + item.S + item.T) || 0
}

const calculateFirstScore = (data) => {
  if (!data || data.length === 0) return 0
  return calculateTotal(data[0])
}

const calculateLastScore = (data) => {
  if (!data || data.length === 0) return 0
  return calculateTotal(data[data.length - 1])
}

const calculateImprovement = (data) => {
  if (!data || data.length < 2) return '0%'
  const first = calculateFirstScore(data)
  const last = calculateLastScore(data)
  if (first === 0) return '0%'
  const improvement = ((last - first) / first * 100).toFixed(1)
  return `${improvement}% ↑`
}

const getScoreClass = (score) => {
  if (score >= 8) return 'score-high'
  if (score >= 6) return 'score-medium'
  return 'score-low'
}

const initAllRadars = () => {
  Object.keys(radarRefs.value).forEach(subReqIndex => {
    initRadar(parseInt(subReqIndex))
  })
}

const initRadar = (subReqIndex) => {
  const container = radarRefs.value[subReqIndex]
  if (!container) {
    console.error(`雷达图容器 ${subReqIndex} 未找到`)
    return
  }

  if (radarCharts.value[subReqIndex]) {
    radarCharts.value[subReqIndex].dispose()
  }

  radarCharts.value[subReqIndex] = echarts.init(container)
  updateRadarChart(subReqIndex)
}

const updateRadarChart = (subReqIndex) => {
  const chart = radarCharts.value[subReqIndex]
  const data = groupedRadarData.value.get(subReqIndex)

  if (!chart || !data || data.length === 0) {
    console.log(`雷达图 ${subReqIndex} 数据为空，跳过更新`)
    return
  }

  console.log(`更新雷达图 ${subReqIndex}，数据:`, data)

  const indicators = [
    { name: "I - 独立性", max: 10 },
    { name: "N - 可协商性", max: 10 },
    { name: "V - 有价值性", max: 10 },
    { name: "E - 可估算性", max: 10 },
    { name: "S - 小尺寸", max: 10 },
    { name: "T - 可测试性", max: 10 }
  ]

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

  const seriesData = data.map((item, index) => ({
    name: `第${item.round}轮`,
    value: [item.I, item.N, item.V, item.E, item.S, item.T],
    itemStyle: {
      color: colors[index % colors.length]
    },
    areaStyle: {
      opacity: 0.3
    },
    lineStyle: {
      width: 2
    }
  }))

  const option = {
    title: {
      text: 'INVEST维度分析',
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#1f2937'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        let result = `<strong>${params.name}</strong><br/>`
        const dimensions = ['I - 独立性', 'N - 可协商性', 'V - 有价值性', 'E - 可估算性', 'S - 小尺寸', 'T - 可测试性']
        params.value.forEach((val, idx) => {
          result += `${dimensions[idx]}: ${val}/10<br/>`
        })
        result += `总分: ${params.value.reduce((a, b) => a + b, 0)}/60`
        return result
      }
    },
    legend: {
      data: data.map(item => `第${item.round}轮`),
      bottom: 5,
      orient: 'horizontal',
      textStyle: {
        fontSize: 11
      },
      itemWidth: 12,
      itemHeight: 12
    },
    radar: {
      indicator: indicators,
      radius: '60%',
      center: ['50%', '52%'],
      splitNumber: 5,
      axisName: {
        color: '#333',
        fontSize: 11
      },
      splitLine: {
        lineStyle: {
          color: '#e5e7eb'
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(59, 130, 246, 0.05)', 'rgba(59, 130, 246, 0.1)']
        }
      },
      axisLine: {
        lineStyle: {
          color: '#d1d5db'
        }
      }
    },
    series: [{
      type: 'radar',
      data: seriesData,
      emphasis: {
        lineStyle: {
          width: 4
        }
      },
      animationDuration: 800
    }]
  }

  chart.setOption(option, true)
  console.log(`雷达图 ${subReqIndex} 更新完成`)
}

onMounted(() => {
  console.log('RadarView 挂载，当前数据:', currentRadarData.value)
  console.log('分组后的数据:', groupedRadarData.value)

  setTimeout(() => {
    initAllRadars()
  }, 200)

  window.addEventListener('resize', () => {
    Object.values(radarCharts.value).forEach(chart => {
      chart?.resize()
    })
  })
})

watch(currentRadarData, (newData) => {
  console.log('雷达图数据变化:', newData)
  if (newData && newData.length > 0) {
    setTimeout(() => {
      initAllRadars()
    }, 200)
  }
}, { deep: true })

watch(groupedRadarData, (newGroupedData) => {
  console.log('分组数据变化:', newGroupedData)
  if (newGroupedData && newGroupedData.size > 0) {
    setTimeout(() => {
      initAllRadars()
    }, 200)
  }
}, { deep: true })

</script>

<style scoped>
.page {
  padding: 20px;
  max-width: 1600px;
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

.content {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stat-label {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-value {
  color: #1f2937;
  font-weight: 700;
  font-size: 24px;
}

.radar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.radar-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.radar-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.radar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f3f4f6;
}

.radar-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 16px;
  font-weight: 600;
}

.round-badge {
  padding: 4px 12px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.radar-chart {
  width: 100%;
  height: 350px;
  margin-bottom: 15px;
}

.radar-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid #f3f4f6;
}

.mini-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.mini-label {
  color: #6b7280;
  font-size: 12px;
}

.mini-value {
  color: #1f2937;
  font-weight: 600;
  font-size: 14px;
}

.data-table-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.data-table-section h3 {
  margin-bottom: 20px;
  color: #1f2937;
  font-size: 18px;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

thead {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

th {
  padding: 14px 10px;
  text-align: center;
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
}

td {
  padding: 12px 10px;
  text-align: center;
  border-bottom: 1px solid #e5e7eb;
  font-size: 13px;
}

tbody tr:hover {
  background: #f3f4f6;
}

tbody tr:last-child td {
  border-bottom: none;
}

.sub-req-cell {
  text-align: left;
  font-weight: 500;
  color: #1f2937;
  max-width: 150px;
  word-wrap: break-word;
}

.round-cell {
  font-weight: 600;
  color: #3b82f6;
  white-space: nowrap;
}

.score-high {
  color: #10b981;
  font-weight: 700;
  background: #d1fae5;
}

.score-medium {
  color: #f59e0b;
  font-weight: 600;
  background: #fef3c7;
}

.score-low {
  color: #ef4444;
  font-weight: 700;
  background: #fee2e2;
}

.total-score {
  font-weight: 700;
  color: #1f2937;
  background: #e0e7ff;
}
</style>

