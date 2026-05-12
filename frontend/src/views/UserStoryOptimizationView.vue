<template>
  <div class="optimization-page">
    <section class="page-header">
      <div>
        <p class="eyebrow">用户故事质量提升</p>
        <h2>用户故事优化</h2>
        <p class="desc">
          上传 Word、PDF、Markdown 或 TXT 用户故事文档后，系统会自动拆分每条用户故事，逐个进行质量诊断与优化，并展示优化前后对比和提升点。
        </p>
      </div>
      <div class="actions" v-if="optimizationId">
        <button @click="exportResult('markdown')">导出 Markdown</button>
        <button @click="exportResult('docx')">导出 Word</button>
        <button @click="exportResult('json')">导出 JSON</button>
      </div>
    </section>

    <section class="upload-card card">
      <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
        <input
          ref="fileInput"
          type="file"
          accept=".docx,.pdf,.md,.markdown,.txt"
          hidden
          @change="handleFileChange"
        />
        <div class="upload-icon">✨</div>
        <h3>{{ file ? file.name : '上传用户故事文档' }}</h3>
        <p>支持 .docx / .pdf / .md / .markdown / .txt</p>
        <button class="primary-btn" @click="fileInput?.click()">选择文件</button>
        <button class="analyze-btn" :disabled="!file || loading" @click="optimizeDocument">
          {{ loading ? '优化中...' : '开始拆分并优化' }}
        </button>
      </div>
    </section>

    <section class="stats" v-if="items.length">
      <div class="stat-card">
        <strong>{{ items.length }}</strong>
        <span>用户故事数量</span>
      </div>
      <div class="stat-card">
        <strong>{{ improvementCount }}</strong>
        <span>提升点数量</span>
      </div>
      <div class="stat-card">
        <strong>{{ criteriaCount }}</strong>
        <span>验收标准数量</span>
      </div>
      <div class="stat-card">
        <strong>{{ selectedItem?.id || '-' }}</strong>
        <span>当前故事</span>
      </div>
    </section>

    <section class="content-grid" v-if="items.length">
      <div class="card story-list">
        <div class="panel-title">
          <h3>拆分后的用户故事</h3>
          <span>点击查看优化结果</span>
        </div>

        <div
          v-for="item in items"
          :key="item.id"
          class="story-item"
          :class="{ active: selectedItem?.id === item.id }"
          @click="selectItem(item)"
        >
          <div class="story-item-title">
            <span>{{ item.id }}</span>
            <strong>{{ item.title }}</strong>
          </div>
          <p>{{ preview(item.original_story) }}</p>
          <div class="mini-tags">
            <em>{{ item.improvement_points?.length || 0 }} 个提升点</em>
            <em>{{ item.acceptance_criteria?.length || 0 }} 条验收标准</em>
          </div>
        </div>
      </div>

      <div class="card compare-panel" v-if="selectedItem">
        <div class="panel-title">
          <h3>优化前后对比</h3>
          <span>{{ selectedItem.id }}</span>
        </div>

        <div class="compare-grid">
          <div class="compare-box before">
            <h4>优化前</h4>
            <pre>{{ selectedItem.original_story }}</pre>
          </div>
          <div class="compare-box after">
            <h4>优化后</h4>
            <pre>{{ selectedItem.optimized_story }}</pre>
          </div>
        </div>

        <div class="section-block">
          <h4>主要问题</h4>
          <p>{{ selectedItem.problem_summary }}</p>
        </div>

        <div class="section-block">
          <h4>提升点标注</h4>
          <div class="improvement-list">
            <div
              v-for="(point, index) in selectedItem.improvement_points || []"
              :key="index"
              class="improvement-item"
            >
              <strong>{{ point.dimension }}</strong>
              <p><b>优化前：</b>{{ point.before }}</p>
              <p><b>优化后：</b>{{ point.after }}</p>
              <p><b>提升原因：</b>{{ point.reason }}</p>
            </div>
          </div>
        </div>

        <div class="section-block">
          <h4>验收标准</h4>
          <ul class="criteria-list">
            <li v-for="(criteria, index) in selectedItem.acceptance_criteria || []" :key="index">
              {{ criteria }}
            </li>
          </ul>
        </div>

        <div class="section-block">
          <h4>INVEST 质量维度说明</h4>
          <div class="dimension-grid">
            <div v-for="(value, key) in selectedItem.quality_dimensions || {}" :key="key" class="dimension-card">
              <strong>{{ key }}</strong>
              <p>{{ value }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="card empty-card">
        请选择左侧某条用户故事查看优化详情
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { exportUserStoryOptimization, optimizeUserStoryDocument } from '@/services/api'

const fileInput = ref(null)
const file = ref(null)
const loading = ref(false)
const optimizationId = ref('')
const items = ref([])
const selectedItem = ref(null)

const improvementCount = computed(() => items.value.reduce((sum, item) => sum + (item.improvement_points?.length || 0), 0))
const criteriaCount = computed(() => items.value.reduce((sum, item) => sum + (item.acceptance_criteria?.length || 0), 0))

const handleFileChange = (event) => {
  file.value = event.target.files?.[0] || null
}

const handleDrop = (event) => {
  file.value = event.dataTransfer.files?.[0] || null
}

const normalizeResult = (data) => {
  optimizationId.value = data.optimization_id || data.id || ''
  items.value = data.items || []
  selectedItem.value = items.value[0] || null
}

const optimizeDocument = async () => {
  if (!file.value) return
  loading.value = true
  try {
    const data = await optimizeUserStoryDocument(file.value)
    normalizeResult(data)
  } catch (error) {
    alert(error.message || '用户故事优化失败，请检查后端服务是否启动')
  } finally {
    loading.value = false
  }
}

const selectItem = (item) => {
  selectedItem.value = item
}

const preview = (text = '') => {
  return text.length > 120 ? `${text.slice(0, 120)}...` : text
}

const exportResult = async (format) => {
  if (!optimizationId.value) return
  try {
    await exportUserStoryOptimization(optimizationId.value, format)
  } catch (error) {
    alert(error.message || '导出失败')
  }
}
</script>

<style scoped>
.optimization-page {
  max-width: 1480px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #2563eb;
  font-weight: 700;
  font-size: 13px;
}

h2 {
  margin: 0 0 8px;
  font-size: 28px;
  color: #111827;
}

.desc {
  margin: 0;
  color: #6b7280;
  line-height: 1.7;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.actions button,
.primary-btn,
.analyze-btn {
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 700;
}

.actions button {
  background: #111827;
  color: white;
}

.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
}

.upload-card {
  margin-bottom: 18px;
}

.upload-area {
  min-height: 210px;
  border: 2px dashed #bfdbfe;
  border-radius: 18px;
  margin: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: #eff6ff;
}

.upload-icon {
  font-size: 42px;
}

.upload-area h3 {
  margin: 0;
  color: #111827;
}

.upload-area p {
  margin: 0;
  color: #6b7280;
}

.primary-btn {
  background: #2563eb;
  color: white;
}

.analyze-btn {
  background: #16a34a;
  color: white;
}

.analyze-btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 16px;
}

.stat-card strong {
  display: block;
  font-size: 24px;
  color: #2563eb;
}

.stat-card span {
  color: #6b7280;
  font-size: 13px;
}

.content-grid {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 18px;
  align-items: start;
}

.story-list,
.compare-panel,
.empty-card {
  padding: 18px;
}

.panel-title {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.panel-title h3 {
  margin: 0;
  color: #111827;
}

.panel-title span {
  color: #6b7280;
  font-size: 13px;
}

.story-item {
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: 0.2s;
}

.story-item:hover,
.story-item.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.story-item-title {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.story-item-title span {
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 999px;
  padding: 3px 8px;
  font-size: 12px;
  font-weight: 800;
}

.story-item-title strong {
  color: #111827;
  font-size: 14px;
}

.story-item p {
  margin: 0 0 10px;
  color: #4b5563;
  line-height: 1.6;
  font-size: 13px;
}

.mini-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mini-tags em {
  font-style: normal;
  font-size: 12px;
  color: #047857;
  background: #d1fae5;
  border-radius: 999px;
  padding: 3px 8px;
}

.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.compare-box {
  border-radius: 16px;
  padding: 14px;
  border: 1px solid #e5e7eb;
}

.compare-box.before {
  background: #fff7ed;
}

.compare-box.after {
  background: #ecfdf5;
}

.compare-box h4,
.section-block h4 {
  margin: 0 0 10px;
  color: #111827;
}

.compare-box pre {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  color: #374151;
  line-height: 1.7;
  font-family: inherit;
}

.section-block {
  margin-top: 18px;
  border-top: 1px solid #e5e7eb;
  padding-top: 16px;
}

.section-block p {
  color: #4b5563;
  line-height: 1.7;
}

.improvement-list {
  display: grid;
  gap: 12px;
}

.improvement-item {
  border: 1px solid #bfdbfe;
  background: #eff6ff;
  border-radius: 14px;
  padding: 12px;
}

.improvement-item strong {
  color: #1d4ed8;
}

.improvement-item p {
  margin: 6px 0 0;
}

.criteria-list {
  margin: 0;
  padding-left: 20px;
  color: #374151;
  line-height: 1.8;
}

.dimension-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.dimension-card {
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 12px;
  background: #f9fafb;
}

.dimension-card strong {
  color: #111827;
}

.dimension-card p {
  margin: 6px 0 0;
  color: #4b5563;
  font-size: 13px;
}

.empty-card {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

@media (max-width: 1100px) {
  .content-grid,
  .compare-grid,
  .dimension-grid,
  .stats {
    grid-template-columns: 1fr;
  }
}
</style>
