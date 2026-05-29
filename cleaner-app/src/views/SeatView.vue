<template>
  <div class="seat-view-container">
    <div class="header">
      <h1 class="title">保洁端 - 座位状态总览</h1>
      <button @click="loadSeats" class="refresh-button">刷新</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="error" class="error-box">
      {{ error }}
      <button @click="loadSeats" class="retry-button">重试</button>
    </div>

    <div v-else class="seat-groups">
      <div
        v-for="group in seatGroups"
        :key="group.group_id"
        class="seat-group"
      >
        <h2 class="group-name">{{ group.group_name }}</h2>
        <div class="seats-grid">
          <div
            v-for="seat in group.seats"
            :key="seat.seat_id"
            @click="handleSeatClick(seat)"
            :class="[
              'seat-card',
              seat.is_occupied ? 'occupied' : 'free',
              !seat.is_occupied ? 'disabled' : ''
            ]"
          >
            <div class="seat-number">{{ seat.seat_number }}</div>
            <div class="seat-status">
              {{ seat.is_occupied ? '占用' : '空闲' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 确认对话框 -->
    <div v-if="showConfirmDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-box" @click.stop>
        <h3 class="dialog-title">确认释放座位</h3>
        <p class="dialog-message">
          确定要将 <strong>{{ selectedSeat?.seat_number }} 号座位</strong> 标记为空闲吗？
        </p>
        <div class="dialog-actions">
          <button @click="closeDialog" class="cancel-button">取消</button>
          <button @click="confirmRelease" :disabled="releasing" class="confirm-button">
            {{ releasing ? '处理中...' : '确认' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from '../api/axios'

export default {
  name: 'SeatView',
  setup() {
    const seatGroups = ref([])
    const loading = ref(true)
    const error = ref('')
    const showConfirmDialog = ref(false)
    const selectedSeat = ref(null)
    const releasing = ref(false)
    let refreshTimer = null

    const loadSeats = async () => {
      try {
        loading.value = true
        error.value = ''
        const response = await axios.get('/seats')
        if (response.success) {
          seatGroups.value = response.data
        } else {
          error.value = response.error || '加载座位失败'
        }
      } catch (err) {
        error.value = err.error || '加载座位失败'
      } finally {
        loading.value = false
      }
    }

    const handleSeatClick = (seat) => {
      if (seat.is_occupied) {
        selectedSeat.value = seat
        showConfirmDialog.value = true
      }
    }

    const closeDialog = () => {
      showConfirmDialog.value = false
      selectedSeat.value = null
    }

    const confirmRelease = async () => {
      if (!selectedSeat.value) return
      try {
        releasing.value = true
        const response = await axios.put(`/seats/${selectedSeat.value.seat_id}/release`)
        if (response.success) {
          // 更新本地状态，避免重新请求
          for (const group of seatGroups.value) {
            const seat = group.seats.find(s => s.seat_id === selectedSeat.value.seat_id)
            if (seat) {
              seat.is_occupied = false
              break
            }
          }
          closeDialog()
        } else {
          alert(response.error || '操作失败')
        }
      } catch (err) {
        alert(err.error || '操作失败')
      } finally {
        releasing.value = false
      }
    }

    onMounted(() => {
      loadSeats()
      // 每15秒自动刷新
      refreshTimer = setInterval(loadSeats, 15000)
    })

    onUnmounted(() => {
      if (refreshTimer) clearInterval(refreshTimer)
    })

    return {
      seatGroups, loading, error,
      showConfirmDialog, selectedSeat, releasing,
      loadSeats, handleSeatClick, closeDialog, confirmRelease
    }
  }
}
</script>

<style scoped>
.seat-view-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  background: #000;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 28px;
  font-weight: bold;
  color: #FFF;
}

.refresh-button {
  padding: 10px 20px;
  background: #FFF;
  color: #000;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.refresh-button:hover { 
  background: #DDD;
}

.loading, .error-box {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error-box { color: #c33; }

.retry-button {
  margin-top: 15px;
  padding: 10px 20px;
  background: #000;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.retry-button:hover {
  background: #333;
}

.seat-groups {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.seat-group {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #DDD;
}

.group-name {
  font-size: 18px;
  font-weight: bold;
  color: #000;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #000;
}

.seats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
}

.seat-card {
  padding: 15px 10px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid #000;
}

.seat-card.occupied {
  background: #000;
  color: white;
}

.seat-card.occupied:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  background: #333;
}

.seat-card.free {
  background: #F5F5F5;
  color: #666;
  cursor: not-allowed;
  opacity: 0.75;
  border-color: #999;
}

.seat-number {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 4px;
}

.seat-status {
  font-size: 12px;
  font-weight: 500;
}

.dialog-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-box {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
}

.dialog-title {
  font-size: 20px;
  font-weight: bold;
  color: #000;
  margin-bottom: 15px;
}

.dialog-message {
  font-size: 16px;
  color: #333;
  margin-bottom: 25px;
  line-height: 1.5;
}

.dialog-message strong { color: #000; }

.dialog-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.cancel-button, .confirm-button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.cancel-button { 
  background: #F5F5F5; 
  color: #333;
  border: 1px solid #DDD;
}

.cancel-button:hover {
  background: #E0E0E0;
}

.confirm-button { 
  background: #000; 
  color: white; 
}

.confirm-button:hover {
  background: #333;
}

.confirm-button:disabled { 
  opacity: 0.6; 
  cursor: not-allowed; 
}
</style>
