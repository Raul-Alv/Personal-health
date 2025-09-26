<template>
  <div class="procedure-detail-layout">
    <!-- Panel izquierdo: Datos del procedimiento -->
    <button class="btn btn-link back-btn align-self-start mb-3 fixed-back-btn" @click="goBack">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" class="bi bi-arrow-left" viewBox="0 0 16 16">
          <path fill-rule="evenodd" d="M15 8a.5.5 0 0 1-.5.5H2.707l3.147 3.146a.5.5 0 0 1-.708.708l-4-4a.5.5 0 0 1 0-.708l4-4a.5.5 0 1 1 .708.708L2.707 7.5H14.5A.5.5 0 0 1 15 8z"/>
        </svg>
        <span class="ms-2">Vuelta a la lista</span>
      </button>

    <section class="procedure-data-panel card">
      <div class="d-flex align-items-center mb-3 gap-2 justify-content-between">
        <h1 class="mb-0 fs-5 fw-semibold">Procedimiento <span v-if="procedure_id">#{{ procedure_id }}</span></h1>
        <div class="d-flex gap-2">
          <!-- <button class="icon-btn" @click="onEdit" title="Editar">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16">
              <path d="M12.146.854a.5.5 0 0 1 .708 0l2.292 2.292a.5.5 0 0 1 0 .708l-9.439 9.439a.5.5 0 0 1-.168.11l-4 1.5a.5.5 0 0 1-.65-.65l1.5-4a.5.5 0 0 1 .11-.168l9.439-9.439zm.708-.708a1.5 1.5 0 0 0-2.121 0l-9.439 9.439a1.5 1.5 0 0 0-.329.497l-1.5 4a1.5 1.5 0 0 0 1.95 1.95l4-1.5a1.5 1.5 0 0 0 .497-.329l9.439-9.439a1.5 1.5 0 0 0 0-2.121l-2.292-2.292z"/>
            </svg>
          </button> -->
          <button class="icon-btn text-danger" @click="confirmDelete = true" title="Borrar">
            🗑️
          </button>
        </div>
      </div>
      <div class="row g-3">
        <div class="col-6">
          <div class="label">Procedimiento</div>
          <div class="fw-semibold">{{ procedures[0]?.description || procedures[0]?.text || '—' }}</div>
        </div>
        <div class="col-6">
          <div class="label">Fecha</div>
          <div class="fw-semibold">{{ procedures[0]?.performedDateTime || '—' }}</div>
        </div>
        <div class="col-6">
          <div class="label">Estado</div>
          <div class="fw-semibold">{{ procedures[0]?.status || '—' }}</div>
        </div>
        <div class="col-6">
          <div class="label">Doctor</div>
          <div class="fw-semibold">{{ procedures[0]?.performerRef || '—' }}</div>
        </div>
        <div class="col-12">
          <div class="label">Notas</div>
          <div class="fw-semibold">{{ procedures[0]?.notes || 'Aquí van las notas' }}</div>
        </div>
        <div class="col-12">
          <div class="label">URI</div>
          <div class="font-monospace small text-break">{{ procedures[0]?.procedure_uri || '—' }}</div>
        </div>
      </div>
      <div class="d-flex justify-content-end gap-2 mt-4">
        <button class="btn btn-outline-secondary" @click="onExport">Exportar</button>
      </div>
    </section>

    <!-- Panel derecho: Mapa dental -->
    <aside class="dental-map-panel d-flex flex-column align-items-center justify-content-center">
      
      <div class="dental-map-box d-flex flex-column align-items-center justify-content-center flex-grow-1">
        <h2 class="section-title mb-3">Mapa dental</h2>
        <div class="dental-svg-container">
          <DentaduraIconoSvg ref="icono" class="svg-fluid" />
        </div>
        <div class="d-flex gap-3 mt-3 text-muted small">
          <span class="d-flex align-items-center gap-1"><span class="legend-dot bg-danger"></span> Operado</span>
          <span class="d-flex align-items-center gap-1"><span class="legend-dot bg-secondary"></span> Sin intervención</span>
        </div>
      </div>
    </aside>

    <!-- Confirm Delete Modal -->
    <div v-if="confirmDelete" class="modal-backdrop">
      <div class="modal-dialog-centered">
        <div class="modal-content p-4">
          <h3 class="fs-5 fw-semibold mb-2">Borrar procedimiento</h3>
          <p class="mb-4 text-muted">Esta acción no se puede deshacer. ¿Seguro que quieres eliminarlo?</p>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-outline-secondary" @click="confirmDelete = false">Cancelar</button>
            <button class="btn btn-danger" @click="onDelete">Borrar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DentaduraIconoSvg from '@/assets/Human_dental_arches.svg?component'
import api from '@/api/axios'
import { useRouter } from 'vue-router'

const icono = ref(null)
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
const router = useRouter()
const selectedIso = ref(null)
const procedures = ref([])
const loading    = ref(false)
const error      = ref(false)
const confirmDelete = ref(false)

function pintarDientes() {
  // Aquí puedes manejar el click en el diente
}

async function fetchTooth() {
  loading.value = true
  error.value   = false
  try {
    const resp = await api.get(
      `/mis_pacientes/${props.patient_id}/get/procedimientos/${props.procedure_id}`
    )
    procedures.value = resp.data
    if (procedures.value.length > 0) {  
      selectedIso.value = procedures.value[0].dienteCode
      setTimeout(() => {
        const grupo = document.getElementsByClassName(`${selectedIso.value}`)
        if (grupo.length > 0) {
          grupo[0].setAttribute('fill', '#FF0000')
          grupo[0].addEventListener('click', pintarDientes)
        }
      }, 100)
    }
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
}

function onExport() {
  // Implementa la lógica de exportación
}
function onDelete() {
  // Implementa la lógica de borrado
  api.delete(`/mis_pacientes/${props.patient_id}/delete/procedimientos/${props.procedure_id}`)
    .then(() => {
      goBack()
    })
    .catch((e) => {
      console.error('Error al borrar el procedimiento:', e)
    })
  confirmDelete.value = false
}
function goBack() {
  router.push(`/patient/${props.patient_id}/procedimientos`) // Cambia el nombre de la ruta si es diferente
}

onMounted(() => {
  fetchTooth()
})
</script>

<style>
.procedure-detail-layout {
  display: flex;
  flex-direction: row;
  height: 100vh;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  overflow: hidden;
}

.procedure-data-panel {
  flex: 4;      /* <-- Fijo: 420px de ancho */
  /*max-width: 420px;*/
  /*min-width: 340px;*/
  background: var(--sidebar-card);
  border-radius: 18px;
  margin: 32px 0 32px 32px;
  padding: 32px 32px 24px 32px;
  box-shadow: 0 2px 12px rgba(30,41,59,0.06);
  border: 1px solid var(--sidebar-border);
  display: flex;
  flex-direction: column;
  /*min-width: 0;*/
}

.dental-map-panel {
  flex: 6;         /* <-- Ahora ocupa todo el espacio restante */
  /*min-width: 0;*/
  background: var(--sidebar-bg);
  border-left: 2px solid var(--sidebar-border);
  padding: 32px 18px 32px 18px;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
  overflow: hidden;
}

.dental-map-box {
  background: var(--sidebar-card);
  border-radius: 18px;
  box-shadow: 0 2px 12px rgba(30,41,59,0.06);
  padding: 24px 12px 18px 12px;
  width: 100%;
  height: 100%;
  border: 1px solid var(--sidebar-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.dental-svg-container {
  width: 100%;
  height: 100%;
  aspect-ratio: 1/1;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  /* Añade esto para centrar el SVG */
  position: relative;
}
.svg-fluid {
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
  display: block;
  /* Centrado extra si el SVG tiene mucho espacio en blanco */
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

@media (orientation: portrait) {
  .detail-procedure-layout {
    flex-direction: column;   /* Se apilan */
    overflow: auto;           /* Permite scroll */
  }

  .detail-procedure-layout section,
  .detail-procedure-layout aside {
    flex: none;               
    height: auto;             /* Si se ajusta en la contención */
  }
}

.legend-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
  margin-right: 4px;
}

.bg-danger { background: var(--sidebar-accent) !important; }
.bg-secondary { background: var(--sidebar-muted) !important; }

.back-btn {
  color: var(--sidebar-muted);
  font-weight: 500;
  font-size: 1rem;
  text-decoration: none;
  background: none;
  border: none;
  padding: 0;
  transition: color .15s;
}
.back-btn:hover { color: var(--sidebar-accent); }

.label {
  color: var(--sidebar-muted);
  font-weight: 500;
  font-size: 0.97rem;
  margin-bottom: 2px;
}

.icon-btn {
  background: none;
  border: none;
  padding: 4px;
  margin-right: 4px;
  color: var(--sidebar-muted);
  transition: color .15s;
  border-radius: 6px;
}
.icon-btn:hover {
  color: var(--sidebar-accent);
  background: #f1f5f9;
}

.icon-btn.text-danger:hover {
  color: #fff;
  background: var(--sidebar-accent);
}

.card {
  border-radius: 18px;
  border: 1px solid var(--sidebar-border);
  background: var(--sidebar-card);
  box-shadow: 0 2px 12px rgba(30,41,59,0.06);
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(30,41,59,0.55);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-dialog-centered {
  background: var(--sidebar-card);
  border-radius: 18px;
  box-shadow: 0 2px 24px rgba(30,41,59,0.18);
  max-width: 350px;
  width: 100%;
  padding: 0;
}
.modal-content {
  border-radius: 18px;
  background: var(--sidebar-card);
}

@media (max-width: 900px) {
  .procedure-detail-layout {
    flex-direction: column;
  }
  .procedure-data-panel,
  .dental-map-panel {
    max-width: 100%;
    min-width: 0;
    margin: 0;
    padding: 18px 8px 18px 8px;
    border-radius: 0;
    border: none;
  }
  .dental-map-panel {
    border-left: none;
    border-top: 2px solid var(--sidebar-border);
  }
  .dental-map-box {
    min-height: 220px;
  }
  .dental-svg-container {
    max-width: 220px;
  }
}
</style>
