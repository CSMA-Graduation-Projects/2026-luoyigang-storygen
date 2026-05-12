<template>
  <div class="history-page">
    <section class="page-header">
      <div>
        <p class="eyebrow">History</p>
        <h2>历史用户故事生成</h2>
        <p class="desc">历史数据按文本需求、代码、需求文档和项目源码四类分别存储与展示。</p>
      </div>
      <button class="refresh-btn" @click="loadList(activeType)">刷新列表</button>
    </section>

    <section class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.type"
        :class="{ active: activeType === tab.type }"
        @click="switchTab(tab.type)"
      >
        <strong>{{ tab.title }}</strong>
        <span>{{ counts[tab.type] ?? '-' }}</span>
      </button>
    </section>

    <section v-if="errorMessage" class="error-card">{{ errorMessage }}</section>

    <section class="history-layout">
      <aside class="history-list card">
        <div class="panel-title">
          <h3>{{ currentTab.title }}历史</h3>
          <span>{{ historyItems.length }} 条</span>
        </div>

        <div v-if="loadingList" class="empty">正在读取历史记录...</div>
        <div v-else-if="historyItems.length === 0" class="empty">暂无历史记录，请先完成一次生成。</div>

        <button
          v-for="item in historyItems"
          :key="item.id"
          class="history-item"
          :class="{ selected: selectedId === item.id }"
          @click="openHistory(item)"
        >
          <div class="item-main">
            <strong>{{ item.title || item.filename || item.requirement || '未命名历史记录' }}</strong>
            <span>{{ formatDate(item.created_at) }}</span>
          </div>
          <p>{{ item.summary || buildItemSummary(item) }}</p>
          <div class="item-meta">
            <em v-if="item.statistics">故事 {{ item.statistics.story_count || 0 }}</em>
            <em v-if="item.filename">{{ item.filename }}</em>
            <em v-if="item.language">{{ item.language }}</em>
          </div>
        </button>
      </aside>

      <main class="history-detail card">
        <div v-if="loadingDetail" class="empty large">正在加载历史详情...</div>
        <div v-else-if="!detail" class="empty large">请选择左侧任意历史记录查看对应展示结果。</div>

        <template v-else>
          <section class="detail-header">
            <div>
              <p class="type-label">{{ currentTab.title }}</p>
              <h3>{{ detail.title || detail.filename || '历史详情' }}</h3>
              <p>{{ detail.summary }}</p>
            </div>
            <div class="stats" v-if="detail.statistics">
              <div v-for="(value, key) in detail.statistics" :key="key">
                <strong>{{ value }}</strong>
                <span>{{ statLabel(key) }}</span>
              </div>
            </div>
          </section>

          <TextHistoryDetail v-if="activeType === 'text'" :detail="detail" />
          <CodeHistoryDetail v-else-if="activeType === 'code'" :detail="detail" />
          <DocumentHistoryDetail v-else-if="activeType === 'document'" :detail="detail" />
          <ProjectHistoryDetail v-else-if="activeType === 'project'" :detail="detail" />
        </template>
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { getStoryHistoryDetail, getStoryHistoryList } from '@/services/api'
import { renderMarkdown } from '@/utils/markdown'

const tabs = [
  { type: 'text', title: '文本需求生成' },
  { type: 'code', title: '代码生成用户故事' },
  { type: 'document', title: '文档生成用户故事' },
  { type: 'project', title: '项目源码生成用户故事' },
]

const activeType = ref('text')
const historyItems = ref([])
const counts = ref({ text: 0, code: 0, document: 0, project: 0 })
const selectedId = ref('')
const detail = ref(null)
const loadingList = ref(false)
const loadingDetail = ref(false)
const errorMessage = ref('')

const currentTab = computed(() => tabs.find(item => item.type === activeType.value) || tabs[0])

const loadList = async (type) => {
  loadingList.value = true
  errorMessage.value = ''
  try {
    const data = await getStoryHistoryList(type, 80)
    historyItems.value = data.items || []
    counts.value[type] = historyItems.value.length
    if (historyItems.value.length) {
      await openHistory(historyItems.value[0])
    } else {
      detail.value = null
      selectedId.value = ''
    }
  } catch (error) {
    errorMessage.value = error.message || '读取历史列表失败，请确认 MongoDB 与后端服务是否正常。'
    historyItems.value = []
    detail.value = null
  } finally {
    loadingList.value = false
  }
}

const loadAllCounts = async () => {
  for (const tab of tabs) {
    try {
      const data = await getStoryHistoryList(tab.type, 100)
      counts.value[tab.type] = data.items?.length || 0
      if (tab.type === activeType.value) historyItems.value = data.items || []
    } catch (error) {
      counts.value[tab.type] = 0
    }
  }
}

const switchTab = async (type) => {
  activeType.value = type
  selectedId.value = ''
  detail.value = null
  await loadList(type)
}

const openHistory = async (item) => {
  if (!item?.id) return
  selectedId.value = item.id
  loadingDetail.value = true
  errorMessage.value = ''
  try {
    detail.value = await getStoryHistoryDetail(activeType.value, item.id)
    await nextTick()
  } catch (error) {
    errorMessage.value = error.message || '读取历史详情失败'
  } finally {
    loadingDetail.value = false
  }
}

const formatDate = (value) => {
  if (!value) return ''
  return String(value).replace('T', ' ').slice(0, 19)
}

const buildItemSummary = (item) => {
  const stat = item.statistics || {}
  if (activeType.value === 'project') return `节点 ${stat.symbol_count || 0}，用户故事 ${stat.story_count || 0}`
  if (activeType.value === 'document') return `需求 ${stat.requirement_count || 0}，用户故事 ${stat.story_count || 0}`
  return `功能点 ${stat.requirement_count || 0}，用户故事 ${stat.story_count || 0}`
}

const statLabel = (key) => {
  const map = {
    requirement_count: '需求数',
    functional_count: '功能性',
    non_functional_count: '非功能性',
    story_count: '故事数',
    event_count: '事件数',
    file_count: '文件数',
    symbol_count: '节点数',
    class_count: '类数',
    function_count: '函数数',
    edge_count: '关系数',
  }
  return map[key] || key
}

const StoryCards = defineComponent({
  props: { stories: { type: Array, default: () => [] } },
  setup(props) {
    return () => h('div', { class: 'story-cards' }, props.stories.map((story, index) => h('article', { class: 'story-card', key: index }, [
      h('p', { class: 'story-id' }, story.id || `US-${index + 1}`),
      h('div', { class: 'markdown', innerHTML: renderMarkdown(typeof story === 'string' ? story : (story.story || JSON.stringify(story, null, 2))) }),
      Array.isArray(story.acceptance_criteria) && story.acceptance_criteria.length
        ? h('div', { class: 'criteria' }, [
          h('strong', '验收标准'),
          h('ul', story.acceptance_criteria.map(item => h('li', { key: item }, item)))
        ])
        : null
    ])))
  }
})

const TextHistoryDetail = defineComponent({
  props: { detail: { type: Object, required: true } },
  setup(props) {
    const selectedIndex = ref(0)
    const subReqs = computed(() => props.detail.sub_requirements || [])
    const finalStories = computed(() => (props.detail.final_stories || []).map((item, index) => ({ id: `US-${index + 1}`, story: item })))
    const selectedStory = computed(() => finalStories.value[selectedIndex.value])
    return () => h('div', { class: 'detail-block' }, [
      h('section', { class: 'source-box' }, [h('strong', '原始文本需求'), h('p', props.detail.requirement || '')]),
      h('section', { class: 'two-col' }, [
        h('div', { class: 'mini-list' }, [
          h('h4', '拆分后的需求'),
          ...subReqs.value.map((item, index) => h('button', {
            class: { active: selectedIndex.value === index },
            onClick: () => { selectedIndex.value = index }
          }, [`R${index + 1} ${item}`]))
        ]),
        h('div', { class: 'mini-detail' }, selectedStory.value ? [
          h('h4', `用户故事 US-${selectedIndex.value + 1}`),
          h('div', { class: 'markdown', innerHTML: renderMarkdown(selectedStory.value.story) })
        ] : [h('p', '暂无用户故事')])
      ]),
      h('section', { class: 'event-list' }, [
        h('h4', '生成过程事件'),
        ...(props.detail.events || []).map((event, index) => h('div', { class: 'event-item', key: index }, [
          h('span', event.type),
          h('pre', JSON.stringify(event.data || event, null, 2))
        ]))
      ])
    ])
  }
})

const CodeHistoryDetail = defineComponent({
  props: { detail: { type: Object, required: true } },
  setup(props) {
    const selectedIndex = ref(0)
    const items = computed(() => props.detail.items || [])
    const selected = computed(() => items.value[selectedIndex.value])

    return () => {
      if (items.value.length) {
        return h('div', { class: 'detail-block' }, [
          h('section', { class: 'source-box' }, [
            h('strong', `代码逆向分析（${props.detail.language || 'unknown'}）`),
            h('p', props.detail.summary || ''),
            h('p', `拆分方式：${props.detail.split_mode || ''}；代码单元：${props.detail.statistics?.unit_count || 0}；引用关系：${props.detail.statistics?.edge_count || 0}`)
          ]),
          h('section', { class: 'two-col' }, [
            h('div', { class: 'mini-list' }, [
              h('h4', '代码单元'),
              ...items.value.map((item, index) => h('button', {
                class: { active: selectedIndex.value === index },
                onClick: () => { selectedIndex.value = index }
              }, [`${item.node?.id || item.node_id} ${item.node?.name || ''}`]))
            ]),
            h('div', { class: 'mini-detail' }, selected.value ? [
              h('h4', selected.value.requirement?.title || selected.value.node?.name || '代码单元'),
              h('p', selected.value.requirement?.description || ''),
              h('div', { class: 'markdown', innerHTML: renderMarkdown(selected.value.user_story?.story || '') }),
              Array.isArray(selected.value.user_story?.acceptance_criteria)
                ? h('ul', selected.value.user_story.acceptance_criteria.map(item => h('li', { key: item }, item)))
                : null,
              h('p', `引用：被引用 ${selected.value.incoming?.length || 0}，引用其他 ${selected.value.outgoing?.length || 0}`)
            ] : [h('p', '暂无用户故事')])
          ])
        ])
      }

      return h('div', { class: 'detail-block' }, [
        h('section', { class: 'source-box' }, [
          h('strong', `代码功能分析（${props.detail.language || 'unknown'}）`),
          h('p', props.detail.code_analysis || '')
        ]),
        h(TextHistoryDetail, { detail: { ...props.detail, requirement: props.detail.code_analysis || props.detail.summary || '' } }),
        h('details', { class: 'code-box' }, [
          h('summary', '查看原始代码'),
          h('pre', props.detail.code || props.detail.code_preview || '')
        ])
      ])
    }
  }
})

const DocumentHistoryDetail = defineComponent({
  props: { detail: { type: Object, required: true } },
  setup(props) {
    const selectedId = ref('')
    const graphRef = ref(null)
    let chart = null
    const requirements = computed(() => props.detail.requirements || [])
    const relations = computed(() => props.detail.relations || props.detail.graph?.links || [])
    const selectedReq = computed(() => requirements.value.find(item => item.id === selectedId.value) || requirements.value[0])
    watch(requirements, () => { selectedId.value = requirements.value[0]?.id || '' }, { immediate: true })

    const render = async () => {
      await nextTick()
      if (!graphRef.value || requirements.value.length === 0) return
      chart?.dispose()
      chart = echarts.init(graphRef.value)
      chart.setOption({
        tooltip: { trigger: 'item' },
        legend: [{ data: ['功能性需求', '非功能性需求'] }],
        series: [{
          type: 'graph', layout: 'force', roam: true, draggable: true,
          categories: [{ name: '功能性需求' }, { name: '非功能性需求' }],
          data: requirements.value.map(req => ({ id: req.id, name: `${req.id}\n${req.title}`, category: req.type === 'functional' ? 0 : 1, symbolSize: req.type === 'functional' ? 56 : 46 })),
          links: relations.value.map(rel => ({ source: rel.source, target: rel.target, name: rel.label || rel.name || rel.type })),
          edgeSymbol: ['none', 'arrow'], label: { show: true }, force: { repulsion: 380, edgeLength: 120 }
        }]
      })
      chart.on('click', params => { if (params.dataType === 'node') selectedId.value = params.data.id })
    }
    watch(() => props.detail.id, render, { immediate: true })
    onBeforeUnmount(() => chart?.dispose())

    return () => h('div', { class: 'document-history' }, [
      h('section', { class: 'two-col' }, [
        h('div', { class: 'mini-list' }, [
          h('h4', '需求列表'),
          ...requirements.value.map(req => h('button', { class: { active: selectedReq.value?.id === req.id }, onClick: () => { selectedId.value = req.id } }, [
            h('strong', `${req.id} ${req.title}`), h('span', req.type === 'functional' ? '功能性需求' : '非功能性需求')
          ]))
        ]),
        h('div', { class: 'mini-detail' }, selectedReq.value ? [
          h('h4', selectedReq.value.title),
          h('p', selectedReq.value.description),
          h(StoryCards, { stories: selectedReq.value.user_stories || [] }),
          selectedReq.value.non_functional_constraints?.length ? h('div', { class: 'criteria' }, [h('strong', '非功能性约束'), h('ul', selectedReq.value.non_functional_constraints.map(item => h('li', item)))]) : null
        ] : [h('p', '暂无需求')])
      ]),
      h('section', { class: 'chart-card' }, [h('h4', '需求关系图'), h('div', { ref: graphRef, class: 'history-chart' })])
    ])
  }
})

const ProjectHistoryDetail = defineComponent({
  props: { detail: { type: Object, required: true } },
  setup(props) {
    const selectedNodeId = ref('')
    const functionTreeRef = ref(null)
    const storyTreeRef = ref(null)
    const graphRef = ref(null)
    let fnChart = null
    let storyChart = null
    let graphChart = null
    const nodes = computed(() => props.detail.nodes || [])
    computed(() => props.detail.edges || []);
    const stories = computed(() => props.detail.stories || [])
    const selectedNode = computed(() => nodes.value.find(node => node.id === selectedNodeId.value) || nodes.value[0])
    const selectedStories = computed(() => stories.value.filter(story => story.node_id === selectedNode.value?.id))

    const selectNode = (id) => {
      const realId = String(id || '').replace(/^STORY-/, '')
      if (nodes.value.some(node => node.id === realId)) selectedNodeId.value = realId
    }

    const renderTree = (el, tree, isStory = false) => {
      if (!el || !tree) return null
      const chart = echarts.init(el)
      chart.setOption({
        tooltip: { trigger: 'item' },
        series: [{ type: 'tree', data: [tree], orient: 'LR', roam: true, top: 30, left: 20, right: 160, bottom: 30, symbolSize: 10, initialTreeDepth: 3, expandAndCollapse: true, label: { position: 'left', align: 'right' }, leaves: { label: { position: 'right', align: 'left' } } }]
      })
      chart.on('click', params => selectNode(isStory ? (params.data?.node_id || params.data?.id) : params.data?.id))
      return chart
    }

    const render = async () => {
      await nextTick()
      fnChart?.dispose(); storyChart?.dispose(); graphChart?.dispose()
      fnChart = renderTree(functionTreeRef.value, props.detail.function_tree, false)
      storyChart = renderTree(storyTreeRef.value, props.detail.story_tree, true)
      if (graphRef.value && props.detail.graph) {
        graphChart = echarts.init(graphRef.value)
        graphChart.setOption({
          tooltip: { trigger: 'item' },
          legend: [{ data: props.detail.graph.categories?.map(item => item.name) || [] }],
          series: [{ type: 'graph', layout: 'force', roam: true, draggable: true, data: props.detail.graph.nodes || [], links: props.detail.graph.links || [], categories: props.detail.graph.categories || [], label: { show: true, fontSize: 11 }, edgeSymbol: ['none', 'arrow'], force: { repulsion: 260, edgeLength: 120 } }]
        })
        graphChart.on('click', params => { if (params.dataType === 'node') selectNode(params.data?.id) })
      }
      selectedNodeId.value = nodes.value[0]?.id || ''
    }
    watch(() => props.detail.id, render, { immediate: true })
    onBeforeUnmount(() => { fnChart?.dispose(); storyChart?.dispose(); graphChart?.dispose() })

    return () => h('div', { class: 'project-history' }, [
      h('section', { class: 'project-charts' }, [
        h('div', { class: 'chart-card' }, [h('h4', '函数 / 类调用树'), h('div', { ref: functionTreeRef, class: 'history-chart' })]),
        h('div', { class: 'chart-card' }, [h('h4', '用户故事树'), h('div', { ref: storyTreeRef, class: 'history-chart' })])
      ]),
      h('section', { class: 'two-col' }, [
        h('div', { class: 'mini-list' }, [
          h('h4', '源码节点'),
          ...nodes.value.slice(0, 200).map(node => h('button', { class: { active: selectedNode.value?.id === node.id }, onClick: () => selectNode(node.id) }, [
            h('strong', node.name), h('span', `${node.type}｜${node.file}:${node.line}`)
          ]))
        ]),
        h('div', { class: 'mini-detail' }, selectedNode.value ? [
          h('h4', selectedNode.value.qualified_name || selectedNode.value.name),
          h('p', `${selectedNode.value.type} / ${selectedNode.value.language} / ${selectedNode.value.file}:${selectedNode.value.line}`),
          h(StoryCards, { stories: selectedStories.value }),
          h('details', { class: 'code-box', open: true }, [h('summary', '源码片段'), h('pre', selectedNode.value.code_snippet || '')])
        ] : [h('p', '暂无节点')])
      ]),
      h('section', { class: 'chart-card' }, [h('h4', '函数调用关系图'), h('div', { ref: graphRef, class: 'history-chart large' })])
    ])
  }
})

onMounted(async () => {
  await loadAllCounts()
  await loadList(activeType.value)
})
</script>

<style scoped>
.history-page .tabs button,
.history-page .tabs button strong,
.history-page .tabs button span,
.history-page .stats div,
.history-page .stats div strong,
.history-page .stats div span,
.history-page .history-item,
.history-page .history-item strong,
.history-page .history-item span,
.history-page .history-item p,
.history-page .panel-title,
.history-page .panel-title h3,
.history-page .panel-title span {
  color: #111827 !important;
}

/* 保留数字为蓝色，增强区分度 */
.history-page .tabs button > span,
.history-page .stats div strong {
  color: #2563eb !important;
}

/* 选中卡片时文字也保持黑色 */
.history-page .tabs button.active,
.history-page .tabs button.active strong,
.history-page .history-item.selected,
.history-page .history-item.selected strong,
.history-page .history-item.selected p {
  color: #111827 !important;
}
.page-header { display: flex; justify-content: space-between; gap: 20px; align-items: flex-start; margin-bottom: 18px; }
.eyebrow { margin: 0 0 6px; color: #2563eb; font-weight: 800; }
h2 { margin: 0 0 8px; font-size: 28px; }
.desc { color: #6b7280; margin: 0; line-height: 1.7; }
.refresh-btn, .tabs button, .history-item, .mini-list button { cursor: pointer; }
.refresh-btn { border: none; border-radius: 12px; background: #2563eb; color: white; padding: 11px 16px; font-weight: 700; }
.tabs { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }
.tabs button { background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 16px; text-align: left; box-shadow: 0 8px 20px rgba(15, 23, 42, .05); }
.tabs button.active { border-color: #2563eb; background: #eff6ff; }
.tabs strong { display: block; margin-bottom: 8px; }
.tabs span { color: #2563eb; font-weight: 800; }
.history-layout { display: grid; grid-template-columns: 360px 1fr; gap: 18px; align-items: start; }
.card, .error-card { background: white; border: 1px solid #e5e7eb; border-radius: 18px; box-shadow: 0 12px 30px rgba(15, 23, 42, .06); }
.error-card { padding: 14px 16px; color: #b91c1c; background: #fef2f2; margin-bottom: 18px; }
.history-list, .history-detail { padding: 18px; }
.history-list { position: sticky; top: 10px; max-height: calc(100vh - 140px); overflow: auto; }
.panel-title, .detail-header { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 14px; }
.panel-title h3, .detail-header h3 { margin: 0 0 8px; }
.panel-title span, .type-label { color: #64748b; font-size: 13px; }
.history-item { display: block; width: 100%; border: 1px solid #e5e7eb; background: #f9fafb; border-radius: 14px; padding: 12px; margin-bottom: 10px; text-align: left; }
.history-item.selected { border-color: #2563eb; background: #eff6ff; }
.item-main { display: flex; justify-content: space-between; gap: 10px; }
.item-main strong { font-size: 14px; line-height: 1.5; }
.item-main span { white-space: nowrap; font-size: 12px; color: #64748b; }
.history-item p { margin: 8px 0; color: #64748b; line-height: 1.5; font-size: 13px; }
.item-meta { display: flex; flex-wrap: wrap; gap: 6px; }
.item-meta em { font-style: normal; border-radius: 999px; background: #dbeafe; color: #1d4ed8; padding: 3px 8px; font-size: 12px; }
.empty { color: #94a3b8; text-align: center; padding: 34px 12px; }
.empty.large { padding: 120px 12px; }
.detail-header { padding-bottom: 14px; border-bottom: 1px solid #e5e7eb; }
.detail-header p { margin: 0; color: #64748b; line-height: 1.7; }
.stats { display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }
.stats div { min-width: 76px; border-radius: 12px; background: #f8fafc; padding: 10px; text-align: center; }
.stats strong { display: block; color: #2563eb; font-size: 20px; }
.stats span { color: #64748b; font-size: 12px; }
.source-box, .chart-card, .event-list { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 14px; padding: 14px; margin-bottom: 14px; }
.source-box p { white-space: pre-wrap; line-height: 1.8; color: #374151; }
.two-col { display: grid; grid-template-columns: 320px 1fr; gap: 14px; margin-bottom: 14px; }
.mini-list, .mini-detail { background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 14px; min-height: 180px; }
.mini-list { max-height: 620px; overflow: auto; }
.mini-list h4, .mini-detail h4, .chart-card h4, .event-list h4 { margin: 0 0 12px; }
.mini-list button { display: block; width: 100%; border: 1px solid #e5e7eb; background: #f9fafb; border-radius: 10px; padding: 10px; margin-bottom: 8px; text-align: left; line-height: 1.5; }
.mini-list button.active { border-color: #2563eb; background: #eff6ff; }
.mini-list button span { display: block; color: #64748b; font-size: 12px; margin-top: 4px; }
.markdown { line-height: 1.8; color: #374151; }
.story-cards { display: flex; flex-direction: column; gap: 10px; }
.story-card { border: 1px solid #e5e7eb; background: #ffffff; border-radius: 14px; padding: 14px; }
.story-id { color: #2563eb; font-weight: 800; margin: 0 0 8px; }
.criteria { margin-top: 10px; background: #f8fafc; border-radius: 10px; padding: 10px; }
.criteria ul { margin-bottom: 0; }
.event-item { border-left: 3px solid #bfdbfe; background: #fff; border-radius: 10px; padding: 10px; margin-bottom: 8px; }
.event-item span { display: inline-block; background: #dbeafe; color: #1d4ed8; border-radius: 999px; padding: 3px 9px; margin-bottom: 8px; font-size: 12px; }
.event-item pre, .code-box pre { white-space: pre-wrap; word-break: break-word; background: #0f172a; color: #e5e7eb; border-radius: 12px; padding: 14px; overflow: auto; }
.code-box { margin-top: 14px; }
.history-chart { height: 440px; }
.history-chart.large { height: 560px; }
.project-charts { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 1180px) { .history-layout, .two-col, .project-charts { grid-template-columns: 1fr; } .history-list { position: static; max-height: none; } .tabs { grid-template-columns: repeat(2, 1fr); } }
</style>