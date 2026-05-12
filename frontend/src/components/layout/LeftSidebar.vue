<template>
  <div>
    <div class="menu-group">
      <p class="group-title">生成入口</p>

      <div
          class="menu-item"
          :class="{ active: modelValue === 'chat' }"
          @click="change('chat')"
      >
        💬 文本需求生成
      </div>

      <div
          class="menu-item"
          :class="{ active: modelValue === 'codeStory' }"
          @click="change('codeStory')"
      >
        🧩 代码生成用户故事
      </div>

      <div
          class="menu-item"
          :class="{ active: modelValue === 'documentStory' }"
          @click="change('documentStory')"
      >
        📄 文档生成用户故事
      </div>

      <div
          class="menu-item"
          :class="{ active: modelValue === 'storyOptimization' }"
          @click="change('storyOptimization')"
      >
        ✨ 用户故事优化
      </div>
    </div>

    <div class="menu-group">
      <p class="group-title">系统分析</p>
      <div
          class="menu-item"
          :class="{ active: modelValue === 'agent' }"
          @click="change('agent')"
      >
        🤖 智能体
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: String
})
const emit = defineEmits(['update:modelValue'])

const change = (val) => {
  emit('update:modelValue', val)
}
</script>

<style scoped>
.menu-group {
  margin-bottom: 24px;
}

.group-title {
  color: #9ca3af;
  font-size: 12px;
  margin: 0 0 10px;
}

.menu-item {
  padding: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  border-radius: 8px;
  transition: 0.2s;
}

.menu-item:hover {
  background: #374151;
}

.menu-item.active {
  background: #3b82f6;
}
</style>
