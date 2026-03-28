import tempfile
from pathlib import Path

from pyshex import ShExEvaluator
from rdflib import Graph, Namespace, RDF, URIRef

from repositories.user_repo import UserRepo
from rdf_store import get_allergy_graph, get_patient_graph, get_procedure_graph, get_store, get_user_graph
from rdf_util import copy_subgraph, extraer_valores

FHIR = Namespace("http://hl7.org/fhir/")
EX = Namespace("http://example.org/fhir/custom#")


class ImportService:
    def import_ttl_with_shex(self, user_uri: str, rdf_bytes: bytes, shex_bytes: bytes) -> dict:
        """Replica el flujo de /upload/ pero fuera del router."""
        with tempfile.NamedTemporaryFile(suffix=".ttl", delete=False) as rdf_temp, tempfile.NamedTemporaryFile(suffix=".shex", delete=False) as shex_temp:
            rdf_temp.write(rdf_bytes)
            shex_temp.write(shex_bytes)
            rdf_path = Path(rdf_temp.name)
            shex_path = Path(shex_temp.name)

        g_temp = Graph()
        g_temp.parse(rdf_path, format="ttl")

        schema_str = shex_path.read_text(encoding="utf-8")
        evaluator = ShExEvaluator(rdf=g_temp, schema=schema_str)

        errores = []
        for pac in g_temp.subjects(RDF.type, FHIR.Patient):
            for result in evaluator.evaluate(start="PatientShape", focus=str(pac)):
                if not result.result:
                    errores.append({"focus": str(result.focus), "shape": result.start, "reason": result.reason})

        for proc in g_temp.subjects(RDF.type, FHIR.Procedure):
            for result in evaluator.evaluate(start="ProcedureShape", focus=str(proc)):
                if not result.result:
                    errores.append({"focus": str(result.focus), "shape": result.start, "reason": result.reason})

        for allergy in g_temp.subjects(RDF.type, FHIR.AllergyIntolerance):
            for result in evaluator.evaluate(start="AllergyIntoleranceShape", focus=str(allergy)):
                if not result.result:
                    errores.append({"focus": str(result.focus), "shape": result.start, "reason": result.reason})

        if errores:
            return {"ok": False, "errors": errores}

        store = get_store()
        g_user = get_user_graph()
        g_patient = get_patient_graph()
        g_proc = get_procedure_graph()
        g_allergy = get_allergy_graph()

        for subj in g_temp.subjects(RDF.type, FHIR.Patient):
            if (subj, RDF.type, FHIR.Patient) not in g_patient:
                copy_subgraph(subj, g_temp, g_patient)

        for subj in g_temp.subjects(RDF.type, FHIR.Procedure):
            if (subj, RDF.type, FHIR.Procedure) not in g_proc:
                copy_subgraph(subj, g_temp, g_proc)

        for subj in g_temp.subjects(RDF.type, FHIR.AllergyIntolerance):
            if (subj, RDF.type, FHIR.AllergyIntolerance) not in g_allergy:
                copy_subgraph(subj, g_temp, g_allergy)

        first_patient = next(g_temp.subjects(RDF.type, FHIR.Patient), None)
        if first_patient:
            g_user.add((URIRef(user_uri), EX.tienePaciente, first_patient))

        g_user.commit()
        g_patient.commit()
        g_proc.commit()
        g_allergy.commit()
        store.commit()

        return {
            "ok": True,
            "pacientes_triples": sum(1 for _ in store.triples((None, None, None), context=g_patient.identifier)),
            "procedimientos_triples": sum(1 for _ in store.triples((None, None, None), context=g_proc.identifier)),
        }

    def preview_files(self, files: list[tuple[str, bytes]]) -> list[dict]:
        data: list[dict] = []
        for _, content in files:
            g_temp = Graph()
            g_temp.parse(data=content, format="ttl")
            for subj in g_temp.subjects(RDF.type, FHIR.Patient):
                data.append({"tipo": "paciente", "datos": extraer_valores(g_temp, subj)})
            for subj in g_temp.subjects(RDF.type, FHIR.Procedure):
                data.append({"tipo": "procedimiento", "datos": extraer_valores(g_temp, subj)})
            for subj in g_temp.subjects(RDF.type, FHIR.AllergyIntolerance):
                data.append({"tipo": "alergia", "datos": extraer_valores(g_temp, subj)})
        return data

    def confirm_files(self, user_uri: str, files: list[tuple[str, bytes]], set_as_favorite: bool = False) -> dict:
        g_user = get_user_graph()
        g_patient = get_patient_graph()
        g_proc = get_procedure_graph()
        g_allergy = get_allergy_graph()

        imported_patient_ids: list[str] = []
        for _, content in files:
            g_temp = Graph()
            g_temp.parse(data=content, format="ttl")

            for subj in g_temp.subjects(RDF.type, FHIR.Patient):
                copy_subgraph(subj, g_temp, g_patient)
                imported_patient_ids.append(str(subj).split("/")[-1])

            for subj in g_temp.subjects(RDF.type, FHIR.Procedure):
                copy_subgraph(subj, g_temp, g_proc)

            for subj in g_temp.subjects(RDF.type, FHIR.AllergyIntolerance):
                copy_subgraph(subj, g_temp, g_allergy)

        g_patient.commit()
        g_proc.commit()
        g_allergy.commit()

        for patient_id in imported_patient_ids:
            patient_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
            g_user.add((URIRef(user_uri), EX.tienePaciente, patient_uri))
        g_user.commit()

        if set_as_favorite and imported_patient_ids:
            favorite_patient_uri = f"http://hl7.org/fhir/Patient/{imported_patient_ids[0]}"
            UserRepo().set_favorite_patient(user_uri, favorite_patient_uri)

        if len(imported_patient_ids) == 1:
            return {"redirect": f"/paciente/{imported_patient_ids[0]}"}
        return {"redirect": "/profile"}
