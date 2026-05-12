<template>
  <div class="project-story-page">
    <section class="hero-card">
      <div>
        <p class="eyebrow">Project Source Code → User Stories</p>
        <h2>项目源码逐节点生成用户故事</h2>
        <p class="desc">
          上传 zip / tar / tar.gz / tgz 项目源码后，系统会先解析函数、方法、类等源码节点和调用关系，
          再使用 AI 智能体逐节点逆向生成用户故事。页面会实时展示每个节点的生成进度、调用关系和对应用户故事，
          并支持导出 Word、PDF、Markdown。
        </p>
      </div>
      <div class="upload-box">
        <input ref="fileInputRef" type="file" accept=".zip,.tar,.gz,.tgz,.py,.js,.jsx,.ts,.tsx,.vue,.java" hidden @change="handleFileChange" />
        <button class="primary-btn" :disabled="loading" @click="fileInputRef?.click()">
          {{ loading ? 'AI 智能体逐节点生成中...' : '上传项目源码' }}
        </button>
        <p class="tips">支持项目压缩包或单个源码文件。逐节点生成过程会实时返回。</p>
        <p v-if="selectedFile" class="filename">当前文件：{{ selectedFile.name }}</p>
      </div>
    </section>

    <section v-if="errorMessage" class="error-card">{{ errorMessage }}</section>

    <section v-if="loading || analysisResult" class="progress-card">
      <div>
        <strong>{{ progressText }}</strong>
        <p>{{ currentNodeText }}</p>
      </div>
      <div class="progress-bar"><span :style="{ width: progress + '%' }"></span></div>
    </section>

    <template v-if="analysisResult">
      <section class="summary-grid">
        <div class="stat-card"><strong>{{ statistics.file_count || 0 }}</strong><span>源码文件</span></div>
        <div class="stat-card"><strong>{{ statistics.symbol_count || 0 }}</strong><span>源码节点</span></div>
        <div class="stat-card"><strong>{{ statistics.edge_count || 0 }}</strong><span>调用关系</span></div>
        <div class="stat-card"><strong>{{ stories.length }}</strong><span>已生成用户故事</span></div>
      </section>

      <section class="summary-card">
        <div>
          <h3>分析结果</h3>
          <p>{{ analysisResult.summary || '项目源码节点已解析，AI 智能体正在逐节点生成用户故事。' }}</p>
          <p class="sub-desc">
            AI生成：{{ statistics.ai_story_count || aiStoryCount }} 条；兜底生成：{{ statistics.fallback_story_count || fallbackStoryCount }} 条。
          </p>
        </div>
        <div class="actions">
          <button :disabled="!canExport" @click="handleExport('docx')">导出 Word</button>
          <button :disabled="!canExport" @click="handleExport('pdf')">导出 PDF</button>
          <button :disabled="!canExport" @click="handleExport('markdown')">导出 Markdown</button>
        </div>
      </section>

      <section class="stream-panel panel">
        <div class="panel-header">
          <h3>逐节点 AI 生成过程</h3>
          <span>{{ stories.length }} / {{ nodes.length }}</span>
        </div>
        <div class="stream-list">
          <button
            v-for="story in stories"
            :key="story.id + story.node_id"
            class="stream-item"
            :class="{ selected: selectedNodeId === story.node_id }"
            @click="selectNode(story.node_id)"
          >
            <strong>{{ story.id }}｜{{ story.node_name }}</strong>
            <span>{{ story.ai_generated ? 'AI智能体生成' : '兜底生成' }}｜{{ story.module }}</span>
            <em>{{ story.story }}</em>
          </button>
        </div>
      </section>

      <section class="main-grid">
        <div class="panel">
          <div class="panel-header">
            <h3>函数调用树</h3>
            <span>点击节点查看源码与用户故事</span>
          </div>
          <div ref="functionTreeRef" class="chart"></div>
        </div>
        <div class="panel">
          <div class="panel-header">
            <h3>用户故事树</h3>
            <span>每个源码节点对应用户故事</span>
          </div>
          <div ref="storyTreeRef" class="chart"></div>
        </div>
      </section>

      <section class="detail-grid">
        <div class="panel node-panel">
          <div class="panel-header">
            <h3>源码节点列表</h3>
            <span>{{ filteredNodes.length }} / {{ nodes.length }}</span>
          </div>
          <div class="filters">
            <input v-model="keyword" placeholder="搜索节点 / 文件 / 签名" />
            <select v-model="typeFilter">
              <option value="all">全部</option>
              <option value="class">类</option>
              <option value="function">函数</option>
              <option value="method">方法</option>
            </select>
          </div>
          <div class="node-list">
            <button
              v-for="node in filteredNodes"
              :key="node.id"
              class="node-item"
              :class="{ selected: selectedNode?.id === node.id, done: hasStory(node.id) }"
              @click="selectNode(node.id)"
            >
              <div>
                <strong>{{ node.name }}</strong>
                <span>{{ node.type }}｜{{ node.language }}｜{{ hasStory(node.id) ? '已生成' : '等待生成' }}</span>
              </div>
              <em>{{ node.file }}:{{ node.line }}</em>
            </button>
          </div>
        </div>

        <div class="panel detail-panel">
          <div class="panel-header">
            <h3>节点详情与用户故事</h3>
            <span v-if="selectedNode">{{ selectedNode.id }}</span>
          </div>

          <div v-if="!selectedNode" class="empty-state">
            请选择左侧源码节点，或点击函数调用树 / 用户故事树中的节点。
          </div>

          <template v-else>
            <div class="node-detail-card">
              <p class="tag">{{ selectedNode.type }} / {{ selectedNode.language }}</p>
              <h4>{{ selectedNode.qualified_name || selectedNode.name }}</h4>
              <p class="path">{{ selectedNode.file }}:{{ selectedNode.line }}</p>
              <p v-if="selectedNode.signature" class="signature">{{ selectedNode.signature }}</p>
              <p v-if="selectedNode.docstring" class="docstring">{{ selectedNode.docstring }}</p>
            </div>

            <div class="relation-box">
              <div>
                <strong>调用下层节点</strong>
                <p>{{ outgoingNames || '无已识别调用' }}</p>
              </div>
              <div>
                <strong>被上层节点调用</strong>
                <p>{{ incomingNames || '无已识别调用方' }}</p>
              </div>
            </div>

            <div class="story-list">
              <div v-if="selectedStories.length === 0" class="empty-state small">
                当前节点正在等待 AI 智能体生成用户故事。
              </div>
              <article v-for="story in selectedStories" :key="story.id" class="story-card">
                <p class="story-id">{{ story.id }}｜{{ story.module }}｜{{ story.ai_generated ? 'AI智能体生成' : '兜底生成' }}</p>
                <h4>{{ story.story }}</h4>
                <p class="reasoning">{{ story.technical_reasoning }}</p>
                <div class="criteria">
                  <strong>验收标准</strong>
                  <ul>
                    <li v-for="item in story.acceptance_criteria" :key="item">{{ item }}</li>
                  </ul>
                </div>
              </article>
            </div>

            <details class="code-box" open>
              <summary>源码片段</summary>
              <pre>{{ selectedNode.code_snippet || '暂无源码片段' }}</pre>
            </details>
          </template>
        </div>
      </section>

      <section class="panel graph-panel">
        <div class="panel-header">
          <h3>函数调用关系图</h3>
          <span>展示跨文件函数 / 类依赖</span>
        </div>
        <div ref="graphRef" class="graph-chart"></div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onActivated, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts'
import { analyzeProjectSourceStream, exportProjectStory } from '@/services/api'

const fileInputRef = ref(null)
const selectedFile = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const analysisResult = ref(null)
const selectedNodeId = ref('')
const keyword = ref('')
const typeFilter = ref('all')
const progress = ref(0)
const progressText = ref('等待上传项目源码')
const currentNodeText = ref('')

const functionTreeRef = ref(null)
const storyTreeRef = ref(null)
const graphRef = ref(null)

let functionTreeChart = null
let storyTreeChart = null
let graphChart = null

const statistics = computed(() => analysisResult.value?.statistics || {})
const nodes = computed(() => analysisResult.value?.nodes || [])
const edges = computed(() => analysisResult.value?.edges || [])
const stories = computed(() => analysisResult.value?.stories || [])
const canExport = computed(() => !loading.value && !!analysisResult.value?.project_id && stories.value.length > 0)
const aiStoryCount = computed(() => stories.value.filter(item => item.ai_generated).length)
const fallbackStoryCount = computed(() => stories.value.filter(item => !item.ai_generated).length)

const selectedNode = computed(() => nodes.value.find(item => item.id === selectedNodeId.value))
const selectedStories = computed(() => stories.value.filter(item => item.node_id === selectedNodeId.value))

const filteredNodes = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  return nodes.value.filter(node => {
    const matchType = typeFilter.value === 'all' || node.type === typeFilter.value
    const matchKeyword = !kw || [node.name, node.qualified_name, node.file, node.signature]
      .filter(Boolean)
      .some(item => String(item).toLowerCase().includes(kw))
    return matchType && matchKeyword
  })
})

const incomingNames = computed(() => {
  const map = new Map(nodes.value.map(node => [node.id, node]))
  return edges.value
    .filter(edge => edge.target === selectedNodeId.value)
    .map(edge => map.get(edge.source)?.name)
    .filter(Boolean)
    .join('、')
})

const outgoingNames = computed(() => {
  const map = new Map(nodes.value.map(node => [node.id, node]))
  return edges.value
    .filter(edge => edge.source === selectedNodeId.value)
    .map(edge => map.get(edge.target)?.name)
    .filter(Boolean)
    .join('、')
})

const hasStory = (nodeId) => stories.value.some(story => story.node_id === nodeId)

const handleFileChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  selectedFile.value = file
  loading.value = true
  errorMessage.value = ''
  analysisResult.value = null
  selectedNodeId.value = ''
  progress.value = 0
  progressText.value = '开始上传并解析项目源码'
  currentNodeText.value = ''
  disposeCharts()

  try {
    await analyzeProjectSourceStream(file, async (message) => {
      if (message.event === 'start') {
        progressText.value = message.message || '开始解析项目源码'
      }
      if (message.event === 'parsed') {
        analysisResult.value = {
          project_id: message.project_id,
          filename: message.filename,
          summary: '项目源码节点已解析，AI 智能体正在逐节点生成用户故事。',
          modules: [],
          files: message.files || [],
          nodes: message.nodes || [],
          edges: message.edges || [],
          function_tree: message.function_tree,
          story_tree: null,
          graph: message.graph,
          stories: [],
          statistics: message.statistics || {},
        }
        selectedNodeId.value = message.nodes?.[0]?.id || ''
        progressText.value = `已解析 ${message.nodes?.length || 0} 个源码节点，开始逐节点生成用户故事`
        await nextTick()
        renderCharts()
      }
      if (message.event === 'node_start') {
        currentNodeText.value = `正在生成 ${message.index}/${message.total}：${message.node?.qualified_name || message.node?.name || ''}`
        if (!selectedNodeId.value && message.node?.id) selectedNodeId.value = message.node.id
      }
      if (message.event === 'node_story') {
        const result = analysisResult.value
        if (!result) return
        result.stories = [...(result.stories || []), message.story]
        result.statistics = {
          ...(result.statistics || {}),
          story_count: result.stories.length,
          ai_story_count: result.stories.filter(item => item.ai_generated).length,
          fallback_story_count: result.stories.filter(item => !item.ai_generated).length,
        }
        progress.value = Number(message.progress || 0)
        selectedNodeId.value = message.node_id
        progressText.value = `AI 智能体已生成 ${message.index}/${message.total} 个节点用户故事`
      }
      if (message.event === 'done') {
        analysisResult.value = message.result
        progress.value = 100
        progressText.value = '项目源码逐节点用户故事生成完成'
        currentNodeText.value = '可以查看每个节点的用户故事，也可以导出 Word、PDF、Markdown。'
        selectedNodeId.value = message.result?.nodes?.[0]?.id || selectedNodeId.value
        await nextTick()
        renderCharts()
      }
      if (message.event === 'error') {
        throw new Error(message.message || '项目源码分析失败')
      }
    })
  } catch (error) {
    errorMessage.value = error.message || '项目源码分析失败'
  } finally {
    loading.value = false
    event.target.value = ''
  }
}

const selectNode = (nodeId) => {
  if (!nodeId || nodeId === 'PROJECT_ROOT' || String(nodeId).startsWith('cycle-')) return
  const realNodeId = String(nodeId).replace(/^STORY-/, '')
  if (nodes.value.some(node => node.id === realNodeId)) {
    selectedNodeId.value = realNodeId
  }
}

const handleExport = async (format) => {
  if (!analysisResult.value?.project_id || loading.value) return
  try {
    await exportProjectStory(analysisResult.value.project_id, format)
  } catch (error) {
    errorMessage.value = error.message || '导出失败'
  }
}

const renderCharts = () => {
  disposeCharts()
  renderFunctionTree()
  renderStoryTree()
  renderGraph()
}

const renderFunctionTree = () => {
  if (!functionTreeRef.value || !analysisResult.value?.function_tree) return
  functionTreeChart = echarts.init(functionTreeRef.value)
  functionTreeChart.setOption({
    tooltip: { trigger: 'item', formatter: params => `${params.data?.name || ''}<br/>${params.data?.file || ''}:${params.data?.line || ''}` },
    series: [{
      type: 'tree',
      data: [analysisResult.value.function_tree],
      top: 30,
      left: 20,
      bottom: 30,
      right: 140,
      symbolSize: 10,
      orient: 'LR',
      roam: true,
      expandAndCollapse: true,
      initialTreeDepth: 3,
      label: { position: 'left', verticalAlign: 'middle', align: 'right', fontSize: 12 },
      leaves: { label: { position: 'right', verticalAlign: 'middle', align: 'left' } },
      lineStyle: { curveness: 0.35 },
      emphasis: { focus: 'descendant' }
    }]
  })
  functionTreeChart.on('click', params => selectNode(params.data?.id))
}

const renderStoryTree = () => {
  if (!storyTreeRef.value) return
  const tree = analysisResult.value?.story_tree || buildRealtimeStoryTree()
  if (!tree) return
  storyTreeChart = echarts.init(storyTreeRef.value)
  storyTreeChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: params => {
        const data = params.data || {}
        const attached = data.stories || []
        return attached.length ? `${data.name}<br/>用户故事：${attached.length} 条` : data.name
      }
    },
    series: [{
      type: 'tree',
      data: [tree],
      top: 30,
      left: 20,
      bottom: 30,
      right: 160,
      symbolSize: 11,
      orient: 'LR',
      roam: true,
      expandAndCollapse: true,
      initialTreeDepth: 3,
      label: { position: 'left', verticalAlign: 'middle', align: 'right', fontSize: 12 },
      leaves: { label: { position: 'right', verticalAlign: 'middle', align: 'left' } },
      lineStyle: { curveness: 0.35 },
      emphasis: { focus: 'descendant' }
    }]
  })
  storyTreeChart.on('click', params => selectNode(params.data?.node_id || params.data?.id))
}

const buildRealtimeStoryTree = () => {
  const root = analysisResult.value?.function_tree
  if (!root) return null
  const storyMap = new Map()
  stories.value.forEach(story => storyMap.set(story.node_id, story))
  const convert = (item) => {
    const story = storyMap.get(item.id)
    return {
      id: `STORY-${item.id}`,
      node_id: item.id,
      name: story ? `${item.name}\n${story.id}` : item.name,
      stories: story ? [story] : [],
      children: (item.children || []).filter(child => child.type !== 'cycle').map(convert)
    }
  }
  return {
    id: 'STORY-PROJECT_ROOT',
    name: '用户故事生成树',
    children: (root.children || []).map(convert)
  }
}

const renderGraph = () => {
  if (!graphRef.value || !analysisResult.value?.graph) return
  graphChart = echarts.init(graphRef.value)
  graphChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.dataType === 'edge') return params.data.name || '调用关系'
        const node = params.data.node || {}
        return `${node.qualified_name || node.name}<br/>${node.file || ''}:${node.line || ''}`
      }
    },
    legend: [{ data: analysisResult.value.graph.categories?.map(item => item.name) || [] }],
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      data: analysisResult.value.graph.nodes || [],
      links: analysisResult.value.graph.links || [],
      categories: analysisResult.value.graph.categories || [],
      label: { show: true, fontSize: 11 },
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: 8,
      force: { repulsion: 260, edgeLength: 130 },
      lineStyle: { opacity: 0.7, curveness: 0.08 },
      emphasis: { focus: 'adjacency' }
    }]
  })
  graphChart.on('click', params => {
    if (params.dataType === 'node') selectNode(params.data?.id)
  })
}

const disposeCharts = () => {
  functionTreeChart?.dispose()
  storyTreeChart?.dispose()
  graphChart?.dispose()
  functionTreeChart = null
  storyTreeChart = null
  graphChart = null
}

onActivated(async () => {
  await nextTick()
  functionTreeChart?.resize()
  storyTreeChart?.resize()
  graphChart?.resize()
})

onBeforeUnmount(() => disposeCharts())
</script>

<style scoped>
.project-story-page { min-height: 100%; color: #111827; }
.hero-card, .summary-card, .panel, .error-card, .progress-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 18px; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06); }
.hero-card { display: flex; justify-content: space-between; gap: 24px; padding: 28px; margin-bottom: 18px; }
.eyebrow { color: #2563eb; font-weight: 700; margin: 0 0 8px; }
.hero-card h2 { margin: 0; font-size: 28px; }
.desc { max-width: 820px; color: #6b7280; line-height: 1.8; }
.upload-box { min-width: 300px; padding: 18px; border: 1px dashed #93c5fd; border-radius: 16px; background: #eff6ff; text-align: center; }
.primary-btn, .actions button { border: none; border-radius: 12px; padding: 11px 16px; cursor: pointer; background: #2563eb; color: white; font-weight: 700; }
.primary-btn:disabled, .actions button:disabled { opacity: 0.65; cursor: not-allowed; }
.actions button:nth-child(2) { background: #0f766e; }
.actions button:nth-child(3) { background: #0f172a; }
.tips, .filename, .sub-desc { font-size: 13px; color: #64748b; }
.error-card { padding: 14px 18px; color: #b91c1c; background: #fef2f2; border-color: #fecaca; margin-bottom: 18px; }
.progress-card { padding: 18px; margin-bottom: 18px; }
.progress-card strong { color: #111827; }
.progress-card p { color: #64748b; margin: 6px 0 0; }
.progress-bar { margin-top: 12px; height: 10px; border-radius: 999px; background: #e5e7eb; overflow: hidden; }
.progress-bar span { display: block; height: 100%; border-radius: inherit; background: #2563eb; transition: width .25s ease; }
.summary-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-bottom: 18px; }
.stat-card { padding: 18px; border-radius: 16px; background: #fff; border: 1px solid #e5e7eb; }
.stat-card strong { display: block; font-size: 26px; color: #2563eb; }
.stat-card span { color: #6b7280; font-size: 13px; }
.summary-card { display: flex; justify-content: space-between; gap: 20px; padding: 20px; margin-bottom: 18px; }
.summary-card h3, .panel-header h3 { margin: 0 0 8px; }
.summary-card p { margin: 0; color: #4b5563; line-height: 1.8; }
.actions { display: flex; gap: 10px; align-items: center; white-space: nowrap; }
.main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 18px; }
.detail-grid { display: grid; grid-template-columns: 380px 1fr; gap: 18px; margin-bottom: 18px; }
.panel { padding: 18px; margin-bottom: 18px; }
.panel-header { display: flex; justify-content: space-between; gap: 14px; align-items: flex-start; margin-bottom: 12px; }
.panel-header span { color: #64748b; font-size: 13px; }
.chart { height: 480px; }
.graph-chart { height: 560px; }
.stream-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; max-height: 340px; overflow: auto; }
.stream-item, .node-item { width: 100%; text-align: left; border: 1px solid #e5e7eb; background: white; border-radius: 14px; padding: 12px; cursor: pointer; }
.stream-item:hover, .stream-item.selected, .node-item:hover, .node-item.selected { border-color: #2563eb; background: #eff6ff; }
.stream-item strong, .node-item strong { display: block; color: #111827; }
.stream-item span, .stream-item em, .node-item span, .node-item em { display: block; color: #6b7280; font-size: 12px; margin-top: 4px; font-style: normal; word-break: break-all; }
.stream-item em { line-height: 1.6; }
.filters { display: flex; gap: 8px; margin-bottom: 12px; }
.filters input, .filters select { border: 1px solid #d1d5db; border-radius: 10px; padding: 10px; outline: none; }
.filters input { flex: 1; }
.node-list { max-height: 720px; overflow: auto; padding-right: 4px; }
.node-item { margin-bottom: 10px; }
.node-item.done { border-left: 4px solid #22c55e; }
.empty-state { padding: 30px; text-align: center; color: #64748b; border: 1px dashed #cbd5e1; border-radius: 16px; background: #f8fafc; }
.empty-state.small { padding: 18px; margin-bottom: 12px; }
.node-detail-card { border-radius: 16px; background: #f8fafc; padding: 16px; border: 1px solid #e5e7eb; }
.tag, .story-id { margin: 0 0 8px; color: #2563eb; font-weight: 700; font-size: 13px; }
.node-detail-card h4, .story-card h4 { margin: 0 0 8px; }
.path, .signature, .docstring, .reasoning { color: #64748b; line-height: 1.7; margin: 6px 0; }
.signature { font-family: Consolas, Monaco, monospace; color: #0f172a; }
.relation-box { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 14px 0; }
.relation-box > div { border: 1px solid #e5e7eb; border-radius: 14px; padding: 12px; }
.relation-box p { color: #64748b; line-height: 1.7; }
.story-card { border: 1px solid #dbeafe; background: #eff6ff; border-radius: 16px; padding: 16px; margin-bottom: 12px; }
.criteria strong { display: block; margin: 12px 0 6px; }
.criteria li { margin-bottom: 6px; line-height: 1.7; }
.code-box { margin-top: 14px; border: 1px solid #e5e7eb; border-radius: 14px; overflow: hidden; }
.code-box summary { padding: 12px; cursor: pointer; background: #f3f4f6; font-weight: 700; }
.code-box pre { margin: 0; padding: 14px; overflow: auto; max-height: 360px; background: #0f172a; color: #e5e7eb; font-size: 12px; line-height: 1.6; }
@media (max-width: 1200px) { .hero-card, .summary-card { flex-direction: column; } .main-grid, .detail-grid, .summary-grid, .stream-list { grid-template-columns: 1fr; } }
</style>
