<script setup>
import { ref } from 'vue'
import { api } from '../services/api'

const geminiUrl = ref('')
const loading = ref(false)
const result = ref(null)
const error = ref(null)

async function importConversation() {
  if (!geminiUrl.value.trim()) {
    error.value = '请输入有效的Gemini分享链接'
    return
  }
  
  loading.value = true
  error.value = null
  result.value = null
  
  try {
    const data = await api.importGemini(geminiUrl.value.trim())
    result.value = data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function copyPrompt() {
  if (!result.value) return
  navigator.clipboard.writeText(result.value.prompt)
    .then(() => alert('✅ Prompt已复制到剪贴板'))
    .catch(() => alert('❌ 复制失败，请手动复制'))
}

function downloadMarkdown() {
  if (!result.value) return
  
  const blob = new Blob([result.value.markdown], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = result.value.filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function reset() {
  geminiUrl.value = ''
  result.value = null
  error.value = null
}
</script>

<template>
  <div class="bg-gray-800 rounded-xl shadow-2xl p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center gap-3 border-b border-gray-700 pb-4">
      <span class="text-3xl">📥</span>
      <div>
        <h2 class="text-xl font-bold">导入 Gemini 对话</h2>
        <p class="text-sm text-gray-400">从分享链接提取对话内容</p>
      </div>
    </div>

    <!-- Input Section -->
    <div v-if="!result" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">
          Gemini 分享链接
        </label>
        <input 
          v-model="geminiUrl"
          type="text"
          placeholder="https://gemini.google.com/share/..."
          class="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg 
                 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                 text-white placeholder-gray-500 transition-all"
          @keyup.enter="importConversation"
          :disabled="loading"
        />
      </div>

      <button 
        @click="importConversation"
        :disabled="loading || !geminiUrl.trim()"
        class="w-full py-3 px-6 bg-gradient-to-r from-blue-600 to-blue-700 
               hover:from-blue-700 hover:to-blue-800 disabled:from-gray-700 disabled:to-gray-800
               disabled:cursor-not-allowed text-white font-medium rounded-lg
               transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]
               shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
      >
        <span v-if="loading" class="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
        <span>{{ loading ? '解析中...' : '🚀 开始导入' }}</span>
      </button>

      <!-- Error Display -->
      <div v-if="error" class="p-4 bg-red-900/30 border border-red-700 rounded-lg flex items-start gap-3">
        <span class="text-xl">❌</span>
        <div class="flex-1">
          <p class="font-medium text-red-300">导入失败</p>
          <p class="text-sm text-red-400 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Result Section -->
    <div v-else class="space-y-5 animate-fade-in">
      <!-- Success Header -->
      <div class="flex items-start gap-3 p-4 bg-green-900/20 border border-green-700 rounded-lg">
        <span class="text-2xl">✅</span>
        <div class="flex-1">
          <h3 class="font-bold text-green-300 text-lg">{{ result.title }}</h3>
          <p class="text-sm text-green-400 mt-1">共 {{ result.turn_count }} 轮对话</p>
        </div>
      </div>

      <!-- Prompt Section -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <label class="text-sm font-medium text-gray-300">
            📝 推荐 Prompt（可编辑）
          </label>
          <button 
            @click="copyPrompt"
            class="px-3 py-1.5 text-xs bg-gray-700 hover:bg-gray-600 rounded-md
                   transition-colors flex items-center gap-1.5"
          >
            📋 复制
          </button>
        </div>
        <textarea 
          v-model="result.prompt"
          rows="12"
          class="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg
                 focus:outline-none focus:ring-2 focus:ring-blue-500
                 text-sm text-gray-300 font-mono resize-y"
        ></textarea>
      </div>

      <!-- Actions -->
      <div class="grid grid-cols-2 gap-3">
        <button 
          @click="downloadMarkdown"
          class="py-3 px-4 bg-gradient-to-r from-purple-600 to-purple-700
                 hover:from-purple-700 hover:to-purple-800
                 text-white font-medium rounded-lg transition-all
                 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
        >
          <span class="text-xl">💾</span>
          <span>下载 MD 文件</span>
        </button>
        
        <button 
          @click="reset"
          class="py-3 px-4 bg-gray-700 hover:bg-gray-600
                 text-white font-medium rounded-lg transition-all
                 flex items-center justify-center gap-2"
        >
          <span class="text-xl">🔄</span>
          <span>导入新对话</span>
        </button>
      </div>

      <!-- Usage Hint -->
      <div class="p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
        <p class="text-sm text-blue-300 font-medium mb-2">💡 使用提示</p>
        <ol class="text-sm text-blue-400 space-y-1 list-decimal list-inside">
          <li>点击"下载MD文件"保存对话记录</li>
          <li>打开ChatGPT/Claude，上传该MD文件</li>
          <li>复制上方Prompt并粘贴发送</li>
          <li>AI将自动生成洞察报告</li>
          <li>将报告复制回InsightPipe保存</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
