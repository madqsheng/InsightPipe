<script setup>
import { ref } from 'vue'
import PromptGenerator from './components/PromptGenerator.vue'
import DocEditor from './components/DocEditor.vue'
import DocGallery from './components/DocGallery.vue'

const galleryRef = ref(null)

const onSaved = () => {
  if (galleryRef.value) {
    galleryRef.value.refresh()
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-gray-100 selection:bg-blue-500 selection:text-white pb-20">
    <header class="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-2xl">🧠</span>
          <h1 class="text-xl font-bold tracking-tight">InsightPipe</h1>
        </div>
        <div class="text-sm text-gray-500 font-mono">v0.1 MVP</div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12 h-[600px]">
        <!-- Left: Ask -->
        <PromptGenerator />
        
        <!-- Right: Save -->
        <!-- We trigger gallery refresh when a doc is saved, though currently DocEditor doesn't emit event. 
             Ideally we should pass a prop or use a store used here. For MVP, we can just rely on manual refresh or add emit. -->
        <DocEditor @saved="onSaved" /> 
      </div>

      <!-- Bottom: Gallery -->
      <DocGallery ref="galleryRef" />
      
    </main>
  </div>
</template>
