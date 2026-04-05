<template>
  <div class="import-container">
    <h2>Importar datos RDF</h2>
    <input type="file" multiple @change="onFileChange" accept=".ttl,.rdf" />
    <button :disabled="!files.length" @click="previewFiles">Previsualizar</button>

    <div v-if="preview.length" class="preview-section">
      <h3>Previsualización de datos</h3>
      <div v-for="(item, idx) in preview" :key="idx" class="preview-item">
        <strong>{{ item.tipo.toUpperCase() }}</strong>
        <ul>
          <li v-for="campo in filtrarDatos(item.datos)" :key="campo.etiqueta">
            <span class="label">{{ campo.etiqueta }}: </span>
            <span>{{ campo.valor }}</span>
          </li>
        </ul>
      </div>
      <button @click="confirmImport">Confirmar importación</button>
    </div>
  </div>
</template>

<script setup>
import { useImportView } from '@/scripts/views/importView'

const {
  files,
  preview,
  filtrarDatos,
  onFileChange,
  previewFiles,
  confirmImport
} = useImportView()
</script>

<style scoped src="@/styles/views/ImportView.css"></style>
