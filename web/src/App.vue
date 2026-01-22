<script setup>
import { ref } from 'vue'
import PromptGenerator from './components/PromptGenerator.vue'
import DocEditor from './components/DocEditor.vue'
import DocGallery from './components/DocGallery.vue'
import DocReader from './components/DocReader.vue'
import GeminiImporter from './components/GeminiImporter.vue'

const currentTab = ref('library') // 'library' | 'create'
const selectedDoc = ref(null) // document object when in 'read' mode
const galleryRef = ref(null)

// Actions
const switchTab = (tab) => {
  currentTab.value = tab
  selectedDoc.value = null // Exit read mode when switching main tabs
}

const onDocSelected = (doc) => {
  selectedDoc.value = doc
}

const onReaderClose = () => {
  selectedDoc.value = null
}

const onDocDeleted = () => {
    selectedDoc.value = null
    if (galleryRef.value) {
        galleryRef.value.refresh()
    }
}

const onSaved = () => {
    // Automatically switch back to library to show the result
    currentTab.value = 'library'
    // We need to wait for tick or just rely on mounted fetch in Gallery, 
    // but better to trigger refresh if we keep the component alive.
    if (galleryRef.value) {
        setTimeout(() => galleryRef.value.refresh(), 100)
    }
}

</script>

<template>
  <div class="min-h-screen bg-gray-900 text-gray-100 selection:bg-blue-500 selection:text-white flex flex-col">
    <!-- Header with Navigation -->
    <header class="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        <!-- Logo -->
        <div class="flex items-center gap-2 cursor-pointer" @click="switchTab('library')">
          <span class="text-2xl">🧠</span>
          <h1 class="text-xl font-bold tracking-tight hidden sm:block">InsightPipe</h1>
        </div>

        <!-- Tab Navigation -->
        <nav class="flex space-x-1 bg-gray-800 p-1 rounded-lg">
          <button 
            @click="switchTab('library')"
            :class="[
              'px-4 py-2 rounded-md text-sm font-medium transition-all',
              currentTab === 'library' && !selectedDoc
                ? 'bg-gray-700 text-white shadow-sm' 
                : 'text-gray-400 hover:text-gray-200'
            ]"
          >
            📚 Library
          </button>
          <button 
            @click="switchTab('create')"
            :class="[
              'px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-1',
              currentTab === 'create'
                ? 'bg-blue-600 text-white shadow-sm' 
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
            ]"
          >
            <span class="text-lg">+</span> New Insight
          </button>
        </nav>
      </div>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 relative">
      
      <!-- MODE: READ (Overlay) -->
      <transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-150 ease-in" leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
        <div v-if="selectedDoc" class="fixed inset-0 z-[100] bg-gray-900/90 backdrop-blur-sm p-4 sm:p-8 flex justify-center">
            <div class="w-full max-w-4xl h-full">
                <DocReader 
                    :filename="selectedDoc.filename" 
                    @close="onReaderClose" 
                    @deleted="onDocDeleted"
                />
            </div>
        </div>
      </transition>

      <!-- MODE: LIBRARY -->
      <div v-show="currentTab === 'library'" class="animate-fade-in">
         <!-- Pass ref to call refresh -->
         <DocGallery 
            ref="galleryRef" 
            @select="onDocSelected" 
         />
      </div>

      <!-- MODE: CREATE -->
      <div v-if="currentTab === 'create'" class="space-y-8 animate-fade-in-up">
        <!-- Gemini Importer - Full Width Card -->
        <div>
          <GeminiImporter />
        </div>

        <!-- Original Create Flow - Side by Side -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Left: Ask -->
          <div class="h-full overflow-y-auto custom-scrollbar">
              <PromptGenerator />
          </div>
          
          <!-- Right: Save -->
          <div class="h-full overflow-y-auto custom-scrollbar">
              <DocEditor @saved="onSaved" /> 
          </div>
        </div>
      </div>
      
    </main>
  </div>
</template>

<style>
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
.animate-fade-in-up {
  animation: fadeInUp 0.4s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
