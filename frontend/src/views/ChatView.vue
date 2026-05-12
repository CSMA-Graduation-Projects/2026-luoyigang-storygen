<template>
  <div class="chatgpt-layout">
    <!--聊天内容-->
    <div class="chat-container">
      <ChatBox :messages="messages" />
    </div>
    <!--输入框（浮动）-->
    <div class="input-fixed">
      <InputBox @submit="start" />
    </div>
    <!--使用右侧组件-->
    <RightSidebar  :radarData="radarData" :rounds="rounds" :scores="scores" :requirement="requirement" :subRequirements="subRequirements" :finalStories="finalStories" />
  </div>
</template>

<script setup>
import { useChat } from "@/composables/useChat"
import ChatBox from "@/components/chat/ChatBox.vue"
import InputBox from "@/components/chat/InputBox.vue"
import RightSidebar from "@/components/layout/RightSidebar.vue";

// eslint-disable-next-line no-unused-vars
const {
  messages,
  radarData,
  rounds,
  scores,
  start,
  requirement,
  subRequirements,
  finalStories
} = useChat()
</script>

<style scoped>
.chatgpt-layout {
  position: relative;
  height: 100%;
}

/* 聊天区域（居中） */
.chat-container {
  max-width: 70%;
  margin: 0 auto;
  padding-bottom: 120px; /* 留给输入框 */
}

/* 输入框固定底部 */
.input-fixed {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 50%;
  height: 60px;
  background: white;
  padding: 10px;
  border-radius: 30px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.5);
}

/* 图表滚动定位 */
#radar, #line {
  scroll-margin-top: 80px;
}
</style>