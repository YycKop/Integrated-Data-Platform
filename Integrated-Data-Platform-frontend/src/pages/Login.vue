<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/pages/Login.vue-->
<template>
  <div class="login-container">
    <div class="login-form">
      <h2 class="login-title">一体化数据平台</h2>

      <!-- 连接状态提示 -->
      <div v-if="connectionStatus" class="connection-status" :class="connectionStatus.type">
        <el-alert
          :title="connectionStatus.title"
          :description="connectionStatus.description"
          :type="connectionStatus.type"
          show-icon
          :closable="false"
        />
      </div>

      <el-form
        :model="form"
        :rules="rules"
        ref="loginFormRef"
        class="form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="register-link">
        <span>还没有账号？</span>
        <el-button type="text" @click="showRegister = true">立即注册</el-button>
      </div>

      <!-- 测试账号提示 -->
      <div class="test-account">
        <el-divider content-position="center">测试账号</el-divider>
        <p>用户名: testuser</p>
        <p>密码: testpass123</p>
        <el-button type="text" size="small" @click="fillTestAccount">填充测试账号</el-button>
      </div>
    </div>

    <!-- 注册对话框 -->
    <el-dialog
      v-model="showRegister"
      title="用户注册"
      width="500px"
      @close="handleRegisterClose"
    >
      <el-form
        :model="registerForm"
        :rules="registerRules"
        ref="registerFormRef"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="至少3个字符" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入有效邮箱" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" show-password placeholder="至少6个字符" />
        </el-form-item>

        <el-form-item label="确认密码" prop="password_confirm">
          <el-input v-model="registerForm.password_confirm" type="password" show-password placeholder="请再次输入密码" />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select v-model="registerForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="数据分析师" value="analyst" />
            <el-option label="查看者" value="viewer" />
          </el-select>
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="可选" />
        </el-form-item>

        <el-form-item label="部门" prop="department">
          <el-input v-model="registerForm.department" placeholder="可选" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showRegister = false">取消</el-button>
        <el-button type="primary" :loading="registerLoading" @click="handleRegister">
          注册
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref()
const registerFormRef = ref()
const loading = ref(false)
const showRegister = ref(false)
const registerLoading = ref(false)
const connectionStatus = ref(null)

const form = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  role: 'viewer',
  phone: '',
  department: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 测试后端连接
const testBackendConnection = async () => {
  connectionStatus.value = {
    type: 'info',
    title: '正在连接后端服务...',
    description: '请稍候'
  }

  const connected = await authStore.testConnection()

  if (connected) {
    connectionStatus.value = {
      type: 'success',
      title: '后端连接正常',
      description: '可以正常登录和注册'
    }
  } else {
    connectionStatus.value = {
      type: 'warning',
      title: '后端连接异常',
      description: '但接口可能存在，请尝试登录'
    }
  }
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login(form)
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        ElMessage.error(error.message)
        console.error('登录错误详情:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      registerLoading.value = true
      try {
        await authStore.register(registerForm)
        ElMessage.success('注册成功')
        showRegister.value = false
        handleRegisterClose()
        // 注册成功后自动填充登录表单
        form.username = registerForm.username
        form.password = ''
        ElMessage.info('用户名已自动填充，请输入密码登录')
      } catch (error) {
        ElMessage.error(error.message)
        console.error('注册错误详情:', error)
      } finally {
        registerLoading.value = false
      }
    }
  })
}

const handleRegisterClose = () => {
  registerFormRef.value?.resetFields()
  Object.assign(registerForm, {
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    role: 'viewer',
    phone: '',
    department: ''
  })
}

const fillTestAccount = () => {
  form.username = 'testuser'
  form.password = 'testpass123'
  ElMessage.info('已填充测试账号，请点击登录')
}

onMounted(() => {
  testBackendConnection()
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-form {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 400px;
  max-width: 90vw;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
}

.register-link {
  text-align: center;
  color: #666;
  margin-bottom: 20px;
}

.connection-status {
  margin-bottom: 20px;
}

.test-account {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.test-account p {
  margin: 5px 0;
}
</style>
