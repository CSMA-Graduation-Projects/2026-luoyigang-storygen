<template>
  <div class="layout">

    <!-- 左 -->
    <aside class="left">
      <slot name="left" />
    </aside>

    <!-- 中 -->
    <main class="center">
      <slot />
    </main>

    <!-- 右 -->
    <aside class="right" v-if="$slots.right">
      <slot name="right" />
    </aside>

  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
}

/* 左侧 */
.left {
  width: 180px;
  background: #1f2937;
  color: white;
  padding: 20px;
}

/* 中间 */
.center {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f9fafb;
}

/* 右侧 */
.right {
  width: 220px;
  background: #f3f4f6;
  padding: 20px;
  border-left: 1px solid #e5e7eb;
}
</style>