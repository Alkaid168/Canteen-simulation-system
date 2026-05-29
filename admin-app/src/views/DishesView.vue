<template>
  <div class="dishes-view">
    <div class="page-header">
      <h1>菜品管理</h1>
      <button @click="showAddDialog = true" class="add-button">+ 添加菜品</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>菜品名称</th>
            <th>价格</th>
            <th>图片</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="dish in dishes" :key="dish.id">
            <td>{{ dish.id }}</td>
            <td>{{ dish.name }}</td>
            <td>¥{{ dish.price }}</td>
            <td>
              <span v-if="dish.image_url" class="image-indicator" title="有图片">🖼️</span>
              <span v-else>-</span>
            </td>
            <td>
              <span :class="['status-badge', dish.is_active ? 'active' : 'inactive']">
                {{ dish.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td>
              <button @click="editDish(dish)" class="btn-edit">编辑</button>
              <button v-if="dish.is_active" @click="deleteDish(dish.id)" class="btn-delete">下架</button>
              <button v-else @click="activateDish(dish.id)" class="btn-activate">上架</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 添加/编辑对话框 -->
    <div v-if="showAddDialog || showEditDialog" class="dialog-overlay" @click="closeDialogs">
      <div class="dialog-box" @click.stop>
        <h3>{{ showEditDialog ? '编辑菜品' : '添加菜品' }}</h3>
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label>菜品名称</label>
            <input v-model="formData.name" required />
          </div>
          <div class="form-group">
            <label>价格</label>
            <input v-model.number="formData.price" type="number" step="0.01" required />
          </div>
          <div class="form-group">
            <label>图片URL</label>
            <input v-model="formData.image_url" placeholder="可选，留空显示默认图片" />
          </div>
          <div class="form-group" v-if="showEditDialog">
            <label>
              <input type="checkbox" v-model="formData.is_active" />
              启用
            </label>
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
  name: 'DishesView',
  setup() {
    const dishes = ref([])
    const loading = ref(true)
    const showAddDialog = ref(false)
    const showEditDialog = ref(false)
    const formData = ref({
      name: '',
      price: 0,
      image_url: '',
      is_active: true
    })
    const editingId = ref(null)

    const loadDishes = async () => {
      try {
        loading.value = true
        const response = await axios.get('/admin/dishes')
        if (response.success) {
          dishes.value = response.data
        }
      } catch (error) {
        alert('加载失败: ' + (error.error || '未知错误'))
      } finally {
        loading.value = false
      }
    }

    const editDish = (dish) => {
      formData.value = { ...dish }
      editingId.value = dish.id
      showEditDialog.value = true
    }

    const deleteDish = async (id) => {
      if (!confirm('确定要下架这个菜品吗？')) return
      try {
        const response = await axios.delete(`/admin/dishes/${id}`)
        if (response.success) {
          loadDishes()
        }
      } catch (error) {
        alert('下架失败: ' + (error.error || '未知错误'))
      }
    }

    const activateDish = async (id) => {
      if (!confirm('确定要重新上架这个菜品吗？')) return
      try {
        const response = await axios.post(`/admin/dishes/${id}/activate`)
        if (response.success) {
          loadDishes()
        }
      } catch (error) {
        alert('上架失败: ' + (error.error || '未知错误'))
      }
    }

    const submitForm = async () => {
      try {
        if (showEditDialog.value) {
          await axios.put(`/admin/dishes/${editingId.value}`, formData.value)
        } else {
          await axios.post('/admin/dishes', formData.value)
        }
        closeDialogs()
        loadDishes()
      } catch (error) {
        alert('操作失败: ' + (error.error || '未知错误'))
      }
    }

    const closeDialogs = () => {
      showAddDialog.value = false
      showEditDialog.value = false
      formData.value = {
        name: '',
        price: 0,
        image_url: '',
        is_active: true
      }
      editingId.value = null
    }

    onMounted(() => {
      loadDishes()
    })

    return {
      dishes,
      loading,
      showAddDialog,
      showEditDialog,
      formData,
      editDish,
      deleteDish,
      activateDish,
      submitForm,
      closeDialogs
    }
  }
}
</script>

<style scoped>
.dishes-view {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  color: #000;
  font-weight: bold;
}

.add-button {
  padding: 10px 20px;
  background: #000;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.add-button:hover {
  background: #333;
}

.loading {
  text-align: center;
  padding: 40px;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #DDD;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #000;
  color: #FFF;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #000;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
}

.status-badge.active {
  background: #FFF;
  color: #000;
  border-color: #000;
}

.status-badge.inactive {
  background: #F5F5F5;
  color: #666;
  border-color: #999;
}

.btn-edit, .btn-delete {
  padding: 6px 12px;
  margin-right: 5px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
}

.btn-edit {
  background: #000;
  color: white;
}

.btn-edit:hover {
  background: #333;
}

.btn-delete {
  background: #FFF;
  color: #000;
  border: 1px solid #000;
}

.btn-delete:hover {
  background: #F5F5F5;
}

.btn-activate {
  padding: 6px 12px;
  margin-right: 5px;
  border: 1px solid #000;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  background: #000;
  color: #FFF;
}

.btn-activate:hover {
  background: #333;
}

.image-indicator {
  font-size: 16px;
  cursor: help;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-box {
  background: white;
  padding: 30px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  border: 2px solid #000;
}

.dialog-box h3 {
  margin-bottom: 20px;
  color: #000;
  font-weight: bold;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #000;
  font-size: 14px;
  font-weight: 600;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 2px solid #DDD;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #000;
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-cancel, .btn-submit {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.btn-cancel {
  background: #F5F5F5;
  color: #333;
  border: 1px solid #DDD;
}

.btn-cancel:hover {
  background: #E0E0E0;
}

.btn-submit {
  background: #000;
  color: white;
}

.btn-submit:hover {
  background: #333;
}
</style>
