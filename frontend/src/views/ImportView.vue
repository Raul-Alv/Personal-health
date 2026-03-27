<template>
  <div class="import-container">
    <h2>Importar datos RDF</h2>
    <input type="file" multiple @change="onFileChange" accept=".ttl,.rdf" />
    <button :disabled="!files.length" @click="previewFiles">Previsualizar</button>

    <div v-if="preview.length" class="preview-section">
      <h3>Previsualización de datos</h3>
      <div v-for="(item, idx) in preview" :key="idx" class="preview-item">
        <strong>{{ item.tipo.toUpperCase() }}</strong>
        <ul>
          <li v-for="campo in filtrarDatos(item.datos)" :key="campo.etiqueta">
            <span class="label">{{ campo.etiqueta }}: </span>
            <span>{{ campo.valor }}</span>
          </li>
        </ul>
      </div>
      <button @click="confirmImport">Confirmar importación</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "@/api/axios";
import { useRouter } from "vue-router";
import { computed } from "vue";

const files = ref([]);
const preview = ref([]);
const router = useRouter();

const prefixMap = {
  "http://hl7.org/fhir/": "fhir:",
  "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf:",
  "http://www.w3.org/2001/XMLSchema#": "xsd:",
  "http://example.org/fhir/custom#": "ex:"
};



function filtrarDatos(datos) {
  // Devuelve solo las entradas que tienen etiqueta
  return Object.entries(datos)
    .filter(([clave, valor]) => etiquetas[abreviarClave(clave)])
    .map(([clave, valor]) => ({
      etiqueta: etiquetas[abreviarClave(clave)],
      valor
    }));
}

function abreviarClave(clave) {
  if (!clave || typeof clave !== "string") return "";
  let abreviada = clave;
  for (const [url, prefijo] of Object.entries(prefixMap)) {
    abreviada = abreviada.replaceAll(url, prefijo);
  }
  return abreviada;
}

const etiquetas = {
  // --- Paciente ---
  "fhir:Patient.name__fhir:HumanName.given__fhir:value": "Nombre",
  "fhir:Patient.name__fhir:HumanName.family__fhir:value": "Apellidos",
  "fhir:Patient.birthDate__fhir:value": "Fecha de nacimiento",
  "fhir:Patient.gender__fhir:value": "Género",
  "fhir:Patient.identifier__fhir:Identifier.value__fhir:value": "Identificador",
  "fhir:Patient.address__fhir:Address.city__fhir:value": "Ciudad",
  "fhir:Patient.address__fhir:Address.line__fhir:value": "Dirección",
  "fhir:Patient.address__fhir:Address.postalCode__fhir:value": "Código postal",
  "fhir:Patient.telecom__fhir:ContactPoint.value__fhir:value": "Teléfono/Email",

  // --- Alergia ---
  //"fhir:AllergyIntolerance.clinicalStatus__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value": "Estado clínico",
  "fhir:AllergyIntolerance.code__fhir:CodeableConcept.coding__fhir:Coding.display__fhir:value": "Alergia",
  "fhir:AllergyIntolerance.code__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value": "Código",
  //"fhir:AllergyIntolerance.code__fhir:CodeableConcept.text__fhir:value": "Texto alergia",
  "fhir:AllergyIntolerance.onsetDateTime__fhir:value": "Fecha de inicio",
  "fhir:AllergyIntolerance.patient__fhir:Reference.reference__fhir:value": "Paciente",
  "fhir:AllergyIntolerance.actor__fhir:Reference.reference__fhir:value": "Profesional",
  "fhir:AllergyIntolerance.category__fhir:value": "Categoría",

  // --- Procedimiento ---
  "fhir:Procedure.code__fhir:CodeableConcept.coding__fhir:Coding.display__fhir:value": "Procedimiento",
  "fhir:Procedure.code__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value": "Código procedimiento",
  "fhir:Procedure.code__fhir:CodeableConcept.text__fhir:value": "Texto procedimiento",
  "fhir:Procedure.performedDateTime__fhir:value": "Fecha del procedimiento",
  "fhir:Procedure.subject__fhir:Reference.reference__fhir:value": "Paciente",
  "fhir:Procedure.performer__fhir:Procedure.performer.actor__fhir:Reference.reference__fhir:value": "Profesional",

  // --- Otros ejemplos útiles ---
  "fhir:AllergyIntolerance.verificationStatus__fhir:CodeableConcept.coding__fhir:Coding.code__fhir:value": "Estado de verificación",
  "fhir:AllergyIntolerance.criticality__fhir:value": "Criticidad",
  "fhir:AllergyIntolerance.note__fhir:Annotation.text__fhir:value": "Notas",
  "fhir:Procedure.status__fhir:value": "Estado del procedimiento"
};

function onFileChange(e) {
  files.value = Array.from(e.target.files);
  preview.value = [];
}

async function previewFiles() {
  const form = new FormData();
  files.value.forEach(f => form.append("files", f));
  const { data } = await api.post("/import/preview", form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  preview.value = data;
  // Imprime todos los datos en consola para depuración
  console.log("Preview completa:", data);

  preview.value.forEach(item => {
    Object.keys(item.datos).forEach(clave => {
      const abrev = abreviarClave(clave);
      console.log("Abreviada:", abrev, "| Original:", clave);
      console.log("Etiqueta:", etiquetas[abrev] || "No encontrada");
      console.log("Valor:", item.datos[clave] || "No encontrado");
      console.log("-----------------------------");
      
    });
    console.log("Item completo:", item.datos);
  });
}

async function confirmImport() {
  const form = new FormData();
  files.value.forEach(f => form.append("files", f));
  const { data } = await api.post("/import/confirm", form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  router.push(data.redirect);
}
</script>

<style scoped src="@/styles/views/ImportView.css"></style>
