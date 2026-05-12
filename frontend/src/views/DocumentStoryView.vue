<template>
  <div class="document-story-page">
    <section class="page-header">
      <div>
        <p class="eyebrow">需求文档解析</p>
        <h2>由需求文档到用户故事</h2>
        <p class="desc">上传 Word、PDF、Markdown 或 TXT 文档后，系统自动解析需求、拆分功能点、生成用户故事并展示需求关系图。</p>
      </div>
      <div class="actions" v-if="documentId">
        <button @click="exportResult('markdown')">导出 Markdown</button>
        <button @click="exportResult('json')">导出 JSON</button>
      </div>
    </section>

    <section class="upload-card card">
      <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
        <input ref="fileInput" type="file" accept=".docx,.pdf,.md,.markdown,.txt" hidden @change="handleFileChange" />
        <div class="upload-icon">📄</div>
        <h3>{{ file ? file.name : '上传需求文档' }}</h3>
        <p>支持 .docx / .pdf / .md / .txt</p>
        <button class="primary-btn" @click="fileInput?.click()">选择文件</button>
        <button class="analyze-btn" :disabled="!file || loading" @click="analyzeDocument">
          {{ loading ? '解析中...' : '开始解析并生成' }}
        </button>
      </div>
    </section>

    <section class="stats" v-if="requirements.length">
      <div class="stat-card">
        <strong>{{ requirements.length }}</strong>
        <span>需求总数</span>
      </div>
      <div class="stat-card">
        <strong>{{ functionalCount }}</strong>
        <span>功能性需求</span>
      </div>
      <div class="stat-card">
        <strong>{{ nonFunctionalCount }}</strong>
        <span>非功能性需求</span>
      </div>
      <div class="stat-card">
        <strong>{{ moduleCount }}</strong>
        <span>模块数量</span>
      </div>
    </section>

    <section class="content-grid" v-if="requirements.length">
      <div class="card requirement-list">
        <div class="panel-title">
          <h3>分析后的需求</h3>
          <span>点击查看用户故事</span>
        </div>

        <div class="module-group" v-for="moduleName in moduleNames" :key="moduleName">
          <h4>{{ moduleName }}</h4>
          <div
            v-for="req in getRequirementsByModule(moduleName)"
            :key="req.id"
            class="requirement-item"
            :class="{ active: selectedRequirement?.id === req.id }"
            @click="selectRequirement(req)"
          >
            <div class="requirement-main">
              <span class="req-id">{{ req.id }}</span>
              <span class="req-title">{{ req.title }}</span>
            </div>
            <p>{{ req.description }}</p>
            <span class="type-tag" :class="req.type === 'functional' ? 'functional' : 'non-functional'">
              {{ req.type === 'functional' ? '功能性需求' : '非功能性需求' }}
            </span>
          </div>
        </div>
      </div>

      <div class="card story-panel">
        <div class="panel-title">
          <h3>用户故事生成情况</h3>
          <span v-if="selectedRequirement">{{ selectedRequirement.id }}</span>
        </div>

        <div v-if="selectedRequirement" class="story-detail">
          <h4>{{ selectedRequirement.title }}</h4>
          <p class="req-desc">{{ selectedRequirement.description }}</p>

          <template v-if="selectedRequirement.user_story">
            <div class="story-box">
              <h5>用户故事</h5>
              <p>{{ selectedRequirement.user_story }}</p>
            </div>

            <div class="story-box">
              <h5>验收标准</h5>
              <ul>
                <li v-for="(item, index) in selectedRequirement.acceptance_criteria || []" :key="index">
                  {{ item }}
                </li>
              </ul>
            </div>
          </template>

          <div v-else class="empty small">该项为非功能性需求或暂无用户故事，可作为约束参与相关功能故事生成。</div>

          <div class="story-box" v-if="relatedRequirements.length">
            <h5>关联需求</h5>
            <div class="related-list">
              <button v-for="item in relatedRequirements" :key="item.id" @click="selectRequirement(item)">
                {{ item.id }} {{ item.title }}
              </button>
            </div>
          </div>
        </div>

        <div v-else class="empty">请选择左侧需求或点击下方关系图节点</div>
      </div>
    </section>

    <section class="card graph-card" v-if="requirements.length">
      <div class="panel-title">
        <h3>需求关系图</h3>
        <span>点击节点查看详情</span>
      </div>
      <div ref="graphRef" class="graph"></div>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onActivated, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts'
import { analyzeRequirementDocument, exportDocumentStory } from '@/services/api'

const fileInput = ref(null)
const file = ref(null)
const loading = ref(false)
const documentId = ref('')
const requirements = ref([])
const links = ref([])
const selectedRequirement = ref(null)
const graphRef = ref(null)
let chart = null

const functionalCount = computed(() => requirements.value.filter(item => item.type === 'functional').length)
const nonFunctionalCount = computed(() => requirements.value.filter(item => item.type !== 'functional').length)
const moduleNames = computed(() => [...new Set(requirements.value.map(item => item.module || '未分组模块'))])
const moduleCount = computed(() => moduleNames.value.length)

const relatedRequirements = computed(() => {
  if (!selectedRequirement.value) return []
  const id = selectedRequirement.value.id
  const relatedIds = links.value
    .filter(link => link.source === id || link.target === id)
    .flatMap(link => [link.source, link.target])
    .filter(item => item !== id)
  return requirements.value.filter(item => relatedIds.includes(item.id))
})

const handleFileChange = (event) => {
  file.value = event.target.files?.[0] || null
}

const handleDrop = (event) => {
  file.value = event.dataTransfer.files?.[0] || null
}

const normalizeResult = (data) => {
  documentId.value = data.document_id || data.id || ''
  requirements.value = data.requirements || data.data?.requirements || []
  links.value = data.links || data.graph?.links || []
  selectedRequirement.value = requirements.value[0] || null
}

const analyzeDocument = async () => {
  if (!file.value) return
  loading.value = true
  try {
    const data = await analyzeRequirementDocument(file.value)
    normalizeResult(data)
    await nextTick()
    renderGraph()
  } catch (error) {
    alert(error.message || '文档解析失败，请检查后端服务是否启动')
  } finally {
    loading.value = false
  }
}

const getRequirementsByModule = (moduleName) => {
  return requirements.value.filter(item => (item.module || '未分组模块') === moduleName)
}

const selectRequirement = (req) => {
  selectedRequirement.value = req
  highlightGraphNode(req.id)
}

const renderGraph = () => {
  if (!graphRef.value) return
  chart?.dispose()
  chart = echarts.init(graphRef.value)

  const nodes = requirements.value.map(item => ({
    id: item.id,
    name: `${item.id}\n${item.title}`,
    value: item.title,
    category: item.type === 'functional' ? 0 : 1,
    symbolSize: item.type === 'functional' ? 58 : 48
  }))

  const graphLinks = links.value.map(item => ({
    source: item.source,
    target: item.target,
    label: { show: true, formatter: item.relation || item.type || '关联' }
  }))

  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: [{ data: ['功能性需求', '非功能性需求'] }],
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      categories: [{ name: '功能性需求' }, { name: '非功能性需求' }],
      data: nodes,
      links: graphLinks,
      edgeSymbol: ['none', 'arrow'],
      label: { show: true, fontSize: 12 },
      edgeLabel: { fontSize: 11 },
      force: { repulsion: 420, edgeLength: 130 },
      lineStyle: { curveness: 0.18 }
    }]
  })

  chart.on('click', params => {
    if (params.dataType === 'node') {
      const req = requirements.value.find(item => item.id === params.data.id)
      if (req) selectedRequirement.value = req
    }
  })
}

const highlightGraphNode = (id) => {
  if (!chart) return
  chart.dispatchAction({ type: 'downplay', seriesIndex: 0 })
  chart.dispatchAction({ type: 'highlight', seriesIndex: 0, dataIndex: requirements.value.findIndex(item => item.id === id) })
}

const exportResult = async (format) => {
  if (!documentId.value) return
  try {
    await exportDocumentStory(documentId.value, format)
  } catch (error) {
    alert(error.message || '导出失败')
  }
}

const handleWindowResize = () => chart?.resize()
window.addEventListener('resize', handleWindowResize)

onActivated(async () => {
  await nextTick()
  chart?.resize()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleWindowResize)
  chart?.dispose()
})
</script>

<style scoped>
.document-story-page { max-width: 1320px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 18px; }
.eyebrow { color: #2563eb; font-weight: 700; margin: 0 0 6px; }
h2 { margin: 0 0 8px; color: #111827; }
.desc { margin: 0; color: #6b7280; }
.card { background: #fff; border-radius: 14px; padding: 18px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08); margin-bottom: 18px; }
.actions { display: flex; gap: 10px; }
.actions button, .related-list button { border: 1px solid #bfdbfe; background: #eff6ff; color: #1d4ed8; border-radius: 8px; padding: 8px 12px; cursor: pointer; }
.upload-area { border: 2px dashed #bfdbfe; background: #f8fbff; border-radius: 14px; padding: 34px; text-align: center; }
.upload-icon { font-size: 42px; }
.upload-area h3 { margin: 10px 0 6px; }
.upload-area p { margin: 0 0 16px; color: #6b7280; }
.primary-btn, .analyze-btn { border: none; border-radius: 10px; padding: 10px 16px; margin: 0 6px; cursor: pointer; font-weight: 700; }
.primary-btn { background: #e0f2fe; color: #0369a1; }
.analyze-btn { background: #2563eb; color: white; }
.analyze-btn:disabled { background: #93c5fd; cursor: not-allowed; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px; }
.stat-card { background: white; border-radius: 14px; padding: 18px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08); }
.stat-card strong { display: block; font-size: 30px; color: #2563eb; }
.stat-card span { color: #6b7280; }
.content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; align-items: start; }
.panel-title { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 14px; }
.panel-title h3 { margin: 0; color: #111827; }
.panel-title span { color: #6b7280; font-size: 13px; }
.module-group h4 { color: #111827; margin: 16px 0 10px; }
.requirement-item { border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px; margin-bottom: 12px; background: #f9fafb; cursor: pointer; transition: 0.2s; }
.requirement-item:hover, .requirement-item.active { border-color: #2563eb; background: #eff6ff; }
.requirement-main { display: flex; gap: 10px; align-items: center; font-weight: 700; color: #111827; }
.req-id { color: #2563eb; }
.requirement-item p, .req-desc { color: #4b5563; line-height: 1.7; }
.type-tag { display: inline-block; border-radius: 999px; padding: 4px 10px; font-size: 12px; }
.type-tag.functional { background: #dcfce7; color: #15803d; }
.type-tag.non-functional { background: #fef3c7; color: #92400e; }
.story-detail h4 { margin-top: 0; color: #111827; }
.story-box { background: #f9fafb; border-radius: 12px; padding: 14px; margin-top: 12px; }
.story-box h5 { margin: 0 0 8px; color: #111827; }
.story-box p, .story-box li { line-height: 1.8; color: #374151; }
.related-list { display: flex; flex-wrap: wrap; gap: 8px; }
.empty { color: #9ca3af; background: #f9fafb; border-radius: 12px; padding: 36px; text-align: center; }
.empty.small { padding: 18px; text-align: left; }
.graph { height: 520px; width: 100%; }
@media (max-width: 1080px) { .content-grid, .stats { grid-template-columns: 1fr; } .page-header { flex-direction: column; } }
</style>
