<template>
  <div class="page">
    <div class="ppv-content">
      <div class="ppv-list">
        <div
          v-for="proc in procedures"
          :key="proc.id"
          class="ppv-item-wrapper"
        >
          <div
            class="ppv-item"
            @click="selectProcedure(proc)"
          >
            <div class="ppv-item-title">{{ proc.text }}</div>
            <div class="ppv-item-meta">
              <span class="ppv-item-code">{{ proc.code }}</span>
              <span class="ppv-item-date">{{ proc.date }}</span>
            </div>
          </div>
          <button
            class="ppv-delete-btn"
            @click.stop="deleteProcedure(proc)"
            title="Eliminar procedimiento"
          >
            X
          </button>
        </div>
        <div v-if="loading" class="ppv-loading">Cargando...</div>
        <div v-if="error" class="ppv-error">Error al cargar</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useProcedureListPageView } from '@/scripts/views/procedureListPageView'

const props = defineProps({
  patient_id: {
    type: [String, Number],
    required: true
  }
})

const { procedures, loading, error, deleteProcedure, selectProcedure } =
  useProcedureListPageView(props)
</script>

<style scoped src="@/styles/views/ProcedureListPage.css"></style>
