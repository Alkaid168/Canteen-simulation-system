<template>
  <div class="prediction-view">
    <div class="page-header">
      <h1>预测管理</h1>
      <div class="header-actions">
        <button @click="runPrediction" :disabled="running" class="btn-run">
          {{ running ? '运行中...' : '手动触发预测' }}
        </button>
        <button @click="runTraining" :disabled="training" class="btn-train">
          {{ training ? '训练中...' : '手动触发训练' }}
        </button>
      </div>
    </div>

    <div v-if="message" :class="['message-box', messageType]">{{ message }}</div>

    <div class="section">
      <h2>今日菜品预测数量</h2>
      <p class="hint">可直接修改"调整数量"，保存后将作为今日实际库存</p>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="predictions.length === 0" class="empty">
        暂无预测数据，请先触发预测
      </div>

      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>菜品ID</th>
              <th>预测数量</th>
              <th>调整数量</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pred in predictions" :key="pred.id">
              <td>{{ pred.id }}</td>
              <td>{{ pred.dish_id }}</td>
              <td>{{ pred.predicted_quantity ?? '暂无' }}</td>
              <td>
                <input
                  v-model.number="adjustValues[pred.id]"
                  type="number"
                  min="0"
                  class="adjust-input"
                  :placeholder="pred.adjusted_quantity ?? pred.predicted_quantity ?? ''"
                />
              </td>
              <td>
                <button @click="saveAdjust(pred)" class="btn-save">保存</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="section">
      <h2>今日菜单库存</h2>
      <div v-if="loadingMenu" class="loading">加载中...</div>
      <div v-else-if="dailyMenu.length === 0" class="empty">暂无今日菜单数据</div>
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>菜品名称</th>
              <th>窗口ID</th>
              <th>当前库存</th>
              <th>是否售罄</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="menu in dailyMenu" :key="menu.id">
              <td>{{ menu.dish_name }}</td>
              <td>{{ menu.window_id }}</td>
              <td>{{ menu.stock }}</td>
              <td>
                <span :class="['status-badge', menu.is_sold_out ? 'inactive' : 'active']">
                  {{ menu.is_sold_out ? '已售罄' : '供应中' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import axios from '../api/axios'

export default {
  name: 'PredictionView',
  setup() {
    const predictions = ref([])
    const dailyMenu = ref([])
    const loading = ref(true)
    const loadingMenu = ref(true)
    const running = ref(false)
    const training = ref(false)
    const message = ref('')
    const messageType = ref('success')
    const adjustValues = reactive({})

    const showMessage = (msg, type = 'success') => {
      message.value = msg
      messageType.value = type
      setTimeout(() => { message.value = '' }, 3000)
    }

    const loadPredictions = async () => {
      try {
        loading.value = true
        const response = await axios.get('/admin/predictions')
        if (response.success) {
          predictions.value = response.data
          // 初始化调整值
          response.data.forEach(p => {
            adjustValues[p.id] = p.adjusted_quantity ?? p.predicted_quantity ?? 0
          })
        }
      } catch (error) {
        showMessage('加载预测数据失败', 'error')
      } finally {
        loading.value = false
      }
    }

    const loadDailyMenu = async () => {
      try {
        loadingMenu.value = true
        const response = await axios.get('/admin/daily-menu')
        if (response.success) dailyMenu.value = response.data
      } catch (error) {
        console.error('加载菜单失败')
      } finally {
        loadingMenu.value = false
      }
    }

    const saveAdjust = async (pred) => {
      const val = adjustValues[pred.id]
      if (val === null || val === undefined || val < 0) {
        showMessage('请输入有效的调整数量', 'error')
        return
      }
      try {
        const response = await axios.put(`/admin/prediction/${pred.id}/adjust`, {
          adjusted_quantity: val
        })
        if (response.success) {
          showMessage('保存成功，库存已同步更新')
          loadDailyMenu()
          loadPredictions()
        }
      } catch (error) {
        showMessage('保存失败: ' + (error.error || '未知错误'), 'error')
      }
    }

    const runPrediction = async () => {
      try {
        running.value = true
        const response = await axios.post('/admin/prediction/run')
        if (response.success) {
          showMessage('预测已触发，数据正在更新...')
          setTimeout(() => {
            loadPredictions()
            loadDailyMenu()
          }, 1000)
        }
      } catch (error) {
        showMessage('触发预测失败: ' + (error.error || '未知错误'), 'error')
      } finally {
        running.value = false
      }
    }

    const runTraining = async () => {
      try {
        training.value = true
        const response = await axios.post('/admin/prediction/train')
        if (response.success) {
          showMessage('训练任务已触发')
        }
      } catch (error) {
        showMessage('触发训练失败: ' + (error.error || '未知错误'), 'error')
      } finally {
        training.value = false
      }
    }

    onMounted(() => {
      loadPredictions()
      loadDailyMenu()
    })

    return {
      predictions, dailyMenu, loading, loadingMenu,
      running, training, message, messageType, adjustValues,
      saveAdjust, runPrediction, runTraining
    }
  }
}
</script>

<style scoped>
.prediction-view { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h1 { font-size: 24px; color: #000; font-weight: bold; }
.header-actions { display: flex; gap: 10px; }
.btn-run { padding: 10px 20px; background: #000; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600; }
.btn-run:hover { background: #333; }
.btn-train { padding: 10px 20px; background: #333; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600; }
.btn-train:hover { background: #555; }
.btn-run:disabled, .btn-train:disabled { opacity: 0.6; cursor: not-allowed; }
.message-box { padding: 12px 20px; border-radius: 5px; margin-bottom: 20px; font-size: 14px; border: 1px solid; }
.message-box.success { background: #F5F5F5; color: #000; border-color: #000; }
.message-box.error { background: #FEE; color: #C33; border-color: #FCC; }
.section { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid #DDD; }
.section h2 { font-size: 18px; color: #000; margin-bottom: 10px; font-weight: bold; }
.hint { font-size: 13px; color: #666; margin-bottom: 15px; }
.loading, .empty { text-align: center; padding: 30px; color: #999; }
.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #000; color: #FFF; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #000; }
.data-table td { padding: 12px; border-bottom: 1px solid #f0f0f0; color: #333; }
.adjust-input { width: 80px; padding: 6px; border: 2px solid #DDD; border-radius: 4px; text-align: center; }
.adjust-input:focus { outline: none; border-color: #000; }
.btn-save { padding: 6px 12px; background: #000; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 600; }
.btn-save:hover { background: #333; }
.status-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; border: 1px solid; }
.status-badge.active { background: #FFF; color: #000; border-color: #000; }
.status-badge.inactive { background: #F5F5F5; color: #666; border-color: #999; }
</style>
