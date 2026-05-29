<template>
  <div class="order-list-container">
    <div class="header">
      <button @click="goBack" class="back-button">← 返回</button>
      <h1 class="title">{{ windowInfo.name }} - 待取餐订单</h1>
      <button @click="loadOrders" class="refresh-button">刷新</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error-box">
      {{ error }}
    </div>

    <div v-else>
      <div v-if="orders.length === 0" class="empty-state">
        <p>暂无待取餐订单</p>
      </div>

      <div v-else class="orders-list">
        <div
          v-for="order in orders"
          :key="order.order_id"
          class="order-card"
        >
          <div class="order-header">
            <span class="order-id">订单 #{{ order.order_id }}</span>
            <span class="order-time">{{ formatTime(order.created_at) }}</span>
          </div>

          <div class="order-dishes">
            <div
              v-for="(dish, index) in order.items"
              :key="index"
              class="dish-item"
            >
              <span class="dish-name">{{ dish.dish_name }}</span>
              <span class="dish-quantity">x{{ dish.quantity }}</span>
            </div>
          </div>

          <button
            @click="completeOrder(order.order_id)"
            :disabled="completing[order.order_id]"
            class="complete-button"
          >
            {{ completing[order.order_id] ? '处理中...' : '出餐完成' }}
          </button>
        </div>
      </div>

      <div class="prediction-section">
        <h2 class="section-title">今日预计出餐量</h2>
        <div v-if="loadingPrediction" class="loading-small">加载中...</div>
        <div v-else-if="predictions.length === 0" class="empty-prediction">
          暂无预测数据
        </div>
        <div v-else class="prediction-list">
          <div
            v-for="pred in predictions"
            :key="pred.dish_id"
            class="prediction-item"
          >
            <span class="pred-dish-name">{{ pred.dish_name }}</span>
            <span class="pred-quantity">{{ pred.effective_quantity || pred.predicted_quantity || 0 }} 份</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from '../api/axios'

export default {
  name: 'OrderListView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const windowId = route.params.windowId

    const windowInfo = ref({ name: '', window_number: '' })
    const orders = ref([])
    const predictions = ref([])  // 数组格式，后端返回扁平列表
    const loading = ref(true)
    const loadingPrediction = ref(true)
    const error = ref('')
    const completing = reactive({})

    const loadOrders = async () => {
      try {
        loading.value = true
        error.value = ''
        const response = await axios.get(`/kitchen/orders?window_id=${windowId}`)
        
        if (response.success) {
          orders.value = response.data
        } else {
          error.value = response.error || '加载订单失败'
        }
      } catch (err) {
        error.value = err.error || '加载订单失败'
      } finally {
        loading.value = false
      }
    }

    const loadPredictions = async () => {
      try {
        loadingPrediction.value = true
        const response = await axios.get('/kitchen/prediction')
        
        if (response.success) {
          predictions.value = response.data  // 直接使用返回的对象
        }
      } catch (err) {
        console.error('加载预测数据失败:', err)
      } finally {
        loadingPrediction.value = false
      }
    }

    const getMealTypeName = (mealType) => {
      const names = { 'breakfast': '早餐', 'lunch': '午餐', 'dinner': '晚餐' }
      return names[mealType] || mealType
    }

    const loadWindowInfo = async () => {
      try {
        const response = await axios.get('/windows')
        if (response.success) {
          const window = response.data.find(w => w.id === parseInt(windowId))
          if (window) {
            windowInfo.value = window
          }
        }
      } catch (err) {
        console.error('加载窗口信息失败:', err)
      }
    }

    const completeOrder = async (orderId) => {
      try {
        completing[orderId] = true
        const response = await axios.put(`/kitchen/orders/${orderId}/complete`)
        
        if (response.success) {
          // 从列表中移除已完成的订单
          orders.value = orders.value.filter(o => o.order_id !== orderId)
        } else {
          alert(response.error || '操作失败')
        }
      } catch (err) {
        alert(err.error || '操作失败')
      } finally {
        completing[orderId] = false
      }
    }

    const formatTime = (timeStr) => {
      const date = new Date(timeStr)
      return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
      })
    }

    const goBack = () => {
      router.push('/')
    }

    onMounted(() => {
      loadWindowInfo()
      loadOrders()
      loadPredictions()
      
      // 每30秒自动刷新订单列表
      const interval = setInterval(loadOrders, 30000)
      
      // 组件卸载时清除定时器
      return () => clearInterval(interval)
    })

    return {
      windowInfo,
      orders,
      predictions,
      loading,
      loadingPrediction,
      error,
      completing,
      loadOrders,
      completeOrder,
      formatTime,
      goBack,
      getMealTypeName
    }
  }
}
</script>

<style scoped>
.order-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.header {
  background: #000;
  color: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.back-button, .refresh-button {
  padding: 10px 20px;
  background: #fff;
  color: #000;
  border: 2px solid #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.3s;
}

.back-button:hover, .refresh-button:hover {
  background: #000;
  color: #fff;
  border-color: #fff;
}

.title {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
  letter-spacing: 1px;
}

.loading, .error-box {
  text-align: center;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error-box {
  color: #dc143c;
  border: 1px solid #dc143c;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-state p {
  font-size: 18px;
  color: #666;
}

.orders-list {
  display: grid;
  gap: 15px;
  margin-bottom: 30px;
}

.order-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.order-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #000;
}

.order-id {
  font-size: 18px;
  font-weight: bold;
  color: #000;
}

.order-time {
  font-size: 14px;
  color: #666;
}

.order-dishes {
  margin-bottom: 15px;
}

.dish-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.dish-item:last-child {
  border-bottom: none;
}

.dish-name {
  font-size: 16px;
  color: #333;
}

.dish-quantity {
  font-size: 16px;
  font-weight: bold;
  color: #000;
}

.complete-button {
  width: 100%;
  padding: 12px;
  background: #000;
  color: #fff;
  border: 2px solid #000;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.complete-button:hover:not(:disabled) {
  background: #fff;
  color: #000;
}

.complete-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.prediction-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #000;
  margin-bottom: 20px;
  letter-spacing: 1px;
}

.loading-small {
  text-align: center;
  padding: 20px;
  color: #666;
}

.empty-prediction {
  text-align: center;
  padding: 20px;
  color: #999;
}

.prediction-container {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.meal-section {
  border: 2px solid #000;
  border-radius: 8px;
  padding: 15px;
  background: #f9f9f9;
}

.meal-title {
  font-size: 18px;
  font-weight: bold;
  color: #000;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #000;
  letter-spacing: 1px;
}

.prediction-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.prediction-item {
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.pred-dish-name {
  font-size: 14px;
  color: #333;
}

.pred-quantity {
  font-size: 16px;
  font-weight: bold;
  color: #000;
}
</style>
