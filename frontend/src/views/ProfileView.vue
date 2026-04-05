<template>
  <div class="page">
    <section class="card profile-card">
      <div class="card-header">
        <div>
          <p class="eyebrow">Mi perfil</p>
          <h1>{{ user.nombre || 'Usuario' }}</h1>
        </div>

        <div class="actions">
          <button
            class="btn btn-danger"
            @click="logout"
          >
            Cerrar sesión
          </button>
          <button
            v-if="!isEditing"
            class="btn btn-primary"
            @click="startEdit"
          >
            Editar
          </button>

          <template v-else>
            <button
              class="btn btn-success"
              :disabled="saving"
              @click="saveEdit"
            >
              {{ saving ? 'Guardando...' : 'Guardar' }}
            </button>
            <button
              class="btn btn-secondary"
              :disabled="saving"
              @click="cancelEdit"
            >
              Cancelar
            </button>
          </template>
        </div>
      </div>

      <p v-if="error" class="message message-error">{{ error }}</p>
      <p v-if="success" class="message message-success">{{ success }}</p>

      <div class="profile-grid">
        <div class="form-row">
          <label>Nombre</label>
          <template v-if="isEditing">
            <input v-model="edited.nombre" type="text" class="input" />
          </template>
          <template v-else>
            <div class="value">{{ user.nombre || '-' }}</div>
          </template>
        </div>

        <div class="form-row">
          <label>Email</label>
          <template v-if="isEditing">
            <input v-model="edited.email" type="email" class="input" />
          </template>
          <template v-else>
            <div class="value">{{ user.email || '-' }}</div>
          </template>
        </div>

        <div v-if="isEditing" class="form-row">
          <label>Contraseña</label>
          <button class="btn btn-outline" type="button" @click="openPasswordModal">
            Cambiar contraseña
          </button>
          <small v-if="passwordChanged" class="helper-text success-text">
            Se cambiará la contraseña al guardar el perfil.
          </small>
        </div>
      </div>

      <div v-if="defaultPatient" class="related-section">
        <div class="section-header">
          <h2>Paciente predeterminado</h2>
        </div>

        <button class="default-patient-card" @click="goToPatient(defaultPatient.id)">
          <span class="default-badge">Predeterminado</span>
          <strong>{{ defaultPatient.nombre }} {{ defaultPatient.apellido }}</strong>
        </button>
      </div>

      <div v-if="!patients.length || otherPatients.length || isEditing" class="related-section">
        <div class="section-header">
          <h2>{{ patients.length ? 'Otros pacientes' : 'Paciente principal' }}</h2>
          <p v-if="isEditing && patients.length" class="section-help">
            Pulsa la estrella para convertir un paciente en predeterminado.
          </p>
          <p v-else-if="!patients.length" class="section-help">
            Importa tu paciente principal para empezar.
          </p>
        </div>

        <div class="patient-list">
          <div
            v-for="patient in otherPatients"
            :key="patient.id"
            class="patient-item"
          >
            <button
              v-if="isEditing"
              class="star-btn"
              type="button"
              title="Poner como predeterminado"
              @click.stop="askSetDefault(patient)"
            >
              ★
            </button>

            <button
              class="patient-chip"
              @click="goToPatient(patient.id)"
            >
              {{ patient.nombre }} {{ patient.apellido }}
            </button>
          </div>
          <button
            v-if="!patients.length"
            class="add-patient-btn"
            type="button"
            title="Importar paciente principal"
            @click="openImportModal"
          >
            +
          </button>
        </div>
      </div>
    </section>

    <div v-if="showPasswordModal" class="modal-overlay" @click.self="closePasswordModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Cambiar contraseña</h3>
          <button class="modal-close" @click="closePasswordModal">×</button>
        </div>

        <div class="modal-body">
          <div class="form-row">
            <label>Nueva contraseña</label>
            <input
              v-model="passwordForm.newPassword"
              type="password"
              class="input"
              placeholder="Introduce la nueva contraseña"
            />
          </div>

          <div class="form-row">
            <label>Confirmar contraseña</label>
            <input
              v-model="passwordForm.confirmPassword"
              type="password"
              class="input"
              placeholder="Repite la nueva contraseña"
            />
          </div>

          <p v-if="passwordError" class="message message-error">
            {{ passwordError }}
          </p>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="closePasswordModal">
            Cancelar
          </button>
          <button class="btn btn-primary" @click="confirmPasswordChange">
            Confirmar
          </button>
        </div>
      </div>
    </div>

    <div v-if="showDefaultModal && pendingDefaultPatient" class="modal-overlay" @click.self="closeDefaultModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Cambiar paciente predeterminado</h3>
          <button class="modal-close" @click="closeDefaultModal">×</button>
        </div>

        <div class="modal-body">
          <p>
            ¿Quieres poner a
            <strong>{{ pendingDefaultPatient.nombre }} {{ pendingDefaultPatient.apellido }}</strong>
            como perfil predeterminado?
          </p>
          <p v-if="defaultPatient">
            <strong>{{ defaultPatient.nombre }} {{ defaultPatient.apellido }}</strong>
            pasará a la lista de otros pacientes.
          </p>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="closeDefaultModal">
            Cancelar
          </button>
          <button class="btn btn-primary" @click="confirmSetDefaultPatient">
            Aceptar
          </button>
        </div>
      </div>
    </div>

    <div v-if="showImportModal" class="modal-overlay" @click.self="closeImportModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Importar paciente</h3>
          <button class="modal-close" @click="closeImportModal">×</button>
        </div>

        <div class="modal-body">
          <div class="form-row">
            <label>Archivo TTL del paciente</label>
            <input
              class="input"
              type="file"
              accept=".ttl,text/turtle"
              @change="handleImportFileChange"
            />
          </div>

          <p v-if="selectedImportFiles.length" class="helper-text">
            Archivo seleccionado: {{ selectedImportFiles.map(file => file.name).join(', ') }}
          </p>

          <p v-if="importError" class="message message-error">
            {{ importError }}
          </p>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" :disabled="importing" @click="closeImportModal">
            Cancelar
          </button>
          <button
            class="btn btn-primary"
            :disabled="importing || !selectedImportFiles.length"
            @click="confirmImportPatient"
          >
            {{ importing ? 'Importando...' : 'Importar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useProfileView } from '@/scripts/views/profileView'

const {
  user,
  edited,
  patients,
  isEditing,
  saving,
  error,
  success,
  showPasswordModal,
  passwordChanged,
  passwordError,
  showDefaultModal,
  pendingDefaultPatient,
  showImportModal,
  selectedImportFiles,
  importing,
  importError,
  passwordForm,
  defaultPatient,
  otherPatients,
  startEdit,
  cancelEdit,
  openPasswordModal,
  closePasswordModal,
  confirmPasswordChange,
  askSetDefault,
  closeDefaultModal,
  confirmSetDefaultPatient,
  openImportModal,
  closeImportModal,
  handleImportFileChange,
  confirmImportPatient,
  saveEdit,
  goToPatient,
  logout
} = useProfileView()
</script>

<style scoped src="@/styles/views/ProfileView.css"></style>
