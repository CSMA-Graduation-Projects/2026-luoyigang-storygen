<template>
  <div class="floating-tools">
    <!-- 跳转雷达图 -->
    <div class="tool-btn" @click="go('/analysis/radar')" title="查看雷达图分析">
      📊
    </div>
    <!-- 跳转趋势图 -->
    <div class="tool-btn" @click="go('/analysis/line')" title="查看优化趋势">
      📈
    </div>
    <!-- PDF -->
    <div class="tool-btn pdf" @click="download" title="导出PDF报告">
      📄
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router"
import { exportPDF } from "@/services/api"
import { useChat } from "@/composables/useChat"

const router = useRouter()

// 从 useChat 获取共享数据（单例模式）
const { radarData, rounds, scores, requirement, subRequirements, finalStories } = useChat()

const go = (path) => {
  console.log('跳转路径:', path)
  console.log('当前雷达图数据:', radarData.value)
  console.log('当前轮次:', rounds.value)
  console.log('当前分数:', scores.value)

  router.push(path)
}

const download = () => {
  console.log('=== PDF 导出调试信息 ===')
  console.log('requirement:', requirement.value)
  console.log('subRequirements:', subRequirements.value)
  console.log('finalStories:', finalStories.value)
  console.log('finalStories 长度:', finalStories.value?.length)

  // 检查是否有用户故事数据
  if (!finalStories.value || finalStories.value.length === 0) {
    alert("请先生成用户故事")
    return
  }

  // 构建导出数据
  const exportData = {
    requirement: requirement.value,
    sub_requirements: subRequirements.value,
    final_stories: finalStories.value
  }

  console.log('导出数据:', exportData)

  // 导出 PDF
  exportPDF(exportData)
}
</script>

<style scoped>
.floating-tools {
  position: fixed;
  right: 20px;
  bottom: 120px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 1000;
}

.tool-btn {
  width: 45px;
  height: 45px;
  background: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  font-size: 20px;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.tool-btn:hover {
  background: #2563eb;
  transform: scale(1.1);
}

/* PDF特殊颜色 */
.pdf {
  background: #10b981;
}

.pdf:hover {
  background: #059669;
}
</style>
