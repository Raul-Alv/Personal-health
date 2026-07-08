<template>
  <div class="procedure-detail-layout">
    <div class="procedure-backbar">
      <button class="back-btn" @click="goBack">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="22"
          height="22"
          fill="currentColor"
          viewBox="0 0 16 16"
        >
          <path
            fill-rule="evenodd"
            d="M15 8a.5.5 0 0 1-.5.5H2.707l3.147 3.146a.5.5 0 0 1-.708.708l-4-4a.5.5 0 0 1 0-.708l4-4a.5.5 0 1 1 .708.708L2.707 7.5H14.5A.5.5 0 0 1 15 8z"
          />
        </svg>
        <span>Volver a la lista</span>
      </button>
    </div>

    <div class="procedure-main">
      <section class="procedure-data-panel">
        <div class="panel-header">
          <h1 class="detail-title">
            Intervención <span v-if="procedure_id">#{{ procedure_id }}</span>
          </h1>

          <div class="panel-actions">
            <button class="icon-btn" @click="confirmDelete = true" title="Eliminar intervención" type="button">
              <Trash2 :size="16" />
              Eliminar
            </button>
          </div>
        </div>

        <div class="field-grid">
          <div class="field-card">
            <span class="label">Intervención</span>
            <div class="detail-value">{{ procedures[0]?.description || procedures[0]?.text || '-' }}</div>
          </div>

          <div class="field-card">
            <span class="label">Fecha</span>
            <div class="detail-value">{{ procedures[0]?.performedDateTime || '-' }}</div>
          </div>

          <div class="field-card">
            <span class="label">Estado</span>
            <div class="detail-value">{{ procedureStatusLabel }}</div>
          </div>

          <div class="field-card">
            <span class="label">Profesional responsable</span>
            <div class="detail-value">{{ procedures[0]?.performerRef || '-' }}</div>
          </div>

          <div class="field-card field-card-full">
            <span class="label">Notas</span>
            <div class="detail-value">{{ procedures[0]?.notes || 'Sin notas registradas' }}</div>
          </div>

          <div class="field-card field-card-full">
            <span class="label">URI</span>
            <div class="detail-value monospace">{{ procedures[0]?.procedure_uri || '-' }}</div>
          </div>
        </div>

        <div class="panel-actions">
          <button class="action-btn" @click="onExport" type="button">Ir a exportación</button>
        </div>
      </section>

      <aside class="dental-map-panel">
        <div class="dental-map-box">
          <h2 class="section-title">Mapa dental</h2>
          <p class="section-subtitle">
            {{
              hasDentalData
                ? `Pieza dental asociada: ${procedures[0]?.dienteDisplay || activeTeeth.join(', ')}`
                : 'Sin pieza dental asociada a esta intervención.'
            }}
          </p>

          <div class="dental-svg-container">
            <div ref="icono" class="svg-fluid" v-html="dentalSvgMarkup"></div>
          </div>

          <div class="legend">
            <span class="legend-item">
              <span class="legend-dot legend-danger"></span> Operado
            </span>
            <span class="legend-item">
              <span class="legend-dot legend-secondary"></span> Sin intervención
            </span>
          </div>
        </div>
      </aside>
    </div>

    <div v-if="confirmDelete" class="modal-backdrop">
      <div class="modal-dialog-centered">
        <div class="modal-content">
          <h3 class="modal-title">Eliminar intervención</h3>
          <p class="modal-text">
            Esta acción no se puede deshacer. ¿Seguro que quieres eliminar esta intervención?
          </p>
          <div class="modal-footer">
            <button class="action-btn action-btn-secondary" @click="confirmDelete = false" type="button">Cancelar</button>
            <button class="action-btn action-btn-danger" @click="onDelete" type="button">Eliminar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Trash2 } from 'lucide-vue-next'
import {
  dentalSvgMarkup,
  useProcedureDetailView
} from '@/scripts/views/procedureDetailView'

const props = defineProps({
  patient_id: {
    type: [String, Number],
    required: true
  },
  procedure_id: {
    type: [String, Number],
    required: true
  }
})

const { icono, procedures, activeTeeth, hasDentalData, procedureStatusLabel, confirmDelete, onExport, onDelete, goBack } =
  useProcedureDetailView(props)
</script>

<style scoped src="@/styles/views/ProcedureDetail.css"></style>
