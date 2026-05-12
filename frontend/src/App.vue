<template>
  <div class="layout">
    <!-- 左侧 -->
    <div class="sidebar-left">
      <div class="brand">
        <div class="logo">US</div>
        <div>
          <h1>用户故事系统</h1>
          <p>Multi-Agent</p>
        </div>
      </div>

      <div class="menu-group">
        <p class="group-title">生成入口</p>
        <router-link to="/" class="menu-item" active-class="active">
          <em>文本需求生成</em>
        </router-link>
        <router-link to="/code-story" class="menu-item" active-class="active">
          <em>代码生成用户故事</em>
        </router-link>
        <router-link to="/document-story" class="menu-item" active-class="active">
          <em>文档生成用户故事</em>
        </router-link>
        <router-link to="/project-story" class="menu-item" active-class="active">
          <em>项目源码生成用户故事</em>
        </router-link>
        <router-link to="/history-stories" class="menu-item" active-class="active">
          <em>历史需求</em>
        </router-link>
      </div>

      <div class="menu-group">
        <p class="group-title">用户故事优化</p>
        <router-link to="/story-optimization" class="menu-item" active-class="active">
          <em>用户故事优化</em>
        </router-link>
      </div>

      <div class="menu-group">
        <p class="group-title">系统分析</p>
        <router-link to="/agent" class="menu-item" active-class="active">
          <em>智能体</em>
        </router-link>
      </div>
    </div>

    <!-- 中间内容区 -->
    <div class="main">
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
}

/* 左 */
.sidebar-left {
  width: 240px;
  background: #111827;
  color: white;
  padding: 18px;
  box-sizing: border-box;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  padding-bottom: 18px;
  margin-bottom: 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.logo {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}

.brand h1 {
  margin: 0;
  font-size: 16px;
}

.brand p {
  margin: 4px 0 0;
  color: #9ca3af;
  font-size: 12px;
}

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
  border-radius: 10px;
  transition: 0.2s;
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: white;
}

.menu-item em {
  font-style: normal;
  font-size: 14px;
}

.menu-item:hover {
  background: #374151;
}

.menu-item.active {
  background: #2563eb;
}

/* 中 */
.main {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f9fafb;
}
</style>
<script setup lang="ts">
</script>