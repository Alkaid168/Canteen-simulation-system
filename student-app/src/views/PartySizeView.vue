<template>
  <div class="party-size-container">
    <div class="party-size-box">
      <h1 class="title">请选择就餐人数</h1>
      
      <div class="size-options">
        <button
          v-for="size in [1, 2, 3, 4]"
          :key="size"
          @click="selectSize(size)"
          :class="['size-button', { active: selectedSize === size }]"
        >
          <span class="size-number">{{ size }}</span>
          <span class="size-text">人</span>
        </button>
      </div>
      
      <button
        @click="confirmSize"
        :disabled="!selectedSize"
        class="confirm-button"
      >
        确认并选择菜品
      </button>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'PartySizeView',
  setup() {
    const router = useRouter()
    const selectedSize = ref(null)

    const selectSize = (size) => {
      selectedSize.value = size
    }

    const confirmSize = () => {
      if (selectedSize.value) {
        // 将人数存储到sessionStorage，供后续使用
        sessionStorage.setItem('partySize', selectedSize.value)
        router.push('/menu')
      }
    }

    return {
      selectedSize,
      selectSize,
      confirmSize
    }
  }
}
</script>

<style scoped>
.party-size-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #F5F5F5;
}

.party-size-box {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  border: 2px solid #000;
}

.title {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  color: #000;
  margin-bottom: 40px;
}

.size-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.size-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  border: 2px solid #000;
  border-radius: 10px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.size-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  background: #F5F5F5;
}

.size-button.active {
  background: #000;
  color: white;
}

.size-number {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 5px;
}

.size-text {
  font-size: 18px;
}

.confirm-button {
  width: 100%;
  padding: 15px;
  background: #000;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.confirm-button:hover:not(:disabled) {
  background: #333;
}

.confirm-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
