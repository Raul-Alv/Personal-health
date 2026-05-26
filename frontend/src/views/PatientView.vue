<template>
  <div class="page">
    <div
      v-if="isEditing"
      class="overlay"
    ></div>
    <div class="container">
      <section class="details">
        <header class="header">
          <svg class="avatar" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2c-3.3 0-10 1.7-10 5v3h20v-3c0-3.3-6.7-5-10-5z"/>
          </svg>
          <h1 class="name">{{ patient.nombre }} {{ patient.apellido }}</h1>
        </header>
        <hr class="divider-horizontal" />

        <button
          v-if="!isEditing"
          @click="startEdit"
          class="btn edit-btn"
        >
          Editar
        </button>

        <div v-else class="edit-actions">
          <button
            @click="openConfirmSave"
            class="btn save-btn"
          >
            Guardar
          </button>
          <button
            @click="cancelEdit"
            class="btn cancel-btn"
          >
            Cancelar
          </button>
        </div>

        <p v-if="error" class="page-error">{{ error }}</p>

        <div class="field">
          <label>Género:</label>
          <template v-if="isEditing">
            <select v-model="edited.genero" class="editable-field editable-select">
              <option
                v-for="option in genderOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </template>
          <span
            v-else
            class="editable-field"
          >{{ genderLabel }}</span>
        </div>
        <div class="field">
          <label>Fecha de nacimiento:</label>
          <span
            :contenteditable="isEditing"
            @input="onInput('fecha_nacimiento', $event)"
            class="editable-field"
          >{{ patient.fecha_nacimiento }}</span>
        </div>
        <div class="field">
          <label>Estado civil:</label>
          <template v-if="isEditing">
            <select v-model="edited.estado_civil" class="editable-field editable-select">
              <option
                v-for="option in maritalStatusOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </template>
          <span
            v-else
            class="editable-field"
          >{{ maritalStatusLabel }}</span>
        </div>
        <div class="field ssn-field">
          <label>Seguridad Social:</label>
          <span
            :contenteditable="isEditing"
            @input="onInput('ssn', $event)"
            class="editable-field"
          >{{ showSSN ? patient.ssn : maskedSSN }}</span>
          <button class="eye-btn" @click="showSSN = !showSSN" :aria-label="showSSN ? 'Ocultar' : 'Mostrar'">
            <svg v-if="!showSSN" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 5c-7.633 0-11 6.5-11 6.5s3.367 6.5 11 6.5 11-6.5 11-6.5S19.633 5 12 5zm0 11a4.5 4.5 0 110-9 4.5 4.5 0 010 9z"/>
              <path d="M12 9a3 3 0 100 6 3 3 0 000-6z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7zM12 17c2.761 0 5-2.239 5-5 0-.768-.18-1.494-.5-2.142L9.142 14.5A4.98 4.98 0 0012 17zm-5-5c0 .768.18 1.494.5 2.142l7.358-7.358A4.98 4.98 0 0012 7c-2.761 0-5 2.239-5 5z"/>
            </svg>
          </button>
        </div>

        <fieldset class="address">
          <legend>Dirección</legend>
          <div class="subfield">
            <label>Calle:</label>
            <span
              :contenteditable="isEditing"
              @input="onInput('calle', $event)"
              class="editable-field"
            >{{ patient.address.calle }}</span>
          </div>
          <div class="subfield">
            <label>CP:</label>
            <span
              :contenteditable="isEditing"
              @input="onInput('cp', $event)"
              class="editable-field"
            >{{ patient.address.cp }}</span>
          </div>
          <div class="subfield">
            <label>Ciudad:</label>
            <span
              :contenteditable="isEditing"
              @input="onInput('ciudad', $event)"
              class="editable-field"
            >{{ patient.address.ciudad }}</span>
          </div>
          <div class="subfield">
            <label>Provincia:</label>
            <span
              :contenteditable="isEditing"
              @input="onInput('provincia', $event)"
              class="editable-field"
            >{{ patient.address.provincia }}</span>
          </div>
          <div class="subfield">
            <label>País:</label>
            <span
              :contenteditable="isEditing"
              @input="onInput('pais', $event)"
              class="editable-field"
            >{{ patient.address.pais }}</span>
          </div>
        </fieldset>
      </section>

      <div class="divider-vertical"></div>

      <aside class="actions">
        <button
          class="btn secondary"
          @click="goProcedures"
          :disabled="isEditing"
        >
          Ver procedimientos
        </button>

        <button
          class="btn secondary"
          @click="goAllergies"
          :disabled="isEditing"
        >
          Ver alergias
        </button>

        <button
          class="btn primary"
          @click="doExport"
          :disabled="isEditing"
        >
          Exportar
        </button>
      </aside>
    </div>
  </div>

  <div v-if="showSaveConfirm" class="modal-backdrop">
    <div class="modal-box">
      <h3>Confirmar cambios</h3>
      <p>¿Quieres guardar los cambios de este perfil?</p>
      <div class="modal-actions">
        <button class="btn save-btn" @click="confirmSave">Sí, guardar</button>
        <button class="btn cancel-btn" @click="showSaveConfirm = false">No</button>
      </div>
    </div>
  </div>

  <div v-if="showSavedMessage" class="modal-backdrop">
    <div class="modal-box">
      <h3>Cambios guardados</h3>
      <p>El perfil se ha actualizado correctamente.</p>
      <div class="modal-actions">
        <button class="btn save-btn" @click="showSavedMessage = false">Aceptar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { usePatientView } from '@/scripts/views/patientView'

const props = defineProps({
  patient_id: { type: String, required: true }
})

const {
  genderOptions,
  maritalStatusOptions,
  patient,
  edited,
  showSSN,
  error,
  isEditing,
  showSaveConfirm,
  showSavedMessage,
  maskedSSN,
  genderLabel,
  maritalStatusLabel,
  startEdit,
  openConfirmSave,
  onInput,
  confirmSave,
  cancelEdit,
  goProcedures,
  goAllergies,
  doExport
} = usePatientView(props)
</script>

<style scoped src="@/styles/views/PatientView.css"></style>
