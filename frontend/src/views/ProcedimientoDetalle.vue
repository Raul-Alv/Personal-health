<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 600 600"
    class="teeth-diagram"
  >
    <!-- Ejemplo simplificado: solo 4 dientes -->
    <path
      id="tooth-11"
      class="tooth"
      :class="{ selected: selectedIso === '11' }"
      d="M…Z"
    />
    <path
      id="tooth-12"
      class="tooth"
      :class="{ selected: selectedIso === '12' }"
      d="M…Z"
    />
    <path
      id="tooth-21"
      class="tooth"
      :class="{ selected: selectedIso === '21' }"
      d="M…Z"
    />
    <path
      id="tooth-22"
      class="tooth"
      :class="{ selected: selectedIso === '22' }"
      d="M…Z"
    />
    <!-- … el resto de tus path … -->
  </svg>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const selectedIso = ref(null)

async function fetchTooth() {
  const res  = await fetch('/api/selected-tooth')
  const txt  = await res.text()
  const isoM = txt.match(/ISO designation\s*([1-4]\d)/i)
  if (isoM) selectedIso.value = isoM[1]
}

onMounted(fetchTooth)
</script>

<style scoped>
.tooth {
  fill: #f5f5f5;
  stroke: #333;
  transition: fill 0.2s;
}
.tooth.selected {
  fill: red !important;
}
</style>
