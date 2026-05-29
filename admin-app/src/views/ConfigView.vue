<template>
  <div class="config-view">
    <div class="page-header">
      <h1>系统配置</h1>
      <button @click="saveConfig" :disabled="saving" class="save-button">
        {{ saving ? '保存中...' : '保存配置' }}
      </button>
    </div>

    <div v-if="message" :class="['message-box', messageType]">{{ message }}</div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else class="config-list">
      <div
        v-for="config in configs"
        :key="config.id"
        class="config-item"
      >
        <div class="config-info">
          <label class="config-key">{{ config.key }}</label>
          <p v-if="config.description" class="config-desc">{{ config.description }}</p>
        </div>
        <input
          v-model="editValues[config.key]"
          class="config-input"
          :placeholder="config.value"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import axios from '../api/axios'

export default {
  name: 'ConfigView',
  setup() {
    const configs = ref([])
    const loading = ref(true)
    const saving = ref(false)
    const message = ref('')
    const messageType = ref('success')
    const editValues = reactive({})

    const showMessage = (msg, type = 'success') => {
      message.value = msg
      messageType.value = type
      setTimeout(() => { message.value = '' }, 3000)
    }

    const loadConfig = async () => {
      try {
        loading.value = true
        const response = await axios.get('/admin/config')
        if (response.success) {
          configs.value = response.data
          response.data.forEach(c => {
            editValues[c.key] = c.value
          })
        }
      } catch (error) {
        showMessage('加载配置失败', 'error')
      } finally {
        loading.value = false
      }
    }

    const saveConfig = async () => {
      try {
        saving.value = true
        const response = await axios.put('/admin/config', editValues)
        if (response.success) {
          showMessage('配置保存成功')
          loadConfig()
        }
      } catch (error) {
        showMessage('保存失败: ' + (error.error || '未知错误'), 'error')
      } finally {
        saving.value = false
      }
    }

    onMounted(loadConfig)

    return { configs, loading, saving, message, messageType, editValues, saveConfig }
  }
}
</script>

<style scoped>
.config-view { max-width: 800px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h1 { font-size: 24px; color: #000; font-weight: bold; }
.save-button { padding: 10px 20px; background: #000; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; font-weight: 600; }
.save-button:hover { background: #333; }
.save-button:disabled { opacity: 0.6; cursor: not-allowed; }
.message-box { padding: 12px 20px; border-radius: 5px; margin-bottom: 20px; font-size: 14px; border: 1px solid; }
.message-box.success { background: #F5F5F5; color: #000; border-color: #000; }
.message-box.error { background: #FEE; color: #C33; border-color: #FCC; }
.loading { text-align: center; padding: 40px; }
.config-list { display: flex; flex-direction: column; gap: 15px; }
.config-item { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; gap: 20px; border: 1px solid #DDD; }
.config-info { flex: 1; }
.config-key { font-size: 16px; font-weight: 600; color: #000; display: block; margin-bottom: 4px; }
.config-desc { font-size: 13px; color: #666; }
.config-input { width: 250px; padding: 10px; border: 2px solid #DDD; border-radius: 5px; font-size: 14px; }
.config-input:focus { outline: none; border-color: #000; }
</style>
