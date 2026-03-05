# app/notes.py
import logging
from typing import List
from urllib.parse import urlencode

from fastapi import APIRouter, BackgroundTasks, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from service.cache import delete_cached
from service.decorators import cached_route, log_route
from service.service import notes_storage
from service.config import MAX_NOTE_LENGTH, MAX_NOTES

logger = logging.getLogger(__name__)
router = APIRouter()


# @router.post("/notes/add", tags=["Notes"])
def add_note(
    request: Request, note: str = Form(...), background_tasks: BackgroundTasks = None
) -> RedirectResponse:
    notes: List[str] = notes_storage.get_all()

    error_msg = None
    if not note.strip():
        error_msg = "Заметка не может быть пустой"
    elif len(notes) >= MAX_NOTES:
        error_msg = "Превышено максимальное количество заметок"
    elif len(note) > MAX_NOTE_LENGTH:
        error_msg = "Заметка слишком длинная"

    if error_msg:
        # Если запрос ожидает HTML, делаем редирект с ошибкой
        if "text/html" in request.headers.get("accept", ""):
            return _error_redirect(error_msg)
        # Иначе — API-ошибка
        raise HTTPException(status_code=400, detail={f"error": error_msg})

    notes_storage.add(note)
    if background_tasks:
        background_tasks.add_task(delete_cached, "notes")
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


# @router.post("/notes/delete/{note_id}", tags=["Notes"])
def delete_note(
    note_id: int, background_tasks: BackgroundTasks = None
) -> RedirectResponse:
    notes = notes_storage.get_all()
    if note_id < 0 or note_id >= len(notes):
        raise HTTPException(status_code=404, detail={f"error": "Заметка не найдена"})
    notes_storage.delete(note_id)
    if background_tasks:
        background_tasks.add_task(delete_cached, "notes")
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/notes", tags=["Notes"])
@router.get("/notes?nocache=true", tags=["Service"])
@cached_route("notes")
@log_route("/notes")
async def get_notes(request: Request) -> dict:
    force = request.query_params.get("nocache") == "true"
    notes = notes_storage.get_all(force_refresh=force)
    return {"notes": notes}


def _error_redirect(message: str) -> RedirectResponse:
    params = urlencode({"error": message})
    return RedirectResponse(f"/?{params}", status_code=status.HTTP_303_SEE_OTHER)
