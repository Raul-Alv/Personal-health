<template>
  <div class="export-page">
    <div class="export-card">
      <div class="export-header">
        <p class="export-eyebrow">Exportacion</p>
        <h1 class="export-title">Exportar datos clinicos</h1>
        <p class="export-copy">
          Selecciona un paciente y el conjunto de datos que quieres descargar en formato RDF junto con el esquema ShEx de validacion.
        </p>
      </div>

      <div class="selector-row">
        <label class="section-title" for="selected-patient">Selecciona un paciente</label>
        <select id="selected-patient" v-model="selectedPatient" @change="loadPatientData" class="patient-select">
          <option disabled value="">Elige un paciente</option>
          <option v-for="p in pacientes" :key="p.id" :value="p.id">
            {{ p.nombre }} {{ p.apellido }}
          </option>
        </select>
      </div>

      <div v-if="selectedPatient" class="export-section">
        <h2 class="section-title">Datos disponibles para exportar</h2>

        <div class="selection-box">
          <div class="toggle-row">
            <input
              type="checkbox"
              id="incluir-paciente"
              v-model="incluirPaciente"
            />
            <label for="incluir-paciente">
              Incluir datos del paciente en la exportacion
            </label>
          </div>
          <p class="toggle-help">
            Si esta activado, se anadiran los datos personales del paciente junto con los elementos seleccionados.
          </p>
        </div>

        <p v-if="!hasExportableItems" class="empty-state">
          No hay intervenciones ni alergias disponibles para este paciente.
        </p>

        <template v-else>
          <div class="selection-actions">
            <button @click="selectAll" class="selection-btn">Seleccionar todo</button>
            <button @click="deselectAll" class="selection-btn">Deseleccionar todo</button>
          </div>

          <div class="selection-groups">
            <section v-if="procedimientos.length" class="selection-group">
              <div class="selection-group-header">
                <h3 class="section-title">Intervenciones ({{ procedimientos.length }})</h3>
                <div class="selection-group-actions">
                  <button @click="selectAllProcedimientos" class="selection-link-btn">Todos</button>
                  <button @click="deselectAllProcedimientos" class="selection-link-btn">Ninguno</button>
                </div>
              </div>

              <ul class="selection-list">
                <li
                  v-for="(item, index) in procedimientos"
                  :key="getProcedureId(item, index)"
                  class="selection-item"
                >
                  <input
                    type="checkbox"
                    v-model="procedimientosSeleccionados"
                    :value="getProcedureId(item, index)"
                    :id="`procedure-${index}`"
                  />
                  <label :for="`procedure-${index}`" class="selection-label">
                    {{ formatProcedureLabel(item, index) }}
                  </label>
                </li>
              </ul>
            </section>

            <section v-if="alergias.length" class="selection-group">
              <div class="selection-group-header">
                <h3 class="section-title">Alergias ({{ alergias.length }})</h3>
                <div class="selection-group-actions">
                  <button @click="selectAllAlergias" class="selection-link-btn">Todas</button>
                  <button @click="deselectAllAlergias" class="selection-link-btn">Ninguna</button>
                </div>
              </div>

              <ul class="selection-list">
                <li
                  v-for="(item, index) in alergias"
                  :key="getAllergyId(item, index)"
                  class="selection-item"
                >
                  <input
                    type="checkbox"
                    v-model="alergiasSeleccionadas"
                    :value="getAllergyId(item, index)"
                    :id="`allergy-${index}`"
                  />
                  <label :for="`allergy-${index}`" class="selection-label">
                    {{ formatAllergyLabel(item, index) }}
                  </label>
                </li>
              </ul>
            </section>
          </div>
        </template>

        <div class="summary">
          <p class="selection-count">Elementos seleccionados: {{ totalSeleccionados }}</p>
          <p>Intervenciones: {{ procedimientosSeleccionados.length }} | Alergias: {{ alergiasSeleccionadas.length }}</p>
          <p>Datos del paciente: {{ incluirPaciente ? 'incluidos' : 'no incluidos' }}</p>
        </div>

        <button
          @click="exportarSeleccionados"
          :disabled="totalSeleccionados === 0"
          class="export-btn"
        >
          Exportar seleccion ({{ totalSeleccionados }})
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
  procedimientosSeleccionados,
  alergiasSeleccionadas,
  incluirPaciente,
  totalSeleccionados,
  hasExportableItems,
  getProcedureId,
  getAllergyId,
  formatProcedureLabel,
  formatAllergyLabel,
  loadPatientData,
  selectAllProcedimientos,
  deselectAllProcedimientos,
  selectAllAlergias,
  deselectAllAlergias,
  selectAll,
  deselectAll,
  exportarSeleccionados
} = useExportView()
</script>

<style scoped src="@/styles/views/ExportView.css"></style>
