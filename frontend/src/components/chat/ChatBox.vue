<template>
  <div class="chat-box" ref="chatBox">
    <div v-for="(msg, index) in messages" :key="index"
         :class="['bubble', msg.role]">

      <div class="title">{{ msg.type }}</div>
      <div class="content" v-html="msg.content"></div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from "vue"

const props = defineProps({
  messages: Array
})

const box = ref(null)

watch(
    () => props.messages,
    async () => {
      await nextTick()
      box.value.scrollTop = box.value.scrollHeight
    },
    {deep: true}
)
</script>

<style scoped>
.chat-box {
  padding: 20px 0;
}

/* 一行 */
.message-row {
  display: flex;
  padding: 20px 0;
  justify-content: center;
}

/* 用户（右） */
.pm {
  justify-content: center;
}

/* AI（左） */
.qa, .arch, .invest, .final {
  justify-content: center;
}

/* 气泡 */
.message {
  padding: 10px;
  border-radius: 12px;
  background: #f3f4f6;
  justify-content: center;
  word-break: break-word;
}

/* 用户气泡 */
.pm .message {
  background: #3b82f6;
  color: white;
}
</style>