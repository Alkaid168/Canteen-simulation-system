<template>
  <div class="students-view">
    <div class="page-header">
      <h1>学生管理</h1>
      <button @click="showAddDialog = true" class="add-button">+ 添加学生</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>学号</th>
            <th>姓名</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in students" :key="student.id">
            <td>{{ student.id }}</td>
            <td>{{ student.student_id }}</td>
            <td>{{ student.name }}</td>
            <td>{{ formatDate(student.created_at) }}</td>
            <td>
              <button @click="editStudent(student)" class="btn-edit">编辑</button>
              <button @click="deleteStudent(student.id)" class="btn-delete">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showAddDialog || showEditDialog" class="dialog-overlay" @click="closeDialogs">
      <div class="dialog-box" @click.stop>
        <h3>{{ showEditDialog ? '编辑学生' : '添加学生' }}</h3>
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label>学号</label>
            <input v-model="formData.student_id" required />
          </div>
          <div class="form-group">
            <label>姓名</label>
            <input v-model="formData.name" required />
          </div>
          <div class="form-group">
            <label>密码</label>
            <input v-model="formData.password" type="password" :required="!showEditDialog" 
                   :placeholder="showEditDialog ? '留空则不修改' : ''" />
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
  name: 'StudentsView',
  setup() {
    const students = ref([])
    const loading = ref(true)
    const showAddDialog = ref(false)
    const showEditDialog = ref(false)
    const formData = ref({ student_id: '', name: '', password: '' })
    const editingId = ref(null)

    const loadStudents = async () => {
      try {
        loading.value = true
        const response = await axios.get('/admin/students')
        if (response.success) students.value = response.data
      } catch (error) {
        alert('加载失败')
      } finally {
        loading.value = false
      }
    }

    const editStudent = (student) => {
      formData.value = { student_id: student.student_id, name: student.name, password: '' }
      editingId.value = student.id
      showEditDialog.value = true
    }

    const deleteStudent = async (id) => {
      if (!confirm('确定要删除吗？')) return
      try {
        await axios.delete(`/admin/students/${id}`)
        loadStudents()
      } catch (error) {
        alert('删除失败')
      }
    }

    const submitForm = async () => {
      try {
        const data = { ...formData.value }
        if (showEditDialog.value && !data.password) {
          delete data.password
        }
        if (showEditDialog.value) {
          await axios.put(`/admin/students/${editingId.value}`, data)
        } else {
          await axios.post('/admin/students', data)
        }
        closeDialogs()
        loadStudents()
      } catch (error) {
        alert('操作失败')
      }
    }

    const closeDialogs = () => {
      showAddDialog.value = false
      showEditDialog.value = false
      formData.value = { student_id: '', name: '', password: '' }
      editingId.value = null
    }

    const formatDate = (dateStr) => {
      return new Date(dateStr).toLocaleString('zh-CN')
    }

    onMounted(loadStudents)

    return { students, loading, showAddDialog, showEditDialog, formData, editStudent, deleteStudent, submitForm, closeDialogs, formatDate }
  }
}
</script>

<style scoped>
.students-view { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h1 { font-size: 24px; color: #000; font-weight: bold; }
.add-button { padding: 10px 20px; background: #000; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600; }
.add-button:hover { background: #333; }
.loading { text-align: center; padding: 40px; }
.table-container { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid #DDD; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #000; color: #FFF; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #000; }
.data-table td { padding: 12px; border-bottom: 1px solid #f0f0f0; color: #333; }
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
.form-group input { width: 100%; padding: 8px; border: 2px solid #DDD; border-radius: 4px; }
.form-group input:focus { outline: none; border-color: #000; }
.dialog-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.btn-cancel, .btn-submit { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; }
.btn-cancel { background: #F5F5F5; color: #333; border: 1px solid #DDD; }
.btn-cancel:hover { background: #E0E0E0; }
.btn-submit { background: #000; color: white; }
.btn-submit:hover { background: #333; }
</style>
