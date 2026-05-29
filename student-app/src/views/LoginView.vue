<template>
  <div class="login-container">
    <div class="login-box">
      <h1 class="title">北京交通大学食堂就餐系统</h1>
      <h2 class="subtitle">学生登录</h2>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="studentId">学号</label>
          <input
            id="studentId"
            v-model="studentId"
            type="text"
            placeholder="请输入学号"
            required
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            required
            class="form-input"
          />
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <button type="submit" class="login-button" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../api/axios'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const studentId = ref('')
    const password = ref('')
    const errorMessage = ref('')
    const loading = ref(false)

    const handleLogin = async () => {
      errorMessage.value = ''
      loading.value = true

      try {
        const response = await axios.post('/auth/student/login', {
          student_id: studentId.value,
          password: password.value
        })

        if (response.success) {
          // 登录成功，跳转到选人数页
          router.push('/party-size')
        } else {
          errorMessage.value = response.error || '登录失败'
        }
      } catch (error) {
        errorMessage.value = error.error || '登录失败，请检查学号和密码'
      } finally {
        loading.value = false
      }
    }

    return {
      studentId,
      password,
      errorMessage,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #F5F5F5;
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  border: 2px solid #000;
}

.title {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  color: #000;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 18px;
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.login-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #000;
  font-weight: 600;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #DDD;
  border-radius: 5px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #000;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 15px;
  text-align: center;
  font-size: 14px;
  border: 1px solid #fcc;
}

.login-button {
  width: 100%;
  padding: 12px;
  background: #000;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.login-button:hover:not(:disabled) {
  background: #333;
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
