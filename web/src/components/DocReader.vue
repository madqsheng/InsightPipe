<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import MarkdownIt from 'markdown-it'
import { api } from '../services/api'

const props = defineProps({
  filename: String
})

const emit = defineEmits(['close', 'deleted'])

// State
const mode = ref('read') // 'read' | 'edit'
const content = ref('') // The raw content
const loading = ref(false)
const error = ref('')
const saving = ref(false)

// Edit state
const editContent = ref('')

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

const renderedContent = computed(() => {
  return md.render(content.value)
})

const title = computed(() => props.filename?.replace('.md', ''))

const loadDoc = async () => {
  if (!props.filename) return
  
  loading.value = true
  error.value = ''
  mode.value = 'read'
  
  try {
    const res = await api.getDocument(props.filename)
    content.value = res.content
  } catch (err) {
    error.value = 'Failed to load document: ' + err.message
  } finally {
    loading.value = false
  }
}

const startEdit = () => {
    editContent.value = content.value
    mode.value = 'edit'
}

const cancelEdit = () => {
    mode.value = 'read'
    editContent.value = ''
}

const saveEdit = async () => {
    saving.value = true
    try {
        await api.saveDocument(title.value, editContent.value, true)
        content.value = editContent.value
        mode.value = 'read'
    } catch (err) {
        alert('Failed to save: ' + err.message)
    } finally {
        saving.value = false
    }
}

const deleteDoc = async () => {
    if (!confirm(`Are you sure you want to delete "${title.value}"?`)) return
    
    try {
        await api.deleteDocument(props.filename)
        emit('deleted', props.filename)
        emit('close')
    } catch (err) {
        alert('Failed to delete: ' + err.message)
    }
}

onMounted(loadDoc)
watch(() => props.filename, loadDoc)
</script>

<template>
  <div class="bg-gray-800 rounded-xl shadow-2xl border border-gray-700 flex flex-col h-full overflow-hidden">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-700 bg-gray-900/50 flex justify-between items-center shrink-0">
      <h2 class="text-xl font-bold bg-gradient-to-r from-green-400 to-teal-300 bg-clip-text text-transparent truncate flex-1">
        {{ title }}
      </h2>
      
      <div class="flex items-center gap-2 ml-4">
        <template v-if="mode === 'read'">
            <button 
                @click="startEdit"
                class="text-gray-400 hover:text-blue-400 p-2 rounded hover:bg-gray-700 transition"
                title="Edit"
            >
                ✏️
            </button>
            <button 
                @click="deleteDoc"
                class="text-gray-400 hover:text-red-400 p-2 rounded hover:bg-gray-700 transition"
                title="Delete"
            >
                🗑️
            </button>
            <div class="w-px h-5 bg-gray-700 mx-2"></div>
            <button 
                @click="$emit('close')"
                class="text-gray-400 hover:text-white hover:bg-gray-700 px-3 py-1 rounded text-sm transition"
            >
                Close
            </button>
        </template>
        
        <template v-else>
            <button 
                @click="saveEdit"
                :disabled="saving"
                class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded text-sm transition flex items-center gap-1"
            >
                <span v-if="saving">⏳</span> 💾 Save
            </button>
            <button 
                @click="cancelEdit"
                class="text-gray-400 hover:text-white px-3 py-1 rounded text-sm transition"
            >
                Cancel
            </button>
        </template>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-4 sm:p-8 custom-scrollbar bg-gray-900">
      <div v-if="loading" class="flex justify-center items-center h-full text-gray-400">
        <span class="animate-pulse">Loading content...</span>
      </div>
      
      <div v-else-if="error" class="text-red-400 text-center mt-10">
        {{ error }}
      </div>
      
      <!-- Read Mode -->
      <div v-else-if="mode === 'read'" class="prose prose-invert prose-blue max-w-none">
        <div v-html="renderedContent"></div>
      </div>
      
      <!-- Edit Mode -->
      <div v-else class="h-full flex flex-col">
         <textarea 
            v-model="editContent"
            class="flex-1 w-full bg-gray-800 border border-gray-700 rounded-lg p-4 font-mono text-sm text-gray-200 outline-none focus:border-blue-500 resize-none"
         ></textarea>
      </div>
    </div>
  </div>
</template>
