<template>
  <div class="reports-view">
    <div class="page-header">
      <h1>运营报表</h1>
    </div>

    <!-- Tab 切换 -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="['tab-button', { active: activeTab === tab.key }]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 历史订单 -->
    <div v-if="activeTab === 'orders'" class="section">
      <div v-if="loadingOrders" class="loading">加载中...</div>
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>订单ID</th>
              <th>学号</th>
              <th>窗口</th>
              <th>状态</th>
              <th>下单时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.id">
              <td>{{ order.id }}</td>
              <td>{{ order.student_id || '-' }}</td>
              <td>{{ order.window_name || '-' }}</td>
              <td>
                <span :class="['status-badge', order.is_completed ? 'active' : 'pending']">
                  {{ order.is_completed ? '已取餐' : '待取餐' }}
                </span>
              </td>
              <td>{{ formatDate(order.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 每日订单量 -->
    <div v-if="activeTab === 'daily'" class="section">
      <div v-if="loadingDaily" class="loading">加载中...</div>
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>日期</th>
              <th>订单数量</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in dailyData" :key="row.date">
              <td>{{ row.date }}</td>
              <td>{{ row.count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 各窗口出餐量 -->
    <div v-if="activeTab === 'windows'" class="section">
      <div v-if="loadingWindows" class="loading">加载中...</div>
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>窗口</th>
              <th>已完成订单数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in windowsData" :key="row.window_id">
              <td>{{ row.window_name || `窗口${row.window_id}` }}</td>
              <td>{{ row.completed_orders }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 座位使用率 -->
    <div v-if="activeTab === 'seats'" class="section">
      <div v-if="loadingSeats" class="loading">加载中...</div>
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>座位组</th>
              <th>总座位数</th>
              <th>占用数</th>
              <th>使用率</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in seatsData" :key="row.group_id">
              <td>{{ row.group_name }}</td>
              <td>{{ row.total }}</td>
              <td>{{ row.occupied }}</td>
              <td>
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: row.total > 0 ? (row.occupied / row.total * 100) + '%' : '0%' }"
                  ></div>
                  <span class="progress-text">
                    {{ row.total > 0 ? Math.round(row.occupied / row.total * 100) : 0 }}%
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import axios from '../api/axios'

export default {
  name: 'ReportsView',
  setup() {
    const activeTab = ref('orders')
    const tabs = [
      { key: 'orders', label: '历史订单' },
      { key: 'daily', label: '每日订单量' },
      { key: 'windows', label: '窗口出餐量' },
      { key: 'seats', label: '座位使用率' }
    ]

    const orders = ref([])
    const dailyData = ref([])
    const windowsData = ref([])
    const seatsData = ref([])

    const loadingOrders = ref(false)
    const loadingDaily = ref(false)
    const loadingWindows = ref(false)
    const loadingSeats = ref(false)

    const loadOrders = async () => {
      try {
        loadingOrders.value = true
        const response = await axios.get('/admin/reports/orders')
        if (response.success) orders.value = response.data
      } catch (e) { console.error(e) } finally { loadingOrders.value = false }
    }

    const loadDaily = async () => {
      try {
        loadingDaily.value = true
        const response = await axios.get('/admin/reports/daily')
        if (response.success) dailyData.value = response.data
      } catch (e) { console.error(e) } finally { loadingDaily.value = false }
    }

    const loadWindows = async () => {
      try {
        loadingWindows.value = true
        const response = await axios.get('/admin/reports/windows')
        if (response.success) windowsData.value = response.data
      } catch (e) { console.error(e) } finally { loadingWindows.value = false }
    }

    const loadSeats = async () => {
      try {
        loadingSeats.value = true
        const response = await axios.get('/admin/reports/seats')
        if (response.success) seatsData.value = response.data
      } catch (e) { console.error(e) } finally { loadingSeats.value = false }
    }

    const formatDate = (dateStr) => new Date(dateStr).toLocaleString('zh-CN')

    watch(activeTab, (tab) => {
      if (tab === 'orders' && orders.value.length === 0) loadOrders()
      if (tab === 'daily' && dailyData.value.length === 0) loadDaily()
      if (tab === 'windows' && windowsData.value.length === 0) loadWindows()
      if (tab === 'seats' && seatsData.value.length === 0) loadSeats()
    })

    onMounted(() => loadOrders())

    return {
      activeTab, tabs,
      orders, dailyData, windowsData, seatsData,
      loadingOrders, loadingDaily, loadingWindows, loadingSeats,
      formatDate
    }
  }
}
</script>

<style scoped>
.reports-view { max-width: 1200px; }
.page-header { margin-bottom: 20px; }
.page-header h1 { font-size: 24px; color: #000; font-weight: bold; }
.tabs { display: flex; gap: 5px; margin-bottom: 20px; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid #DDD; }
.tab-button { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; background: #F5F5F5; color: #333; transition: all 0.3s; font-weight: 600; }
.tab-button.active { background: #000; color: white; }
.tab-button:hover:not(.active) { background: #E0E0E0; }
.section { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid #DDD; }
.loading { text-align: center; padding: 40px; color: #999; }
.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #000; color: #FFF; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #000; }
.data-table td { padding: 12px; border-bottom: 1px solid #f0f0f0; color: #333; }
.status-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; border: 1px solid; }
.status-badge.active { background: #FFF; color: #000; border-color: #000; }
.status-badge.pending { background: #F5F5F5; color: #666; border-color: #999; }
.progress-bar { display: flex; align-items: center; gap: 10px; }
.progress-fill { height: 12px; background: #000; border-radius: 6px; min-width: 4px; transition: width 0.3s; }
.progress-text { font-size: 13px; color: #333; white-space: nowrap; font-weight: 600; }
</style>
