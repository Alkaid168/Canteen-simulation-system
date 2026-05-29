<template>
  <div class="seats-view">
    <div class="page-header">
      <h1>座位管理</h1>
      <button @click="showAddDialog = true" class="add-button">+ 添加座位</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>座位编号</th>
            <th>座位组ID</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="seat in seats" :key="seat.id">
            <td>{{ seat.id }}</td>
            <td>{{ seat.seat_number }}</td>
            <td>{{ seat.group_id }}</td>
            <td>
              <span :class="['status-badge', !seat.is_occupied ? 'active' : 'inactive']">
                {{ !seat.is_occupied ? '空闲' : '占用' }}
              </span>
            </td>
            <td>
              <button @click="editSeat(seat)" class="btn-edit">编辑</button>
              <button @click="deleteSeat(seat.id)" class="btn-delete">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showAddDialog || showEditDialog" class="dialog-overlay" @click="closeDialogs">
      <div class="dialog-box" @click.stop>
        <h3>{{ showEditDialog ? '编辑座位' : '添加座位' }}</h3>
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label>座位编号</label>
            <input v-model="formData.seat_number" required />
          </div>
          <div class="form-group">
            <label>座位组ID</label>
            <input v-model.number="formData.group_id" type="number" required />
          </div>
          <div class="form-group" v-if="showEditDialog">
            <label>状态</label>
            <select v-model="formData.is_occupied">
              <option :value="false">空闲</option>
              <option :value="true">占用</option>
            </select>
          </div>
          <div class="dialog-actions">
            <button type="button" @click="closeDialogs" class="btn-cancel">取消</button>
            <button type="submit" class="btn-submit">提交</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from '../api/axios'

export default {
  name: 'SeatsView',
  setup() {
    const seats = ref([])
    const loading = ref(true)
    const showAddDialog = ref(false)
    const showEditDialog = ref(false)
    const formData = ref({ seat_number: '', group_id: 1, is_occupied: false })
    const editingId = ref(null)

    const loadSeats = async () => {
      try {
        loading.value = true
        const response = await axios.get('/admin/seats')
        if (response.success) seats.value = response.data
      } catch (error) {
        alert('加载失败')
      } finally {
        loading.value = false
      }
    }

    const editSeat = (seat) => {
      formData.value = { ...seat }
      editingId.value = seat.id
      showEditDialog.value = true
    }

    const deleteSeat = async (id) => {
      if (!confirm('确定要删除吗？')) return
      try {
        await axios.delete(`/admin/seats/${id}`)
        loadSeats()
      } catch (error) {
        alert('删除失败')
      }
    }

    const submitForm = async () => {
      try {
        if (showEditDialog.value) {
          await axios.put(`/admin/seats/${editingId.value}`, formData.value)
        } else {
          await axios.post('/admin/seats', formData.value)
        }
        closeDialogs()
        loadSeats()
      } catch (error) {
        alert('操作失败')
      }
    }

    const closeDialogs = () => {
      showAddDialog.value = false
      showEditDialog.value = false
      formData.value = { seat_number: '', group_id: 1, is_occupied: false }
      editingId.value = null
    }

    onMounted(loadSeats)

    return { seats, loading, showAddDialog, showEditDialog, formData, editSeat, deleteSeat, submitForm, closeDialogs }
  }
}
</script>

<style scoped>
.seats-view { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h1 { font-size: 24px; color: #000; font-weight: bold; }
.add-button { padding: 10px 20px; background: #000; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600; }
.add-button:hover { background: #333; }
.loading { text-align: center; padding: 40px; }
.table-container { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid #DDD; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #000; color: #FFF; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #000; }
.data-table td { padding: 12px; border-bottom: 1px solid #f0f0f0; color: #333; }
.status-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; border: 1px solid; }
.status-badge.active { background: #FFF; color: #000; border-color: #000; }
.status-badge.inactive { background: #F5F5F5; color: #666; border-color: #999; }
.btn-edit, .btn-delete { padding: 6px 12px; margin-right: 5px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 600; }
.btn-edit { background: #000; color: white; }
.btn-edit:hover { background: #333; }
.btn-delete { background: #FFF; color: #000; border: 1px solid #000; }
.btn-delete:hover { background: #F5F5F5; }
.dialog-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.dialog-box { background: white; padding: 30px; border-radius: 8px; width: 90%; max-width: 500px; border: 2px solid #000; }
.dialog-box h3 { margin-bottom: 20px; color: #000; font-weight: bold; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-size: 14px; color: #000; font-weight: 600; }
.form-group input, .form-group select { width: 100%; padding: 8px; border: 2px solid #DDD; border-radius: 4px; }
.form-group input:focus, .form-group select:focus { outline: none; border-color: #000; }
.dialog-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.btn-cancel, .btn-submit { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; }
.btn-cancel { background: #F5F5F5; color: #333; border: 1px solid #DDD; }
.btn-cancel:hover { background: #E0E0E0; }
.btn-submit { background: #000; color: white; }
.btn-submit:hover { background: #333; }
</style>
