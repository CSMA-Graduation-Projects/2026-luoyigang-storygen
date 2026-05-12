<template>
  <div class="input-box">

    <input
        v-model="text"
        placeholder="请输入需求..."
        @keyup.enter="submit"
    />

    <button @click="submit">生成</button>

  </div>
</template>

<script setup>
import { ref } from "vue"

const emit = defineEmits(["submit"])

const text = ref("")

const submit = () => {
  if (!text.value.trim()) return
  emit("submit", text.value)
  text.value = ""
}
</script>

<style scoped>
.input-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
</style>