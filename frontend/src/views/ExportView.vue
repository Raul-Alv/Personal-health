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
import { ref, onMounted, computed } from "vue";
import api from "@/api/axios";

const pacientes = ref([]);
const selectedPatient = ref("");
const procedimientos = ref([]);
const alergias = ref([]);
const tipoSeleccionado = ref("");
const seleccionados = ref([]);
const incluirPaciente = ref(true);

const itemsMostrados = computed(() => {
  return tipoSeleccionado.value === "procedimientos" ? procedimientos.value : alergias.value;
});

const getItemId = (item, index) => {
  if (item.procedure_uri) {
    return item.procedure_uri.split('/').pop();
  } else if (item.alergia_uri) {
    return item.alergia_uri.split('/').pop();
  } else if (item.id) {
    return item.id;
  } else {
    return `${tipoSeleccionado.value}-${index}`;
  }
};

onMounted(async () => {
  try {
    const res = await api.get("/mis_pacientes/menu");
    pacientes.value = res.data;
  } catch (error) {
    console.error("Error cargando pacientes:", error);
    alert("Error al cargar la lista de pacientes");
  }
});

async function loadPatientData() {
  if (!selectedPatient.value) return;

  try {
    const resProc = await api.get(`/mis_pacientes/${selectedPatient.value}/get/procedimientos`);
    procedimientos.value = resProc.data;

    const resAlerg = await api.get(`/mis_pacientes/${selectedPatient.value}/get/alergias`);
    alergias.value = resAlerg.data;
  } catch (error) {
    console.error("Error cargando datos del paciente:", error);
    alert("Error al cargar los datos del paciente");
  }
}

function setTipo(tipo) {
  tipoSeleccionado.value = tipo;
  seleccionados.value = [];
}

function selectAll() {
  seleccionados.value = itemsMostrados.value.map((item, index) => getItemId(item, index));
}

function deselectAll() {
  seleccionados.value = [];
}

async function exportarSeleccionados() {
  if (!seleccionados.value.length) {
    alert("Debes seleccionar al menos un elemento.");
    return;
  }

  try {
    const formData = new FormData();
    formData.append("patient_id", selectedPatient.value);
    formData.append("tipo", tipoSeleccionado.value);
    formData.append("ids", seleccionados.value.join(","));
    formData.append("incluir_paciente", incluirPaciente.value.toString());

    const response = await api.post("/export_seleccionados", formData, {
      responseType: 'blob',
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    const contentDisposition = response.headers['content-disposition'];
    let filename = `export_${tipoSeleccionado.value}_${selectedPatient.value}.ttl`;

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    const blob = new Blob([response.data], { type: 'text/turtle' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    seleccionados.value = [];
    alert(`Exportación completada: ${filename}`);
  } catch (error) {
    console.error("Error en la exportación:", error);

    if (error.response?.status === 404) {
      alert("No se encontraron los elementos seleccionados.");
    } else if (error.response?.status === 403) {
      alert("No tienes permisos para exportar datos de este paciente.");
    } else {
      alert("Error en la exportación: " + (error.response?.data?.detail || error.message));
    }
  }
}
</script>

<style scoped src="@/styles/views/ExportView.css"></style>
