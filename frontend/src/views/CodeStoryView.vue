<template>
  <div class="code-story-page">
    <section class="page-header">
      <div>
        <p class="eyebrow">Code Reverse Engineering</p>
        <h2>由代码到用户故事</h2>
        <p class="desc">
          支持粘贴代码片段或上传单个代码文件。系统会优先拆分函数/方法/类；无法拆分时保留整体代码，并逐个代码单元逆向生成需求和用户故事。
        </p>
      </div>
      <div class="header-actions" v-if="result?.code_story_id">
        <button @click="download('markdown')">导出 Markdown</button>
        <button @click="download('docx')">导出 Word</button>
        <button @click="download('pdf')">导出 PDF</button>
      </div>
    </section>

    <section class="workspace">
      <div class="input-panel card">
        <div class="panel-title">
          <h3>代码输入</h3>
          <span>{{ language || '自动识别/未指定' }}</span>
        </div>

        <div class="form-row">
          <label>代码语言</label>
          <select v-model="language">
            <option value="">自动识别</option>
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="java">Java</option>
            <option value="vue">Vue</option>
          </select>
        </div>

        <div class="form-row">
          <label>上传单个代码文件</label>
          <input type="file" accept=".py,.js,.jsx,.ts,.tsx,.java,.vue,.txt" @change="handleFileUpload" />
          <small v-if="filename">当前文件：{{ filename }}</small>
        </div>

        <textarea v-model="code" placeholder="请粘贴需要逆向生成用户故事的代码..."></textarea>

        <button class="primary-btn" :disabled="loading || !code.trim()" @click="generateFromCode">
          {{ loading ? '分析生成中...' : '开始逆向生成' }}
        </button>
      </div>

      <div class="result-panel card">
        <div class="panel-title">
          <h3>分析概览</h3>
          <span v-if="result">{{ splitModeText }}</span>
        </div>
        <div v-if="result" class="overview">
          <p>{{ result.summary }}</p>
          <div class="stats-grid">
            <div>
              <strong>{{ result.statistics?.unit_count || 0 }}</strong>
              <span>代码单元</span>
            </div>
            <div>
              <strong>{{ result.statistics?.edge_count || 0 }}</strong>
              <span>引用关系</span>
            </div>
            <div>
              <strong>{{ result.statistics?.story_count || 0 }}</strong>
              <span>用户故事</span>
            </div>
          </div>
        </div>
        <div v-else class="empty">等待代码解析与故事生成结果</div>
      </div>
    </section>

    <section class="card" v-if="items.length">
      <div class="panel-title">
        <h3>代码单元列表</h3>
        <span>{{ items.length }} 个</span>
      </div>
      <div class="unit-grid">
        <div
          v-for="(item, index) in items"
          :key="item.node_id"
          class="unit-card"
          :class="{ active: selectedIndex === index }"
          @click="selectedIndex = index"
        >
          <div class="unit-head">
            <span class="index">{{ item.node?.id }}</span>
            <span class="type">{{ item.node?.type }}</span>
          </div>
          <h4>{{ item.node?.name }}</h4>
          <p>{{ item.requirement?.title }}</p>
          <small>{{ item.node?.file }}:{{ item.node?.line }}</small>
        </div>
      </div>
    </section>

    <section class="detail-grid" v-if="selectedItem">
      <div class="card story-card">
        <div class="panel-title">
          <h3>代码到需求与用户故事</h3>
          <span>{{ selectedItem.node?.signature || selectedItem.node?.name }}</span>
        </div>

        <div class="block">
          <h4>逆向需求</h4>
          <p><b>标题：</b>{{ selectedItem.requirement?.title }}</p>
          <p><b>角色：</b>{{ selectedItem.requirement?.role }}</p>
          <p><b>描述：</b>{{ selectedItem.requirement?.description }}</p>
        </div>

        <div class="block">
          <h4>用户故事</h4>
          <div class="story-text">{{ selectedItem.user_story?.story }}</div>
        </div>

        <div class="block">
          <h4>验收标准</h4>
          <ol>
            <li v-for="criteria in selectedItem.user_story?.acceptance_criteria || []" :key="criteria">
              {{ criteria }}
            </li>
          </ol>
        </div>

        <div class="block">
          <h4>业务规则与异常场景</h4>
          <ul>
            <li v-for="rule in selectedItem.requirement?.business_rules || []" :key="rule">
              {{ rule }}
            </li>
          </ul>
        </div>

        <div class="block">
          <h4>技术推导依据</h4>
          <p>{{ selectedItem.technical_reasoning }}</p>
        </div>
      </div>

      <div class="card relation-card">
        <div class="panel-title">
          <h3>引用关系</h3>
          <span>{{ relationCount }} 条</span>
        </div>

        <div v-if="relationCount" class="relation-list">
          <div v-if="selectedItem.incoming?.length" class="relation-section">
            <h4>被以下代码单元引用</h4>
            <button
              v-for="rel in selectedItem.incoming"
              :key="`in-${rel.node_id}`"
              class="relation-chip incoming"
              @click="selectByNodeId(rel.node_id)"
            >
              ← {{ rel.name }}
            </button>
          </div>

          <div v-if="selectedItem.outgoing?.length" class="relation-section">
            <h4>引用以下代码单元</h4>
            <button
              v-for="rel in selectedItem.outgoing"
              :key="`out-${rel.node_id}`"
              class="relation-chip outgoing"
              @click="selectByNodeId(rel.node_id)"
            >
              → {{ rel.name }}
            </button>
          </div>
        </div>
        <div v-else class="empty small">该代码单元没有识别到函数引用关系</div>

        <div class="code-preview">
          <h4>代码片段</h4>
          <pre>{{ selectedItem.node?.code_snippet }}</pre>
        </div>
      </div>
    </section>

    <section class="card" v-if="edges.length">
      <div class="panel-title">
        <h3>全局函数引用关系</h3>
        <span>{{ edges.length }} 条</span>
      </div>
      <div class="edge-list">
        <div v-for="edge in resolvedEdges" :key="`${edge.source}-${edge.target}`" class="edge-item">
          <span>{{ edge.sourceName }}</span>
          <b>→</b>
          <span>{{ edge.targetName }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { analyzeCodeStory, exportCodeStory } from '@/services/api'

const code = ref('')
const language = ref('')
const filename = ref('code_snippet')
const loading = ref(false)
const result = ref(null)
const selectedIndex = ref(0)

const items = computed(() => result.value?.items || [])
const edges = computed(() => result.value?.edges || [])
const selectedItem = computed(() => items.value[selectedIndex.value] || null)
const relationCount = computed(() => (selectedItem.value?.incoming?.length || 0) + (selectedItem.value?.outgoing?.length || 0))

const splitModeText = computed(() => {
  const mode = result.value?.split_mode
  if (mode === 'function') return '已按函数/方法拆分'
  if (mode === 'single_symbol') return '识别到单个代码单元'
  if (mode === 'whole') return '整体代码分析'
  return '已完成'
})

const nodeNameMap = computed(() => {
  const map = {}
  ;(result.value?.nodes || []).forEach(node => {
    map[node.id] = node.qualified_name || node.name || node.id
  })
  return map
})

const resolvedEdges = computed(() => edges.value.map(edge => ({
  ...edge,
  sourceName: nodeNameMap.value[edge.source] || edge.source,
  targetName: nodeNameMap.value[edge.target] || edge.target
})))

const handleFileUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  filename.value = file.name
  code.value = await file.text()
  const ext = file.name.split('.').pop()?.toLowerCase()
  const extMap = {
    py: 'python',
    js: 'javascript',
    jsx: 'javascript',
    ts: 'typescript',
    tsx: 'typescript',
    java: 'java',
    vue: 'vue'
  }
  language.value = extMap[ext] || language.value
}

const generateFromCode = async () => {
  loading.value = true
  result.value = null
  selectedIndex.value = 0

  try {
    result.value = await analyzeCodeStory({
      code: code.value,
      language: language.value,
      filename: filename.value || 'code_snippet'
    })
  } catch (error) {
    alert(error.message || '生成失败，请检查后端服务是否启动')
  } finally {
    loading.value = false
  }
}

const selectByNodeId = (nodeId) => {
  const index = items.value.findIndex(item => item.node_id === nodeId)
  if (index >= 0) selectedIndex.value = index
}

const download = async (format) => {
  if (!result.value?.code_story_id) return
  try {
    await exportCodeStory(result.value.code_story_id, format)
  } catch (error) {
    alert(error.message || '导出失败')
  }
}
</script>

<style scoped>
.code-story-page { max-width: 1280px; margin: 0 auto; color: #111827; }
.page-header { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 18px; }
.eyebrow { color: #2563eb; font-weight: 700; margin: 0 0 6px; }
h2 { margin: 0 0 8px; color: #111827; }
.desc { margin: 0; color: #4b5563; line-height: 1.7; max-width: 880px; }
.header-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.header-actions button { border: 1px solid #bfdbfe; background: #eff6ff; color: #1d4ed8; border-radius: 10px; padding: 9px 12px; cursor: pointer; font-weight: 700; }
.workspace { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; align-items: stretch; }
.card { background: #ffffff; border-radius: 14px; padding: 18px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08); margin-bottom: 18px; }
.panel-title { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 14px; }
.panel-title h3 { margin: 0; color: #111827; }
.panel-title span { color: #6b7280; font-size: 13px; }
.form-row { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; color: #374151; }
.form-row small { color: #6b7280; }
select, input, textarea { border: 1px solid #d1d5db; border-radius: 10px; padding: 10px 12px; background: #ffffff; color: #111827; }
textarea { width: 100%; min-height: 360px; resize: vertical; font-family: Consolas, Monaco, monospace; line-height: 1.6; box-sizing: border-box; }
.primary-btn { width: 100%; border: none; border-radius: 10px; padding: 12px; background: #2563eb; color: #ffffff; cursor: pointer; font-weight: 700; }
.primary-btn:disabled { background: #93c5fd; cursor: not-allowed; }
.empty { color: #6b7280; background: #f9fafb; border-radius: 10px; padding: 36px; text-align: center; }
.empty.small { padding: 18px; }
.overview p { color: #374151; line-height: 1.8; margin-top: 0; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.stats-grid div { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px; text-align: center; }
.stats-grid strong { display: block; color: #2563eb; font-size: 26px; margin-bottom: 4px; }
.stats-grid span { color: #4b5563; font-size: 13px; }
.unit-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; }
.unit-card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px; cursor: pointer; background: #f9fafb; transition: 0.2s; color: #111827; }
.unit-card:hover, .unit-card.active { border-color: #2563eb; background: #eff6ff; transform: translateY(-1px); }
.unit-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.index { color: #2563eb; font-weight: 800; }
.type { color: #1f2937; background: #e5e7eb; border-radius: 999px; padding: 2px 8px; font-size: 12px; }
.unit-card h4 { margin: 0 0 8px; color: #111827; }
.unit-card p { margin: 0 0 8px; color: #374151; line-height: 1.6; }
.unit-card small { color: #6b7280; }
.detail-grid { display: grid; grid-template-columns: 1fr 0.9fr; gap: 18px; align-items: start; }
.block { border-top: 1px solid #e5e7eb; padding-top: 12px; margin-top: 12px; }
.block:first-of-type { border-top: none; margin-top: 0; padding-top: 0; }
.block h4, .relation-section h4, .code-preview h4 { margin: 0 0 10px; color: #111827; }
.block p, .block li { color: #374151; line-height: 1.8; }
.story-text { background: #f9fafb; border-radius: 10px; padding: 14px; color: #1f2937; line-height: 1.8; }
.relation-list { display: flex; flex-direction: column; gap: 14px; }
.relation-chip { display: inline-flex; margin: 0 8px 8px 0; border: none; border-radius: 999px; padding: 8px 12px; cursor: pointer; font-weight: 700; }
.relation-chip.incoming { background: #fef3c7; color: #92400e; }
.relation-chip.outgoing { background: #dbeafe; color: #1d4ed8; }
.code-preview { margin-top: 16px; }
pre { max-height: 420px; overflow: auto; white-space: pre-wrap; word-break: break-word; background: #0f172a; color: #e5e7eb; border-radius: 12px; padding: 14px; line-height: 1.6; }
.edge-list { display: flex; flex-direction: column; gap: 8px; }
.edge-item { display: flex; align-items: center; gap: 12px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 10px 12px; color: #374151; }
.edge-item b { color: #2563eb; }
@media (max-width: 980px) {
  .workspace, .detail-grid { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; }
}
</style>
