<template>
  <div class="agent-page">
    <section class="page-header">
      <div>
        <p class="eyebrow">Agent Prompt Center</p>
        <h2>多智能体作用与提示词管理</h2>
        <p class="desc">展示每个智能体的作用、职责和当前系统提示词，可直接编辑并保存到后端。</p>
      </div>
      <button class="refresh-btn" @click="loadAgents" :disabled="loading">
        {{ loading ? '加载中...' : '刷新配置' }}
      </button>
    </section>

    <section v-if="errorMessage" class="message error">{{ errorMessage }}</section>
    <section v-if="successMessage" class="message success">{{ successMessage }}</section>

    <section class="agent-layout">
      <aside class="agent-list card">
        <div class="list-title">智能体列表</div>
        <button
          v-for="agent in agents"
          :key="agent.id"
          class="agent-card"
          :class="{ active: selectedAgentId === agent.id }"
          @click="selectAgent(agent.id)"
        >
          <strong>{{ agent.name }}</strong>
          <span>{{ agent.role }}</span>
        </button>
      </aside>

      <main v-if="selectedAgent" class="agent-detail card">
        <div class="detail-head">
          <div>
            <p class="eyebrow">{{ selectedAgent.id }}</p>
            <h3>{{ selectedAgent.name }}</h3>
            <p class="role-tag">{{ selectedAgent.role }}</p>
          </div>
          <div class="actions">
            <button class="secondary" @click="resetPrompt" :disabled="saving">恢复默认</button>
            <button class="primary" @click="savePrompt" :disabled="saving || !hasChanged">
              {{ saving ? '保存中...' : '保存提示词' }}
            </button>
          </div>
        </div>

        <section class="info-grid">
          <div class="info-block">
            <h4>智能体作用</h4>
            <p>{{ selectedAgent.description }}</p>
          </div>
          <div class="info-block">
            <h4>主要职责</h4>
            <ul>
              <li v-for="(feature, index) in selectedAgent.features" :key="index">{{ feature }}</li>
            </ul>
          </div>
        </section>

        <section class="prompt-panel">
          <div class="prompt-head">
            <h4>系统提示词</h4>
            <span>{{ promptText.length }} 字符</span>
          </div>
          <textarea
            v-model="promptText"
            class="prompt-editor"
            spellcheck="false"
            placeholder="请输入该智能体的系统提示词..."
          />
          <p class="hint">
            修改后点击“保存提示词”，后端后续创建该智能体时会读取新的提示词配置。
          </p>
        </section>
      </main>

      <main v-else class="empty card">
        <h3>请选择一个智能体</h3>
        <p>左侧选择 PM、QA、架构师、代码逆向等智能体后，可查看作用并编辑提示词。</p>
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { getAgentConfigs, resetAgentConfig, updateAgentConfig } from '@/services/api'

const agents = ref([])
const selectedAgentId = ref('')
const promptText = ref('')
const originalPrompt = ref('')
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const selectedAgent = computed(() => agents.value.find(agent => agent.id === selectedAgentId.value))
const hasChanged = computed(() => promptText.value !== originalPrompt.value)

const showSuccess = (message) => {
  successMessage.value = message
  window.setTimeout(() => {
    successMessage.value = ''
  }, 1800)
}

const loadAgents = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const data = await getAgentConfigs()
    agents.value = data.agents || []
    if (!selectedAgentId.value && agents.value.length) {
      selectedAgentId.value = agents.value[0].id
    }
    syncPrompt()
  } catch (error) {
    errorMessage.value = error.message || '智能体配置读取失败'
  } finally {
    loading.value = false
  }
}

const syncPrompt = () => {
  const agent = selectedAgent.value
  promptText.value = agent?.prompt || ''
  originalPrompt.value = agent?.prompt || ''
}

const selectAgent = (id) => {
  selectedAgentId.value = id
}

const savePrompt = async () => {
  if (!selectedAgent.value) return
  saving.value = true
  errorMessage.value = ''
  try {
    const updated = await updateAgentConfig(selectedAgent.value.id, {
      prompt: promptText.value
    })
    const index = agents.value.findIndex(item => item.id === updated.id)
    if (index !== -1) agents.value[index] = updated
    originalPrompt.value = updated.prompt || promptText.value
    showSuccess('提示词已保存，新的智能体调用将使用该配置。')
  } catch (error) {
    errorMessage.value = error.message || '提示词保存失败'
  } finally {
    saving.value = false
  }
}

const resetPrompt = async () => {
  if (!selectedAgent.value) return
  saving.value = true
  errorMessage.value = ''
  try {
    const updated = await resetAgentConfig(selectedAgent.value.id)
    const index = agents.value.findIndex(item => item.id === updated.id)
    if (index !== -1) agents.value[index] = updated
    promptText.value = updated.prompt || ''
    originalPrompt.value = updated.prompt || ''
    showSuccess('已恢复默认提示词。')
  } catch (error) {
    errorMessage.value = error.message || '恢复默认失败'
  } finally {
    saving.value = false
  }
}

watch(selectedAgentId, syncPrompt)
onMounted(loadAgents)
</script>

<style scoped>
.agent-page {
  padding: 24px;
  color: #1f2937;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #2563eb;
  font-weight: 700;
}

h2,
h3,
h4,
p {
  color: #111827;
}

h2 {
  margin: 0 0 8px;
  font-size: 26px;
}

.desc {
  margin: 0;
  color: #4b5563;
}

.agent-layout {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 18px;
}

.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.agent-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: calc(100vh - 150px);
  overflow: auto;
}

.list-title {
  font-weight: 800;
  color: #111827;
  margin-bottom: 6px;
}

.agent-card {
  width: 100%;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  border-radius: 14px;
  padding: 14px;
  text-align: left;
  cursor: pointer;
  transition: 0.2s;
}

.agent-card strong,
.agent-card span {
  display: block;
  color: #111827;
}

.agent-card span {
  margin-top: 6px;
  color: #4b5563;
  font-size: 13px;
}

.agent-card:hover,
.agent-card.active {
  border-color: #2563eb;
  background: #eff6ff;
  transform: translateY(-1px);
}

.agent-detail,
.empty {
  padding: 22px;
}

.detail-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 18px;
}

.detail-head h3 {
  margin: 0 0 8px;
  font-size: 22px;
}

.role-tag {
  display: inline-block;
  margin: 0;
  padding: 6px 12px;
  border-radius: 999px;
  color: #1d4ed8;
  background: #dbeafe;
  font-weight: 700;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

button {
  border: none;
  border-radius: 12px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.primary,
.refresh-btn {
  background: #2563eb;
  color: #ffffff;
}

.secondary {
  background: #f3f4f6;
  color: #111827;
  border: 1px solid #d1d5db;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}

.info-block {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 16px;
  background: #f9fafb;
}

.info-block h4,
.prompt-panel h4 {
  margin: 0 0 10px;
}

.info-block p,
.info-block li {
  color: #374151;
  line-height: 1.7;
}

.info-block ul {
  margin: 0;
  padding-left: 20px;
}

.prompt-panel {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 16px;
  background: #ffffff;
}

.prompt-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #6b7280;
  margin-bottom: 10px;
}

.prompt-editor {
  width: 100%;
  min-height: 430px;
  resize: vertical;
  box-sizing: border-box;
  border: 1px solid #d1d5db;
  border-radius: 14px;
  padding: 14px;
  color: #111827;
  background: #f9fafb;
  line-height: 1.65;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 14px;
  outline: none;
}

.prompt-editor:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.hint {
  margin: 10px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.message {
  padding: 12px 14px;
  border-radius: 14px;
  margin-bottom: 14px;
  font-weight: 700;
}

.message.error {
  color: #991b1b;
  background: #fee2e2;
  border: 1px solid #fecaca;
}

.message.success {
  color: #166534;
  background: #dcfce7;
  border: 1px solid #bbf7d0;
}

.empty {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.empty p {
  color: #6b7280;
}

@media (max-width: 920px) {
  .page-header,
  .detail-head {
    flex-direction: column;
  }

  .agent-layout,
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
