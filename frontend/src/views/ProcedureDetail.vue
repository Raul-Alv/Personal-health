<template>
  <div v-if="loading">Cargando...</div>
  <div v-else-if="error">Error al cargar los procedimientos.</div>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <!-- Side Drawer -->
    <aside class="fixed inset-y-0 left-0 w-72 bg-white shadow-xl z-40 transform transition-transform duration-300"
      :class="drawerOpen ? 'translate-x-0' : '-translate-x-full'" role="dialog" aria-label="Menú lateral">
      <div class="h-16 flex items-center px-4 border-b">
        <span class="font-semibold text-lg">Menú</span>
        <button class="ml-auto p-2 rounded-lg hover:bg-gray-100" @click="closeDrawer" aria-label="Cerrar menú">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
            <path fill-rule="evenodd"
              d="M5.47 5.47a.75.75 0 011.06 0L12 10.94l5.47-5.47a.75.75 0 111.06 1.06L13.06 12l5.47 5.47a.75.75 0 11-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 01-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 010-1.06z"
              clip-rule="evenodd" />
          </svg>
        </button>
      </div>
      <nav class="p-4 space-y-1">
        <button class="w-full text-left px-3 py-2 rounded-xl hover:bg-gray-100">Perfil</button>
        <button class="w-full text-left px-3 py-2 rounded-xl hover:bg-gray-100">Pacientes</button>
        <button
          class="w-full text-left px-3 py-2 rounded-xl hover:bg-gray-100 font-semibold bg-gray-100">Procedimientos</button>
        <button class="w-full text-left px-3 py-2 rounded-xl hover:bg-gray-100">Alergias</button>
        <div class="h-px bg-gray-200 my-2"></div>
        <button class="w-full text-left px-3 py-2 rounded-xl hover:bg-gray-100">Ajustes</button>
        <button class="w-full text-left px-3 py-2 rounded-xl hover:bg-gray-100 text-red-600">Cerrar sesión</button>
      </nav>
    </aside>


    <!-- Header -->
    <header class="sticky top-0 z-20 bg-white/90 backdrop-blur border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center gap-3">
        <button class="p-2 rounded-xl hover:bg-gray-100" @click="toggleDrawer" aria-label="Abrir menú">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
            <path fill-rule="evenodd"
              d="M3.75 5.25a.75.75 0 000 1.5h16.5a.75.75 0 000-1.5H3.75zm0 6a.75.75 0 000 1.5h16.5a.75.75 0 000-1.5H3.75zm0 6a.75.75 0 000 1.5h16.5a.75.75 0 000-1.5H3.75z"
              clip-rule="evenodd" />
          </svg>
        </button>


        <div class="flex-1 min-w-0">
          <h1 class="text-lg sm:text-xl font-semibold truncate">
            Procedimiento <span v-if="procedure_id">#{{ procedure_id }}</span>
          </h1>
          <p v-if="proc?.name || proc?.text" class="text-sm text-gray-500 truncate">
            {{ proc?.name || proc?.text }}
          </p>
        </div>


        <div class="flex items-center gap-2">
          <button class="px-3 py-2 rounded-xl bg-gray-900 text-white hover:bg-black disabled:opacity-50"
            @click="onExport" :disabled="loading" title="Exportar">
            Exportar
          </button>
          <button class="p-2 rounded-xl hover:bg-gray-100" @click="onEdit" title="Editar" aria-label="Editar">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
              <path
                d="M21.731 2.269a2.625 2.625 0 00-3.712 0l-1.157 1.157 3.712 3.712 1.157-1.157a2.625 2.625 0 000-3.712z" />
              <path d="M3 17.25V21h3.75L19.78 7.97l-3.712-3.712L3 17.25z" />
            </svg>
          </button>
          <button class="p-2 rounded-xl hover:bg-red-50 text-red-600" @click="confirmDelete = true" title="Borrar"
            aria-label="Borrar">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
              <path fill-rule="evenodd"
                d="M9.75 3a.75.75 0 00-.75.75V5H6a.75.75 0 000 1.5h12A.75.75 0 0018 5h-3V3.75a.75.75 0 00-.75-.75h-4.5zM5.25 7.5A.75.75 0 016 6.75h12a.75.75 0 01.75.75v11.25A2.25 2.25 0 0116.5 21h-9A2.25 2.25 0 015.25 18.75V7.5z"
                clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </header>
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left: metadata cards -->
        <section class="lg:col-span-1 space-y-6">
          <div class="bg-white rounded-2xl shadow-sm ring-1 ring-black/5 p-5">
            <h2 class="text-base font-semibold mb-4">Datos del procedimiento</h2>
            <dl class="grid grid-cols-1 gap-4 text-sm">
              <div class="flex items-start justify-between gap-4">
                <dt class="text-gray-500">Fecha</dt>
                <dd class="font-medium text-right">{{ procedures[0]?.performedDateTime || '—' }}</dd>
              </div>
              <div class="flex items-start justify-between gap-4">
                <dt class="text-gray-500">Código</dt>
                <dd class="font-medium text-right">{{ procedures[0]?.code || '—' }}</dd>
              </div>
              <div class="flex items-start justify-between gap-4">
                <dt class="text-gray-500">Estado</dt>
                <dd class="font-medium text-right">{{ procedures[0]?.status || '—' }}</dd>
              </div>
              <div class="flex items-start justify-between gap-4">
                <dt class="text-gray-500">Descripción</dt>
                <dd class="font-medium text-right max-w-[16rem] sm:max-w-none">{{ procedures[0]?.description || procedures[0]?.text || '—'
                  }}</dd>
              </div>
              <div class="flex items-start justify-between gap-4">
                <dt class="text-gray-500">Doctor</dt>
                <dd class="font-medium text-right">{{ procedures[0]?.performerRef || '—' }}</dd>
              </div>
              <div class="flex items-start justify-between gap-4">
                <dt class="text-gray-500">URI</dt>
                <dd class="font-mono text-xs text-right break-all">{{ procedures[0]?.procedure_uri || '—' }}</dd>
              </div>
            </dl>
          </div>
        </section>
        <section class="lg:col-span-2">
          <div class="bg-white rounded-2xl shadow-sm ring-1 ring-black/5 p-5">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-base font-semibold">Mapa dental</h2>
              <div class="flex items-center gap-3 text-xs text-gray-500">
                <span class="inline-flex items-center gap-1"><span
                    class="inline-block w-3 h-3 rounded-sm bg-red-500"></span> Operado</span>
                <span class="inline-flex items-center gap-1"><span
                    class="inline-block w-3 h-3 rounded-sm bg-gray-300"></span> Sin intervención</span>
              </div>
            </div>
            <div class="w-full aspect-[16/9] bg-gray-50/60 rounded-xl grid place-items-center ring-1 ring-gray-200">
              <slot name="toothmap">
                <div class="text-center text-sm text-gray-500">
                  <DentaduraIconoSvg ref="icono" :width="1000" :height="1000" />
                </div>
              </slot>
            </div>
          </div>
        </section>
      </div>
    </main>
    
    <!-- Confirm Delete Modal -->
    <div v-if="confirmDelete" class="fixed inset-0 z-50 grid place-items-center">
      <div class="absolute inset-0 bg-black/40" @click="confirmDelete = false"></div>
      <div class="relative bg-white rounded-2xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold mb-2">Borrar procedimiento</h3>
        <p class="text-sm text-gray-600 mb-5">Esta acción no se puede deshacer. ¿Seguro que quieres eliminarlo?</p>
        <div class="flex justify-end gap-2">
          <button class="px-4 py-2 rounded-xl hover:bg-gray-100" @click="confirmDelete = false">Cancelar</button>
          <button class="px-4 py-2 rounded-xl bg-red-600 text-white hover:bg-red-700" @click="onDelete">Borrar</button>
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


const drawerOpen = ref(false)

function toggleDrawer() {
  drawerOpen.value = !drawerOpen.value
}

function closeDrawer() {
  drawerOpen.value = false
}

async function fetchTooth() {
  loading.value = true
  error.value   = false
  try {
    const resp = await api.get(
      `/mis_pacientes/${props.patient_id}/get/procedimientos/${props.procedure_id}`
    )
    // Asume que la respuesta es un array de { id, code, text, date }
    procedures.value = resp.data
    console.log('Procedimientos:', procedures.value)
    if (procedures.value.length > 0) {  
      // Aquí puedes manejar la lógica para seleccionar un diente
      // Por ejemplo, si el primer procedimiento tiene un código ISO
      selectedIso.value = procedures.value[0].dienteCode
      console.log('Diente seleccionado:', selectedIso.value)
      const grupo = document.getElementsByClassName(`${selectedIso.value}`)
            //.forEach(p=>p.setAttribute('fill', '#FF0000'))
      console.log('Grupo de dientes:', grupo)
      if (grupo.length > 0) {
        grupo[0].setAttribute('fill', '#FF0000') // Cambia el color del diente seleccionado
        grupo[0].addEventListener('click', pintarDientes)
      } else {

        console.warn(`No se encontró el grupo de dientes para el código ISO: ${selectedIso.value}`)
      }
    }
  } catch (e) {
    console.error(e)
    error.value = true
  } finally {
    loading.value = false
  }
}

function pintarDientes() {
  console.log('click en el SVG importado')
}

onMounted(fetchTooth)


</script>

<style>
/* ---------- Paleta y tokens (salud: grises/rojos/negros/blancos) ---------- */
:root {
  --c-bg:        #f6f7f8;   /* fondo general gris muy claro */
  --c-surface:   #ffffff;   /* tarjetas/superficies */
  --c-text:      #111111;   /* texto principal (negro) */
  --c-muted:     #6b7280;   /* texto secundario (gris) */
  --c-border:    #e5e7eb;   /* líneas divisorias */
  --c-primary:   #ef4444;   /* rojo principal (acciones) */
  --c-primary-6: #dc2626;   /* hover */
  --c-primary-7: #b91c1c;   /* active */
  --c-accent:    #0a0a0a;   /* negro profundo para headers/botones oscuros */

  /* tamaños ajustables sin tocar el HTML */
  --radius-lg:   14px;
  --radius-xl:   18px;
  --gap:         14px;

  /* tamaño máximo del SVG (puedes subirlo/bajarlo) */
  --svg-max-h:   520px;
}

/* ---------- Layout base ---------- */
.min-h-screen {
  background: var(--c-bg);
  color: var(--c-text);
}

/* ---------- Header sticky ---------- */
header.sticky {
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--c-border);
}

/* Botón hamburguesa: foco accesible y área táctil cómoda */
header .p-2 {
  outline: none;
}
header .p-2:focus-visible {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, .35); /* focus rojo accesible */
  border-radius: 12px;
}

/* Botón primario “Guardar/Acción” coherente con la paleta */
.btn-primary,
button.bg-gray-900 {
  background: var(--c-accent) !important;
  color: #fff !important;
  transition: background .2s ease, transform .05s ease;
}
.btn-primary:hover,
button.bg-gray-900:hover {
  background: #000 !important;
}
.btn-primary:active,
button.bg-gray-900:active {
  transform: translateY(0.5px);
}

/* Botón de peligro secundario con rojo */
.btn-danger {
  background: var(--c-primary);
  color: #fff;
}
.btn-danger:hover { background: var(--c-primary-6); }
.btn-danger:active { background: var(--c-primary-7); }

/* ---------- Cajitas / tarjetas (para separar visualmente) ---------- */
.card,
.bg-white.border {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-xl);
  box-shadow:
    0 1px 1px rgba(0,0,0,.03),
    0 4px 12px rgba(17,24,39,.04);
}

/* Títulos de sección discretos */
.section-title {
  font-weight: 600;
  color: var(--c-accent);
}

/* Líneas divisorias más sutiles */
.divider,
.h-px.bg-gray-200 {
  background: var(--c-border) !important;
  height: 1px;
  opacity: .9;
}

/* ---------- Menú lateral (drawer) ---------- */
/* Accesible con animación suave, usa tus clases Tailwind + estos ajustes */
aside[aria-label="Menú lateral"] {
  background: var(--c-surface);
  border-right: 1px solid var(--c-border);
}

/* Items del menú: estados coherentes y tacto cómodo */
aside[aria-label="Menú lateral"] nav button {
  border-radius: 12px;
  line-height: 1.25;
}
aside[aria-label="Menú lateral"] nav button:hover {
  background: #f3f4f6; /* gris claro */
}
aside[aria-label="Menú lateral"] nav button[aria-current="page"],
aside[aria-label="Menú lateral"] nav .bg-gray-100 {
  background: #f3f4f6 !important;
  font-weight: 600;
}

/* Backdrop para cuando el drawer está abierto en móvil (añade el div sugerido abajo) */
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(17, 24, 39, .35);
  backdrop-filter: blur(2px);
  z-index: 30; /* por debajo del aside z-40 */
  opacity: 0;
  pointer-events: none;
  transition: opacity .2s ease;
}
.drawer-backdrop.is-open {
  opacity: 1;
  pointer-events: auto;
}

/* ---------- Tablas / listas de detalle ---------- */
.table-like {
  border: 1px solid var(--c-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.table-like .row {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: var(--gap);
  padding: 12px 14px;
  align-items: start;
}
.table-like .row + .row {
  border-top: 1px solid var(--c-border);
}
.table-like .label {
  color: var(--c-muted);
  font-weight: 500;
}
.table-like .value {
  color: var(--c-text);
}

/* ---------- SVG redimensionable sin perder trazo ---------- */
/* Aplica la clase .svg-fluid al <svg> principal (ver micro-cambio abajo) */
.svg-fluid {
  display: block;
  width: 100%;
  height: auto;
  max-height: var(--svg-max-h);
}

/* Mantiene el grosor del trazo al escalar */
.svg-fluid [stroke] {
  vector-effect: non-scaling-stroke;
}

/* Hover útil en zonas clicables (si tu SVG usa clases tipo .tooth/.zone) */
.svg-fluid .tooth:hover,
.svg-fluid .zone:hover {
  fill: #fee2e2;           /* rojo muy claro al pasar el ratón */
  cursor: pointer;
  transition: fill .15s ease;
}

/* Estado “seleccionado” que puedes aplicar dinámicamente desde Vue */
.svg-selected {
  outline: 2px solid var(--c-primary);
  outline-offset: 2px;
  border-radius: 10px;
}

/* ---------- Utilidades suaves para separar contenido ---------- */
.stack-md > * + * { margin-top: 12px; }
.stack-lg > * + * { margin-top: 18px; }
.cluster { display: flex; gap: var(--gap); align-items: center; }
.grid-cards { display: grid; gap: var(--gap); grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }

/* ---------- Accesibilidad: foco y reducción de movimiento ---------- */
:focus-visible {
  outline: 2px solid rgba(239, 68, 68, .8);
  outline-offset: 2px;
  border-radius: 10px;
}
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
</style>
