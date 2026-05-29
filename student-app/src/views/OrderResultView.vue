<template>
  <div class="result-container">
    <div class="result-box">
      <div class="success-icon">✓</div>
      <h1 class="title">订单提交成功！</h1>
      
      <div class="order-info">
        <div class="info-item">
          <span class="label">订单号：</span>
          <span class="value">{{ orderData.order_id }}</span>
        </div>
        
        <div class="info-item highlight">
          <span class="label">取餐窗口：</span>
          <span class="value window-number">{{ orderData.window_number }} 号窗口</span>
        </div>
        
        <div class="info-item highlight">
          <span class="label">就餐座位：</span>
          <span class="value seat-numbers">
            {{ orderData.seat_numbers.join('、') }} 号座位
          </span>
        </div>
      </div>

      <div class="instructions">
        <h3>温馨提示</h3>
        <ol>
          <li>请前往 <strong>{{ orderData.window_number }} 号窗口</strong> 取餐</li>
          <li>取餐后请前往 <strong>{{ orderData.seat_numbers.join('、') }} 号座位</strong> 就座</li>
          <li>用餐完毕后请将餐具放回回收处</li>
        </ol>
      </div>

      <button @click="backToLogin" class="back-button">
        返回登录页
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'OrderResultView',
  setup() {
    const router = useRouter()
    const orderData = ref({
      order_id: '',
      window_number: '',
      seat_numbers: [],
      status: ''
    })

    onMounted(() => {
      // 从sessionStorage获取订单结果
      const result = sessionStorage.getItem('orderResult')
      if (result) {
        orderData.value = JSON.parse(result)
      } else {
        // 如果没有订单数据，返回登录页
        router.push('/login')
      }
    })

    const backToLogin = () => {
      // 清除session数据
      sessionStorage.removeItem('partySize')
      sessionStorage.removeItem('orderResult')
      router.push('/login')
    }

    return {
      orderData,
      backToLogin
    }
  }
}
</script>

<style scoped>
.result-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #F5F5F5;
  padding: 20px;
}

.result-box {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  text-align: center;
  border: 2px solid #000;
}

.success-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: #000;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: bold;
}

.title {
  font-size: 28px;
  font-weight: bold;
  color: #000;
  margin-bottom: 30px;
}

.order-info {
  background: #F5F5F5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  text-align: left;
  border: 1px solid #DDD;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #DDD;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item.highlight {
  background: #000;
  color: #FFF;
  padding: 15px;
  margin: 10px -10px;
  border-radius: 5px;
  border-bottom: none;
}

.info-item.highlight .label,
.info-item.highlight .value {
  color: #FFF;
}

.label {
  color: #333;
  font-weight: 500;
}

.value {
  color: #000;
  font-weight: bold;
}

.window-number, .seat-numbers {
  color: #FFF;
  font-size: 20px;
}

.instructions {
  background: #F5F5F5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  text-align: left;
  border: 1px solid #DDD;
}

.instructions h3 {
  color: #000;
  margin-bottom: 15px;
  font-size: 18px;
  font-weight: bold;
}

.instructions ol {
  margin-left: 20px;
  color: #333;
}

.instructions li {
  margin-bottom: 10px;
  line-height: 1.6;
}

.instructions strong {
  color: #000;
  font-weight: bold;
}

.back-button {
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

.back-button:hover {
  background: #333;
}
</style>
