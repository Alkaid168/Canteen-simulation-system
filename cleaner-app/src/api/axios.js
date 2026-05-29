import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

instance.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      return Promise.reject(error.response.data)
    } else if (error.request) {
      return Promise.reject({ error: '网络错误，请检查连接' })
    } else {
      return Promise.reject({ error: error.message })
    }
  }
)

export default instance
