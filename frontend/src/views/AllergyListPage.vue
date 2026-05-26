<template>
  <div class="ppv-container">
    <div class="ppv-list-header">
      <div>
        <p class="ppv-kicker">Seguimiento clínico</p>
        <h1>Alergias</h1>
        <p class="ppv-main-copy">
          Revisa las alergias registradas del paciente y accede rápidamente a sus datos principales.
        </p>
      </div>
      <span class="ppv-counter">{{ allergies.length }} registro<span v-if="allergies.length !== 1">s</span></span>
    </div>

    <div class="ppv-list">
      <div
        v-for="al in allergies"
        :key="al.id"
        class="ppv-item"
        @click="selectAllergy(al)"
      >
        <div class="ppv-item-title">{{ al.display }}</div>
        <div class="ppv-item-meta">
          <span class="ppv-item-code">{{ al.code }}</span>
          <span class="ppv-item-date">{{ al.onsetDateTime }}</span>
        </div>
      </div>
      <div v-if="loading" class="ppv-loading">Cargando...</div>
      <div v-if="error" class="ppv-error">Error al cargar</div>
      <div v-else-if="!allergies.length" class="ppv-empty">No hay alergias registradas para este paciente.</div>
    </div>
  </div>
</template>

<script setup>
import { useAllergyListPageView } from '@/scripts/views/allergyListPageView'

const props = defineProps({
  patient_id: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['back', 'select'])

const { allergies, loading, error, selectAllergy } = useAllergyListPageView(props, emit)
</script>

<style scoped src="@/styles/views/AllergyListPage.css"></style>
