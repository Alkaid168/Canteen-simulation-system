<template>
  <div class="seat-groups-view">
    <div class="page-header">
      <h1>座位组管理</h1>
      <button @click="showAddDialog = true" class="add-button">+ 添加座位组</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>组名</th>
            <th>容量</th>
            <th>座位数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="group in groups" :key="group.id">
            <td>{{ group.id }}</td>
            <td>{{ group.name }}</td>
            <td>{{ group.capacity }}</td>
            <td>{{ group.seats ? group.seats.length : 0 }}</td>
            <td>
              <button @click="deleteGroup(group.id)" class="btn-delete">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showAddDialog" class="dialog-overlay" @click="closeDialogs">
      <div class="dialog-box" @click.stop>
        <h3>添加座位组</h3>
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label>组名</label>
            <input v-model="formData.name" required />
          </div>
          <div class="form-group">
            <label>容量</label>
            <input v-model.number="formData.capacity" type="number" min="1" max="4" required />
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
  name: 'SeatGroupsView',
  setup() {
    const groups = ref([])
    const loading = ref(true)
    const showAddDialog = ref(false)
    const formData = ref({ name: '', capacity: 4 })

    const loadGroups = async () => {
      try {
        loading.value = true
        const response = await axios.get('/admin/seat-groups')
        if (response.success) groups.value = response.data
      } catch (error) {
        alert('加载失败')
      } finally {
        loading.value = false
      }
    }

    const deleteGroup = async (id) => {
      if (!confirm('确定要删除吗？')) return
      try {
        await axios.delete(`/admin/seat-groups/${id}`)
        loadGroups()
      } catch (error) {
        alert('删除失败')
      }
    }

    const submitForm = async () => {
      try {
        await axios.post('/admin/seat-groups', formData.value)
        closeDialogs()
        loadGroups()
      } catch (error) {
        alert('操作失败')
      }
    }

    const closeDialogs = () => {
      showAddDialog.value = false
      formData.value = { name: '', capacity: 4 }
    }

    onMounted(loadGroups)

    return { groups, loading, showAddDialog, formData, deleteGroup, submitForm, closeDialogs }
  }
}
</script>

<style scoped>
.seat-groups-view { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h1 { font-size: 24px; color: #000; font-weight: bold; }
.add-button { padding: 10px 20px; background: #000; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600; }
.add-button:hover { background: #333; }
.loading { text-align: center; padding: 40px; }
.table-container { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid #DDD; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #000; color: #FFF; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #000; }
.data-table td { padding: 12px; border-bottom: 1px solid #f0f0f0; color: #333; }
.btn-delete { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; background: #FFF; color: #000; border: 1px solid #000; font-weight: 600; }
.btn-delete:hover { background: #F5F5F5; }
.dialog-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.dialog-box { background: white; padding: 30px; border-radius: 8px; width: 90%; max-width: 500px; border: 2px solid #000; }
.dialog-box h3 { margin-bottom: 20px; color: #000; font-weight: bold; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-size: 14px; color: #000; font-weight: 600; }
.form-group input { width: 100%; padding: 8px; border: 2px solid #DDD; border-radius: 4px; }
.form-group input:focus { outline: none; border-color: #000; }
.dialog-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.btn-cancel, .btn-submit { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; }
.btn-cancel { background: #F5F5F5; color: #333; border: 1px solid #DDD; }
.btn-cancel:hover { background: #E0E0E0; }
.btn-submit { background: #000; color: white; }
.btn-submit:hover { background: #333; }
</style>
