<template>
  <div class="main-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>管理后台</h2>
      </div>
      
      <nav class="sidebar-nav">
        <div class="nav-section">
          <h3 class="nav-section-title">基础数据</h3>
          <router-link to="/admin/dishes" class="nav-item">
            <span>菜品管理</span>
          </router-link>
          <router-link to="/admin/windows" class="nav-item">
            <span>窗口管理</span>
          </router-link>
          <router-link to="/admin/seat-groups" class="nav-item">
            <span>座位组管理</span>
          </router-link>
          <router-link to="/admin/seats" class="nav-item">
            <span>座位管理</span>
          </router-link>
          <router-link to="/admin/students" class="nav-item">
            <span>学生管理</span>
          </router-link>
        </div>

        <div class="nav-section">
          <h3 class="nav-section-title">预测管理</h3>
          <router-link to="/admin/prediction" class="nav-item">
            <span>预测与调整</span>
          </router-link>
        </div>

        <div class="nav-section">
          <h3 class="nav-section-title">运营报表</h3>
          <router-link to="/admin/reports" class="nav-item">
            <span>数据报表</span>
          </router-link>
        </div>

        <div class="nav-section">
          <h3 class="nav-section-title">系统配置</h3>
          <router-link to="/admin/config" class="nav-item">
            <span>系统设置</span>
          </router-link>
        </div>
      </nav>

      <div class="sidebar-footer">
        <button @click="handleLogout" class="logout-button">
          退出登录
        </button>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import axios from '../api/axios'

export default {
  name: 'MainLayout',
  setup() {
    const router = useRouter()

    const handleLogout = async () => {
      try {
        await axios.post('/auth/logout')
      } catch (error) {
        console.error('登出失败:', error)
      } finally {
        router.push('/login')
      }
    }

    return {
      handleLogout
    }
  }
}
</script>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 250px;
  background: #000;
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.sidebar-header h2 {
  font-size: 20px;
  font-weight: bold;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
}

.nav-section {
  margin-bottom: 25px;
}

.nav-section-title {
  font-size: 12px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.6);
  padding: 0 20px;
  margin-bottom: 10px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.router-link-active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-left: 3px solid #FFF;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.logout-button {
  width: 100%;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.logout-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.main-content {
  flex: 1;
  margin-left: 250px;
  padding: 30px;
  background: #f5f5f5;
  min-height: 100vh;
}
</style>
