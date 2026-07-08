<template>
  <div class="import-page">
    <div class="import-container">
      <div class="import-header">
        <p class="import-eyebrow">Importacion</p>
        <h1>Importar datos RDF</h1>
        <p class="import-copy">
          Sube entre 1 y 3 archivos RDF junto con su ShEx, o directamente un paquete ZIP exportado por la aplicacion.
        </p>
      </div>

      <label class="import-picker">
        <span class="import-picker-title">Seleccionar archivos RDF/ShEx</span>
        <span class="import-picker-help">Formatos admitidos: .ttl, .rdf, .xml, .shex y .zip.</span>
        <input type="file" multiple @change="onFileChange" accept=".ttl,.rdf,.xml,.shex,.zip" />
      </label>

      <p v-if="files.length" class="import-selected">
        {{ files.length }} archivo<span v-if="files.length !== 1">s</span> seleccionado<span v-if="files.length !== 1">s</span>
      </p>

      <button :disabled="!files.length || importing" @click="previewFiles">Previsualizar y validar</button>

      <div v-if="validationErrors.length" class="import-errors">
        <h2>Errores de validacion</h2>
        <ul>
          <li v-for="(error, index) in validationErrors" :key="`${error}-${index}`">
            {{ error }}
          </li>
        </ul>
      </div>

      <div v-if="preview.length" class="preview-section">
        <h2>Vista previa</h2>
        <div class="preview-scroll" tabindex="0" aria-label="Vista previa de datos importados">
          <div v-for="(item, idx) in preview" :key="idx" class="preview-item">
            <strong>{{ item.tipo.toUpperCase() }}</strong>
            <ul>
              <li v-for="campo in filtrarDatos(item.datos)" :key="campo.etiqueta">
                <span class="label">{{ campo.etiqueta }}: </span>
                <span>{{ campo.valor }}</span>
              </li>
            </ul>
          </div>
        </div>
        <button :disabled="importing" @click="confirmImport">
          {{ importing ? 'Importando...' : 'Confirmar importacion' }}
        </button>
      </div>
    </div>

    <div v-if="importSuccessVisible" class="import-success-overlay">
      <div class="import-success-modal" role="dialog" aria-modal="true" aria-labelledby="import-success-title">
        <h2 id="import-success-title">Importacion completada</h2>
        <p>Los datos se han actualizado correctamente.</p>

        <div v-if="importSuccessWarnings.length" class="import-success-warnings">
          <strong>Avisos</strong>
          <ul>
            <li v-for="(warning, index) in importSuccessWarnings" :key="`${warning}-${index}`">
              {{ warning }}
            </li>
          </ul>
        </div>

        <button type="button" @click="acceptImportSuccess">Aceptar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useImportView } from '@/scripts/views/importView'

const {
  files,
  preview,
  validationErrors,
  importSuccessVisible,
  importSuccessWarnings,
  importing,
  filtrarDatos,
  onFileChange,
  previewFiles,
  confirmImport,
  acceptImportSuccess
} = useImportView()
</script>

<style scoped src="@/styles/views/ImportView.css"></style>
