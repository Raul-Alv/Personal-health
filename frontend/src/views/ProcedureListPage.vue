<template>
  <div class="page">
    <div class="ppv-content">
      <div class="ppv-layout">
        <section class="ppv-main">
          <div class="ppv-main-header">
            <div>
              <p class="ppv-kicker">Actividad clínica</p>
              <h1>Procedimientos</h1>
              <p class="ppv-main-copy">
                Consulta el historial del paciente y filtra los resultados por nombre, fecha, profesional o diente.
              </p>
            </div>
            <span class="ppv-counter">{{ procedures.length }} resultado<span v-if="procedures.length !== 1">s</span></span>
          </div>

          <div class="ppv-list">
            <div
              v-for="proc in procedures"
              :key="proc.procedure_uri"
              class="ppv-item-wrapper"
            >
              <div
                class="ppv-item"
                @click="selectProcedure(proc)"
              >
                <div class="ppv-item-title">{{ proc.text || 'Procedimiento sin nombre' }}</div>
                <div class="ppv-item-meta">
                  <span class="ppv-item-code">{{ proc.code || '-' }}</span>
                  <span class="ppv-item-date">{{ proc.performedDateTime || '-' }}</span>
                </div>
                <div v-if="proc.notes" class="ppv-item-notes">
                  <span class="ppv-item-notes-label">Notas</span>
                  <span>{{ proc.notes }}</span>
                </div>
              </div>
              <button
                class="ppv-delete-btn"
                @click.stop="deleteProcedure(proc)"
                title="Eliminar procedimiento"
                type="button"
              >
                <Trash2 :size="16" />
              </button>
            </div>

            <div v-if="loading" class="ppv-loading">Cargando...</div>
            <div v-else-if="error" class="ppv-error">Error al cargar</div>
            <div
              v-else-if="!procedures.length"
              class="ppv-empty"
            >
              {{
                showingFilteredResults
                  ? 'No hay procedimientos que coincidan con los filtros.'
                  : 'No hay procedimientos para este paciente.'
              }}
            </div>
          </div>
        </section>

        <aside class="ppv-sidebar">
          <div class="ppv-sidebar-card">
            <div class="ppv-sidebar-header">
              <h2>Filtros</h2>
              <p>Busca por nombre, fecha, profesional o diente con filtros sobre los datos clínicos.</p>
            </div>

            <form class="ppv-filter-form" @submit.prevent="applyFilters">
              <label class="ppv-filter-group">
                <span class="ppv-filter-label">Nombre</span>
                <input
                  v-model="filters.nombre"
                  class="ppv-filter-input"
                  type="text"
                  placeholder="Ej. Extracción"
                >
              </label>

              <label class="ppv-filter-group">
                <span class="ppv-filter-label">Fecha</span>
                <input
                  v-model="filters.fecha"
                  class="ppv-filter-input"
                  type="text"
                  placeholder="Ej. 2026-04-27"
                >
              </label>

              <label class="ppv-filter-group">
                <span class="ppv-filter-label">Profesional</span>
                <input
                  v-model="filters.practicante"
                  class="ppv-filter-input"
                  type="text"
                  placeholder="Ej. Practitioner/123"
                >
              </label>

              <label class="ppv-filter-group">
                <span class="ppv-filter-label">Diente</span>
                <input
                  v-model="filters.diente"
                  class="ppv-filter-input"
                  type="text"
                  placeholder="Ej. 11 o incisivo"
                >
              </label>

              <div class="ppv-sidebar-actions">
                <button
                  class="ppv-btn"
                  type="submit"
                  :disabled="loading"
                >
                  Buscar
                </button>
                <button
                  class="ppv-btn ppv-btn-secondary"
                  type="button"
                  :disabled="loading || (!hasActiveFilters && !showingFilteredResults)"
                  @click="clearFilters"
                >
                  Borrar filtros
                </button>
              </div>
            </form>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Trash2 } from 'lucide-vue-next'
import { useProcedureListPageView } from '@/scripts/views/procedureListPageView'

const props = defineProps({
  patient_id: {
    type: [String, Number],
    required: true
  }
})

const {
  procedures,
  loading,
  error,
  filters,
  hasActiveFilters,
  showingFilteredResults,
  applyFilters,
  clearFilters,
  deleteProcedure,
  selectProcedure
} = useProcedureListPageView(props)
</script>

<style scoped src="@/styles/views/ProcedureListPage.css"></style>
