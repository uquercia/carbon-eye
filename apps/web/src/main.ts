// 前端应用入口文件：
// 1. 创建 Vue 应用
// 2. 注册 Element Plus 组件库
// 3. 挂载到 index.html 里的 #app 节点
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'
import App from './App.vue'

createApp(App).use(ElementPlus).mount('#app')
