<template>
  <div class="p-6">
    <h1 class="text-xl font-bold mb-4">Exportación de datos</h1>

    <!-- Paso 1: Seleccionar paciente -->
    <div>
      <label class="font-semibold">Selecciona un paciente:</label>
      <select v-model="selectedPatient" @change="loadPatientData" class="border p-2 rounded ml-2">
        <option disabled value="">-- Escoge un paciente --</option>
        <option v-for="p in pacientes" :key="p.id" :value="p.id">
          {{ p.nombre }} {{ p.apellido }}
        </option>
      </select>
    </div>

    <!-- Paso 2: Mostrar opciones de grupos -->
    <div v-if="selectedPatient" class="mt-4">
      <h2 class="font-semibold">Opciones de exportación</h2>
      <div class="space-x-4">
        <button v-if="procedimientos.length" @click="setTipo('procedimientos')" 
                class="px-4 py-2 bg-blue-500 text-white rounded">
          Procedimientos ({{ procedimientos.length }})
        </button>
        <button v-if="alergias.length" @click="setTipo('alergias')" 
                class="px-4 py-2 bg-red-500 text-white rounded">
          Alergias ({{ alergias.length }})
        </button>
      </div>
    </div>

    <!-- Paso 3: Lista de selección -->
    <div v-if="tipoSeleccionado" class="mt-6">
      <h3 class="font-semibold capitalize">{{ tipoSeleccionado }} ({{ itemsMostrados.length }})</h3>
      
      <!-- Toggle para incluir datos del paciente -->
      <div class="mb-4 p-3 bg-gray-100 rounded-lg border">
        <div class="flex items-center space-x-3">
          <input 
            type="checkbox" 
            id="incluir-paciente"
            v-model="incluirPaciente"
            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
          />
          <label for="incluir-paciente" class="font-medium text-gray-700 cursor-pointer">
            Incluir datos del paciente en la exportación
          </label>
        </div>
        <p class="text-sm text-gray-500 mt-1 ml-7">
          Si está activado, se incluirán los datos personales del paciente (nombre, fecha de nacimiento, etc.) junto con los {{ tipoSeleccionado }} seleccionados.
        </p>
      </div>

      <div class="flex space-x-2 mb-2">
        <button @click="selectAll" class="px-3 py-1 bg-gray-300 rounded">Seleccionar todos</button>
        <button @click="deselectAll" class="px-3 py-1 bg-gray-300 rounded">Deseleccionar todos</button>
      </div>

      <ul>
        <li v-for="(item, index) in itemsMostrados" :key="getItemId(item, index)" class="flex items-center space-x-2 mb-2">
          <input 
            type="checkbox" 
            v-model="seleccionados" 
            :value="getItemId(item, index)"
            :id="`item-${index}`"
          />
          <label :for="`item-${index}`" class="cursor-pointer">
            {{ item.text || item.display || item.code || `Item ${index + 1}` }}
          </label>
        </li>
      </ul>

      <div class="mt-4">
        <div class="mb-2">
          <p class="text-sm text-gray-600">Seleccionados: {{ seleccionados.length }} {{ tipoSeleccionado }}</p>
          <p class="text-sm text-gray-600">Datos del paciente: {{ incluirPaciente ? 'Incluidos' : 'No incluidos' }}</p>
        </div>
        <button 
          @click="exportarSeleccionados" 
          :disabled="seleccionados.length === 0"
          class="px-4 py-2 bg-green-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
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
const incluirPaciente = ref(true); // Por defecto incluir datos del paciente

const itemsMostrados = computed(() => {
  return tipoSeleccionado.value === "procedimientos" ? procedimientos.value : alergias.value;
});

// Función para obtener un ID único para cada item
const getItemId = (item, index) => {
  // Extraer el ID real de la URI
  if (item.procedure_uri) {
    // Extraer el ID de URIs como "http://hl7.org/fhir/Procedure/12345"
    return item.procedure_uri.split('/').pop();
  } else if (item.alergia_uri) {
    // Extraer el ID de URIs como "http://hl7.org/fhir/AllergyIntolerance/12345"  
    return item.alergia_uri.split('/').pop();
  } else if (item.id) {
    return item.id;
  } else {
    // Fallback con índice
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
    
    console.log("Procedimientos cargados:", procedimientos.value);
    console.log("Alergias cargadas:", alergias.value);
    
    // Debug: mostrar los IDs que se van a usar
    console.log("IDs de procedimientos:", procedimientos.value.map((item, index) => getItemId(item, index)));
    console.log("IDs de alergias:", alergias.value.map((item, index) => getItemId(item, index)));
    
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
    formData.append("incluir_paciente", incluirPaciente.value.toString()); // Añadir el toggle

    // Debug: mostrar qué se está enviando
    console.log("Datos a enviar:", {
      patient_id: selectedPatient.value,
      tipo: tipoSeleccionado.value,
      ids: seleccionados.value.join(","),
      ids_array: seleccionados.value,
      incluir_paciente: incluirPaciente.value
    });

    const response = await api.post("/export_seleccionados", formData, {
      responseType: 'blob',
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    // Crear enlace de descarga
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

    // Limpiar selección después de exportar
    seleccionados.value = [];
    alert(`Exportación completada: ${filename}`);
    
  } catch (error) {
    console.error("Error en la exportación:", error);
    
    if (error.response?.status === 404) {
      alert("No se encontraron los elementos seleccionados. Verifica los IDs en la consola.");
    } else if (error.response?.status === 403) {
      alert("No tienes permisos para exportar datos de este paciente.");
    } else {
      alert("Error en la exportación: " + (error.response?.data?.detail || error.message));
    }
  }
}
</script>
