<script setup>
import { ref } from 'vue'
import { api } from '../services/api'

const userInput = ref('')
const generatedPrompt = ref('')
const loading = ref(false)
const copied = ref(false)

const handleGenerate = async () => {
  if (!userInput.value.trim()) return
  
  loading.value = true
  generatedPrompt.value = ''
  copied.value = false
  
  try {
    const res = await api.generatePrompt(userInput.value)
    generatedPrompt.value = res.prompt
  } catch (err) {
    console.error(err)
    alert('Error generating prompt')
  } finally {
    loading.value = false
  }
}

const handleCopy = () => {
  navigator.clipboard.writeText(generatedPrompt.value)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}
</script>

<template>
  <div class="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
    <h2 class="text-2xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
      1. Ask InsightPipe
    </h2>
    
    <div class="space-y-4">
      <div>
        <label class="block text-sm text-gray-400 mb-1">What are you curious about?</label>
        <textarea 
          v-model="userInput"
          class="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none transition"
          rows="3"
          placeholder="e.g. What is First Principles Thinking?"
          @keydown.ctrl.enter="handleGenerate"
        ></textarea>
        <p class="text-xs text-gray-500 mt-1 text-right">Ctrl + Enter to generate</p>
      </div>

      <button 
        @click="handleGenerate"
        :disabled="loading || !userInput"
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition-colors flex justify-center items-center gap-2"
      >
        <span v-if="loading" class="animate-spin">⏳</span>
        {{ loading ? 'Generating...' : 'Generate Expert Prompt' }}
      </button>

      <div v-if="generatedPrompt" class="relative mt-4">
        <label class="block text-sm text-gray-400 mb-1">Generated Prompt (Copy this)</label>
        <textarea 
          readonly
          v-model="generatedPrompt"
          class="w-full bg-gray-900 border border-gray-600 rounded-lg p-3 text-sm font-mono text-gray-300 h-48 focus:outline-none"
        ></textarea>
        <button 
          @click="handleCopy"
          class="absolute top-8 right-2 bg-gray-700 hover:bg-gray-600 text-xs px-3 py-1 rounded border border-gray-500 transition"
        >
          {{ copied ? '✅ Copied!' : '📋 Copy' }}
        </button>
      </div>
    </div>
  </div>
</template>
