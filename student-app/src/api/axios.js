import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  withCredentials: true, // 支持跨域携带cookie
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
instance.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      // 服务器返回错误响应
      return Promise.reject(error.response.data)
    } else if (error.request) {
      // 请求已发出但没有收到响应
      return Promise.reject({ error: '网络错误，请检查连接' })
    } else {
      // 其他错误
      return Promise.reject({ error: error.message })
    }
  }
)

export default instance
