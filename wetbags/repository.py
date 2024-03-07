import os
from typing import Any, List

from firebase_admin import credentials, initialize_app, firestore
from google.api_core.exceptions import NotFound
from google.cloud.firestore_v1 import CollectionReference
from google.cloud.firestore_v1.types import WriteResult

from heats.models import Heat
from wetbags.models import Wetbag
from wetbags.creds import creds

cred = credentials.Certificate(creds)

app = initialize_app(cred)

db = firestore.client()

prefix: str = os.environ.get("FIREBASE_COLLECTION_PREFIX", "dev")


def get_wetbags_collection() -> CollectionReference:
    return db.collection("{}_wetbags".format(prefix))


def get_heats_collection() -> CollectionReference:
    return db.collection("{}_heats".format(prefix))


def get_wetbag(wetbag_id: str) -> Wetbag | None:
    wetbag_ref = get_wetbags_collection().document(wetbag_id)

    doc = wetbag_ref.get()

    if doc.exists:
        return Wetbag.from_dict(doc.to_dict())
    else:
        return None


def save_wetbag(wetbag: Wetbag) -> WriteResult:
    return get_wetbags_collection().document(wetbag.id).set(wetbag.to_dict())


def update_wetbag(wetbag_id: str, data: dict[str, Any]) -> WriteResult | None:
    try:
        return get_wetbags_collection().document(wetbag_id).update(data)
    except NotFound:
        return None


def save_heats(heats: List[Heat]) -> None:
    for heat in heats:
        get_heats_collection().document(str(heat.id)).set(heat.to_dict())
