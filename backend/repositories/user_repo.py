from rdflib import URIRef

from rdf_store import get_patient_graph, get_user_graph
from sparql import queries


class UserRepo:
    def exists_by_email(self, email: str) -> bool:
        g_user = get_user_graph()
        return g_user.query(queries.ASK_USER_EXISTS.format(email=email)).askAnswer

    def create_user(self, usuario_uri: str, nombre: str, email: str, hashed: str) -> None:
        g_user = get_user_graph()
        g_user.update(
            queries.INSERT_USER.format(
                usuario_uri=usuario_uri,
                nombre=nombre,
                email=email,
                hashed=hashed,
            )
        )
        g_user.commit()

    def get_by_email(self, email: str) -> tuple[str, str] | None:
        g_user = get_user_graph()
        rows = list(g_user.query(queries.GET_USER_BY_EMAIL.format(email=email)))
        if not rows:
            return None
        user_uri, hashed = rows[0]
        return str(user_uri), str(hashed)

    def get_profile(self, user_uri: str) -> dict | None:
        g_user = get_user_graph()
        rows = list(g_user.query(queries.GET_USER_PROFILE.format(user_uri=user_uri)))
        if not rows:
            return None
        row = rows[0]
        return {"usuario_uri": user_uri, "nombre": str(row.nombre), "email": str(row.email)}

    def list_my_patients(self, user_uri: str) -> list[dict]:
        g_user = get_user_graph()
        g_patient = get_patient_graph()
        rows = g_user.query(queries.GET_USER_PATIENTS.format(user_uri=user_uri))
        output: list[dict] = []
        for row in rows:
            patient_uri = str(row.patient)
            name_rows = list(g_patient.query(queries.GET_NAME_SURNAME.format(patient_uri=patient_uri)))
            item = {"id": patient_uri.split("/")[-1], "uri": patient_uri}
            if name_rows:
                first = name_rows[0]
                if getattr(first, "given", None):
                    item["nombre"] = str(first.given)
                if getattr(first, "family", None):
                    item["apellido"] = str(first.family)
            output.append(item)
        return output

    def link_patient(self, user_uri: str, patient_uri: str) -> None:
        g_user = get_user_graph()
        g_user.update(queries.LINK_USER_PATIENT.format(user_uri=user_uri, patient_uri=patient_uri))
        g_user.commit()

    def has_patient_access(self, user_uri: str, patient_uri: str | URIRef) -> bool:
        g_user = get_user_graph()
        return g_user.query(
            queries.ASK_USER_HAS_PATIENT.format(user_uri=user_uri, patient_uri=str(patient_uri))
        ).askAnswer