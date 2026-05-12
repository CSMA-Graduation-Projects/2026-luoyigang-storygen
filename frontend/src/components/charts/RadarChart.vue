<template>
  <div class="floating-tools">

    <div class="tool-btn" @click="scrollTo('radar')">
      📊
    </div>

    <div class="tool-btn" @click="scrollTo('line')">
      📈
    </div>

  </div>
</template>

<script setup>
const scrollTo = (id) => {
  document.getElementById(id)?.scrollIntoView({
    behavior: "smooth"
  })
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
  font-size: 18px;
}

.tool-btn:hover {
  background: #2563eb;
}
</style>