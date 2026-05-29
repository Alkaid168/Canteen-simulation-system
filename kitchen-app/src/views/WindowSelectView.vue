<template>
  <div class="window-select-container">
    <div class="header">
      <h1 class="title">后厨端 - 选择窗口</h1>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error-box">
      {{ error }}
      <button @click="loadWindows" class="retry-button">重试</button>
    </div>

    <div v-else class="window-grid">
      <div
        v-for="window in windows"
        :key="window.id"
        @click="selectWindow(window)"
        :class="['window-card', { offline: !window.is_online }]"
      >
        <div class="window-number">{{ window.window_number }}</div>
        <div class="window-name">{{ window.name }}</div>
        <div class="window-status">
          {{ window.is_online ? '在线' : '离线' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../api/axios'

export default {
  name: 'WindowSelectView',
  setup() {
    const router = useRouter()
    const windows = ref([])
    const loading = ref(true)
    const error = ref('')

    const loadWindows = async () => {
      try {
        loading.value = true
        error.value = ''
        const response = await axios.get('/windows')
        
        if (response.success) {
          windows.value = response.data
        } else {
          error.value = response.error || '加载窗口列表失败'
        }
      } catch (err) {
        error.value = err.error || '加载窗口列表失败'
      } finally {
        loading.value = false
      }
    }

    const selectWindow = (window) => {
      if (window.is_online) {
        router.push(`/orders/${window.id}`)
      }
    }

    onMounted(() => {
      loadWindows()
    })

    return {
      windows,
      loading,
      error,
      loadWindows,
      selectWindow
    }
  }
}
</script>

<style scoped>
.window-select-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  background: #000;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.title {
  font-size: 28px;
  font-weight: bold;
  color: #FFF;
  text-align: center;
}

.loading, .error-box {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error-box {
  color: #c33;
}

.retry-button {
  margin-top: 15px;
  padding: 10px 20px;
  background: #000;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.retry-button:hover {
  background: #333;
}

.window-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.window-card {
  background: white;
  padding: 40px 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
  border: 2px solid #000;
}

.window-card:hover:not(.offline) {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  background: #000;
  color: #FFF;
}

.window-card:hover:not(.offline) .window-number,
.window-card:hover:not(.offline) .window-name {
  color: #FFF;
}

.window-card.offline {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f5f5f5;
  border-color: #999;
}

.window-number {
  font-size: 48px;
  font-weight: bold;
  color: #000;
  margin-bottom: 10px;
}

.window-card.offline .window-number {
  color: #999;
}

.window-name {
  font-size: 18px;
  color: #333;
  margin-bottom: 10px;
}

.window-status {
  font-size: 14px;
  padding: 5px 15px;
  border-radius: 20px;
  display: inline-block;
}

.window-card:not(.offline) .window-status {
  background: #000;
  color: #FFF;
}

.window-card:hover:not(.offline) .window-status {
  background: #FFF;
  color: #000;
}

.window-card.offline .window-status {
  background: #DDD;
  color: #666;
}
</style>
