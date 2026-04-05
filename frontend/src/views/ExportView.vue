<template>
  <div class="export-page">
    <div class="export-card">
      <h1 class="export-title">Exportación de datos</h1>

      <div class="selector-row">
        <label class="section-title" for="selected-patient">Selecciona un paciente:</label>
        <select id="selected-patient" v-model="selectedPatient" @change="loadPatientData" class="patient-select">
          <option disabled value="">-- Escoge un paciente --</option>
          <option v-for="p in pacientes" :key="p.id" :value="p.id">
            {{ p.nombre }} {{ p.apellido }}
          </option>
        </select>
      </div>

      <div v-if="selectedPatient" class="export-section">
        <h2 class="section-title">Opciones de exportación</h2>
        <div class="export-options">
          <button
            v-if="procedimientos.length"
            @click="setTipo('procedimientos')"
            class="option-btn"
          >
            Procedimientos ({{ procedimientos.length }})
          </button>
          <button
            v-if="alergias.length"
            @click="setTipo('alergias')"
            class="option-btn option-btn-danger"
          >
            Alergias ({{ alergias.length }})
          </button>
        </div>
      </div>

      <div v-if="tipoSeleccionado" class="export-section">
        <h3 class="section-title">{{ tipoSeleccionado }} ({{ itemsMostrados.length }})</h3>

        <div class="selection-box">
          <div class="toggle-row">
            <input
              type="checkbox"
              id="incluir-paciente"
              v-model="incluirPaciente"
            />
            <label for="incluir-paciente">
              Incluir datos del paciente en la exportación
            </label>
          </div>
          <p class="toggle-help">
            Si está activado, se incluirán los datos personales del paciente junto con los {{ tipoSeleccionado }} seleccionados.
          </p>
        </div>

        <div class="selection-actions">
          <button @click="selectAll" class="selection-btn">Seleccionar todos</button>
          <button @click="deselectAll" class="selection-btn">Deseleccionar todos</button>
        </div>

        <ul class="selection-list">
          <li
            v-for="(item, index) in itemsMostrados"
            :key="getItemId(item, index)"
            class="selection-item"
          >
            <input
              type="checkbox"
              v-model="seleccionados"
              :value="getItemId(item, index)"
              :id="`item-${index}`"
            />
            <label :for="`item-${index}`" class="selection-label">
              {{ item.text || item.display || item.code || `Item ${index + 1}` }}
            </label>
          </li>
        </ul>

        <div class="summary">
          <p class="selection-count">Seleccionados: {{ seleccionados.length }} {{ tipoSeleccionado }}</p>
          <p>Datos del paciente: {{ incluirPaciente ? 'Incluidos' : 'No incluidos' }}</p>
        </div>

        <button
          @click="exportarSeleccionados"
          :disabled="seleccionados.length === 0"
          class="export-btn"
        >
          Exportar seleccionados ({{ seleccionados.length }})
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useExportView } from '@/scripts/views/exportView'

const {
  pacientes,
  selectedPatient,
  procedimientos,
  alergias,
  tipoSeleccionado,
  seleccionados,
  incluirPaciente,
  itemsMostrados,
  getItemId,
  loadPatientData,
  setTipo,
  selectAll,
  deselectAll,
  exportarSeleccionados
} = useExportView()
</script>

<style scoped src="@/styles/views/ExportView.css"></style>
