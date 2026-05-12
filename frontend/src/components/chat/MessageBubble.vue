<template>
  <div :class="['message-row', msg.role]">

    <div class="message">

      <!-- ⭐ 角色标签 -->
      <div class="role">{{ msg.type }}</div>

      <!-- ⭐ 内容（支持Markdown） -->
      <div class="content" v-html="msg.content"></div>

    </div>

  </div>
</template>

<script setup>
defineProps({
  msg: Object
})
</script>

<style scoped>
.message-row {
  display: flex;
  padding: 16px 0;
  justify-content: center;
}

.pm {
  justify-content: flex-end;
  word-break: break-word;
  align-items: center;
}

.qa, .arch, .invest, .final, .split {
  justify-content: flex-start;
  word-break: break-word;
  align-items: center;
}

/* 气泡 */
.message {
  width: fit-content;
  padding: 14px;
  border-radius: 12px;
  background: #f3f4f6;
  word-break: break-word;
}

/* 用户（PM） */
.pm .message {
  background: #3b82f6;
  color: white;
}

/* ⭐ 角色标题 */
.role {
  font-size: 12px;
  margin-bottom: 6px;
  opacity: 0.7;
}

/* Markdown样式 */
.content :deep(h1),
.content :deep(h2),
.content :deep(h3) {
  margin: 6px 0;
}

.content :deep(ul) {
  padding-left: 18px;
}

.content :deep(li) {
  margin: 4px 0;
}
</style>