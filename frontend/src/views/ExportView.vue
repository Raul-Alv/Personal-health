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
          Procedimientos
        </button>
        <button v-if="alergias.length" @click="setTipo('alergias')" 
                class="px-4 py-2 bg-red-500 text-white rounded">
          Alergias
        </button>
      </div>
    </div>

    <!-- Paso 3: Lista de selección -->
    <div v-if="tipoSeleccionado" class="mt-6">
      <h3 class="font-semibold capitalize">{{ tipoSeleccionado }}</h3>
      <div class="flex space-x-2 mb-2">
        <button @click="selectAll" class="px-3 py-1 bg-gray-300 rounded">Seleccionar todos</button>
        <button @click="deselectAll" class="px-3 py-1 bg-gray-300 rounded">Deseleccionar todos</button>
      </div>

      <ul>
        <li v-for="item in itemsMostrados" :key="item.id" class="flex items-center space-x-2">
          <input type="checkbox" v-model="seleccionados" :value="item.id" />
          <span>{{ item.text || item.display || item.code }}</span>
        </li>
      </ul>

      <button @click="exportarSeleccionados" class="mt-4 px-4 py-2 bg-green-500 text-white rounded">
        Exportar seleccionados
      </button>
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

const itemsMostrados = computed(() => {
  return tipoSeleccionado.value === "procedimientos" ? procedimientos.value : alergias.value;
});

onMounted(async () => {
  const res = await api.get("/mis_pacientes/menu");
  pacientes.value = res.data;
});

async function loadPatientData() {
  if (!selectedPatient.value) return;

  const token = localStorage.getItem("token");

  const resProc = await fetch(`/api/mis_pacientes/${selectedPatient.value}/get/procedimientos`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  procedimientos.value = await resProc.json();

  const resAlerg = await fetch(`/api/mis_pacientes/${selectedPatient.value}/get/alergias`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  alergias.value = await resAlerg.json();
}

function setTipo(tipo) {
  tipoSeleccionado.value = tipo;
  seleccionados.value = [];
}

function selectAll() {
  seleccionados.value = itemsMostrados.value.map(i => i.id || i.procedure_uri || i.alergia_uri);
}

function deselectAll() {
  seleccionados.value = [];
}

async function exportarSeleccionados() {
  if (!seleccionados.value.length) return alert("Debes seleccionar al menos un elemento.");

  const form = new FormData();
  form.append("patient_id", selectedPatient.value);
  form.append("tipo", tipoSeleccionado.value);
  form.append("ids", seleccionados.value.join(","));

  const res = await fetch("/api/export_seleccionados", {
    method: "POST",
    headers: { Authorization: "Bearer " + localStorage.getItem("token") },
    body: form
  });

  if (!res.ok) {
    alert("Error en la exportación");
    return;
  }

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `export_${tipoSeleccionado.value}_${selectedPatient.value}.ttl`;
  a.click();
  window.URL.revokeObjectURL(url);
}
</script>
