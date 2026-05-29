<template>
  <div class="menu-container">
    <div class="menu-header">
      <h1 class="title">今日菜单</h1>
      <div class="cart-summary">
        <span>已选 {{ totalItems }} 份</span>
        <span class="total-price">¥{{ totalPrice.toFixed(2) }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error-box">
      {{ error }}
    </div>

    <div v-else class="menu-grid">
      <div
        v-for="dish in menuItems"
        :key="dish.dish_id"
        :class="['dish-card', { 'sold-out': dish.is_sold_out || dish.stock === 0 }]"
      >
        <div class="card-image">
          <div class="image-container">
            <img 
              :src="getDishImage(dish)"
              :alt="dish.name"
              class="dish-image"
              @error="handleImageError"
            />
          </div>
        </div>
        
        <div class="card-content">
          <h3 class="dish-name">{{ dish.name }}</h3>
          <div class="dish-meta">
            <span class="dish-price">¥{{ dish.price.toFixed(2) }}</span>
            <span class="dish-stock">剩余: {{ dish.stock }}</span>
          </div>
          
          <div class="card-actions">
            <button
              @click="decreaseQuantity(dish)"
              :disabled="!cart[dish.dish_id] || cart[dish.dish_id] === 0"
              class="action-button minus"
            >
              -
            </button>
            <span class="quantity-display">{{ cart[dish.dish_id] || 0 }}</span>
            <button
              @click="increaseQuantity(dish)"
              :disabled="dish.is_sold_out || dish.stock === 0 || (cart[dish.dish_id] || 0) >= dish.stock"
              class="action-button plus"
            >
              +
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && !error" class="footer">
      <button
        @click="submitOrder"
        :disabled="totalItems === 0 || submitting"
        class="submit-button"
      >
        {{ submitting ? '提交中...' : `提交订单 (¥${totalPrice.toFixed(2)})` }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../api/axios'

export default {
  name: 'MenuView',
  setup() {
    const router = useRouter()
    const menuItems = ref([])
    const cart = ref({})
    const loading = ref(true)
    const error = ref('')
    const submitting = ref(false)

    const totalItems = computed(() => {
      return Object.values(cart.value).reduce((sum, qty) => sum + qty, 0)
    })

    const totalPrice = computed(() => {
      return menuItems.value.reduce((sum, dish) => {
        const qty = cart.value[dish.dish_id] || 0
        return sum + (dish.price * qty)
      }, 0)
    })

    const loadMenu = async () => {
      try {
        loading.value = true
        const response = await axios.get('/menu/today')
        
        if (response.success) {
          menuItems.value = response.data
        } else {
          error.value = response.error || '加载菜单失败'
        }
      } catch (err) {
        error.value = err.error || '加载菜单失败'
      } finally {
        loading.value = false
      }
    }

    const increaseQuantity = (dish) => {
      const currentQty = cart.value[dish.dish_id] || 0
      if (currentQty < dish.stock) {
        cart.value[dish.dish_id] = currentQty + 1
      }
    }

    const decreaseQuantity = (dish) => {
      const currentQty = cart.value[dish.dish_id] || 0
      if (currentQty > 0) {
        cart.value[dish.dish_id] = currentQty - 1
      }
    }

    const submitOrder = async () => {
      const partySize = parseInt(sessionStorage.getItem('partySize'))
      if (!partySize) {
        error.value = '请先选择就餐人数'
        router.push('/party-size')
        return
      }

      // 构建订单项
      const items = []
      for (const [dishId, quantity] of Object.entries(cart.value)) {
        if (quantity > 0) {
          items.push({
            dish_id: parseInt(dishId),
            quantity: quantity
          })
        }
      }

      if (items.length === 0) {
        error.value = '请至少选择一份菜品'
        return
      }

      try {
        submitting.value = true
        const response = await axios.post('/orders', {
          party_size: partySize,
          items: items
        })

        if (response.success) {
          // 订单提交成功，跳转到结果页
          sessionStorage.setItem('orderResult', JSON.stringify(response.data))
          router.push('/order-result')
        } else {
          error.value = response.error || '提交订单失败'
        }
      } catch (err) {
        error.value = err.error || '提交订单失败'
      } finally {
        submitting.value = false
      }
    }

    // 获取菜品图片
    const getDishImage = (dish) => {
      if (dish.image_url) {
        return dish.image_url
      }
      // 默认菜品图片（根据菜品名称选择不同的占位图）
      const defaultImages = {
        '红烧肉盖饭': 'https://images.unsplash.com/photo-1547592166-23ac550943e8?w=400&h=300&fit=crop',
        '番茄鸡蛋面': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop',
        '辣椒炒肉拌面': 'https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400&h=300&fit=crop',
        '麻辣烫': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop',
        '蒸饺': 'https://images.unsplash.com/photo-1586190848861-99aa042a0d0e?w=400&h=300&fit=crop'
      }
      return defaultImages[dish.name] || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop'
    }

    // 图片加载失败处理
    const handleImageError = (event) => {
      event.target.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop'
    }

    onMounted(() => {
      loadMenu()
    })

    return {
      menuItems,
      cart,
      loading,
      error,
      submitting,
      totalItems,
      totalPrice,
      increaseQuantity,
      decreaseQuantity,
      submitOrder,
      getDishImage,
      handleImageError
    }
  }
}
</script>

<style scoped>
.menu-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 100px;
  background: #f5f5f5;
  min-height: 100vh;
}

.menu-header {
  background: #000;
  color: #fff;
  padding: 25px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.title {
  font-size: 28px;
  font-weight: bold;
  color: #fff;
  margin-bottom: 15px;
  text-align: center;
  letter-spacing: 2px;
}

.cart-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  color: #ddd;
  padding: 15px 0;
  border-top: 1px solid #333;
  margin-top: 10px;
}

.total-price {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
}

.loading, .error-box {
  text-align: center;
  padding: 60px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  font-size: 18px;
}

.error-box {
  color: #dc143c;
  background: #fff5f5;
  border: 1px solid #dc143c;
}

/* 网格布局 */
.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.dish-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
}

.dish-card:hover:not(.sold-out) {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border-color: #000;
}

.dish-card.sold-out {
  opacity: 0.5;
  filter: grayscale(1);
}

.dish-card.sold-out::after {
  content: "已售罄";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-15deg);
  background: rgba(0, 0, 0, 0.85);
  color: white;
  padding: 10px 25px;
  border-radius: 4px;
  font-size: 20px;
  font-weight: bold;
  z-index: 2;
  letter-spacing: 3px;
}

.card-image {
  position: relative;
  height: 200px;
  overflow: hidden;
  background: #f5f5f5;
}

.image-container {
  width: 100%;
  height: 100%;
}

.dish-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.dish-card:hover .dish-image {
  transform: scale(1.08);
}

.card-content {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.dish-name {
  font-size: 20px;
  font-weight: bold;
  color: #000;
  margin-bottom: 12px;
  line-height: 1.3;
}

.dish-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dish-price {
  font-size: 24px;
  font-weight: bold;
  color: #000;
}

.dish-stock {
  font-size: 13px;
  color: #666;
  background: #f5f5f5;
  padding: 5px 12px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.card-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.action-button {
  width: 42px;
  height: 42px;
  border: 2px solid #000;
  border-radius: 4px;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  color: #000;
}

.action-button.plus:hover:not(:disabled) {
  background: #000;
  color: #fff;
}

.action-button.minus:hover:not(:disabled) {
  background: #000;
  color: #fff;
}

.action-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  border-color: #ccc;
}

.quantity-display {
  font-size: 22px;
  font-weight: bold;
  min-width: 50px;
  text-align: center;
  color: #000;
}

.footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #000;
  padding: 20px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
  z-index: 100;
}

.submit-button {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  display: block;
  padding: 18px;
  background: #fff;
  color: #000;
  border: 2px solid #fff;
  border-radius: 4px;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  letter-spacing: 2px;
}

.submit-button:hover:not(:disabled) {
  background: #000;
  color: #fff;
  border-color: #fff;
}

.submit-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .menu-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
  
  .title {
    font-size: 24px;
  }
  
  .card-image {
    height: 180px;
  }
}

@media (max-width: 480px) {
  .menu-grid {
    grid-template-columns: 1fr;
  }
  
  .menu-container {
    padding: 15px;
    padding-bottom: 100px;
  }
}
</style>
