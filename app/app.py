""" This file is the entrypoint of the application """

from fastapi import FastAPI, HTTPException

from .entities.session import NotMoreUsersAllowedException, UserNotFoundInSession, WatchableNotFound, Session
from .entities.user_payload import UserPayload
from .entities.vote import Vote
from .session_handler import SessionHandler
from .data.watchables_store.in_memory_watchables_store import InMemoryWatchablesStore
from .data.watchables_store.watchables_store import WatchablesStore
from .data.session_store.in_memory_session_store import InMemorySessionStore
from .data.session_store.session_store import SessionStore
from .session_handler import SessionNotFound

watchables_store: WatchablesStore = InMemoryWatchablesStore()

session_store: SessionStore = InMemorySessionStore()

session_handler = SessionHandler(watchables_store, session_store)

app = FastAPI()

@app.post("/session", status_code=201)
async def create_session():
    session_id = await session_handler.init_session()
    return {"session_id": session_id}


@app.post("/session/{session_id}/user",
          responses={404: {'description': 'Session not found'},
                     409: {'description': 'Session already has the maximum number of users'}},
          status_code=201, response_model=UserPayload)
async def user_joins_session(session_id: str):
    try:
        return await session_handler.join_user_to_session(session_id)
    except SessionNotFound:
        raise HTTPException(status_code=404,
                            detail=f'A session with id {session_id} could not be found')
    except NotMoreUsersAllowedException:
        raise HTTPException(
            status_code=409,
            detail=f'Session with id ${session_id} already has the maximum number of users')

@app.post('/session/{session_id}/user/{user_id}/vote',
          responses={404: {'description': 'Session or user could not be found'},
                     400: {'description': 'Watchable index is out of bounds'}},
          status_code=201)
async def emit_vote(session_id: str, user_id: str, vote: Vote):
    try:
        return await session_handler.emit_vote_to_session(session_id, user_id, vote.watchable_index, vote.content)
    except SessionNotFound:
        raise HTTPException(status_code=404,
                            detail=f'A session with id {session_id} could not be found')
    except UserNotFoundInSession:
        raise HTTPException(status_code=404,
                            detail=f'An user with id {user_id} could not be found in session {session_id}')
    except WatchableNotFound:
        raise HTTPException(status_code=400,
                            detail=f'The watchable index {vote.watchable_index} is out of bounds')


@app.get('/session/{session_id}/summary', responses={404: {'description': 'Session does not exist'}})
async def get_session_summary(session_id: str):
    try:
        return await session_handler.get_session_summary(session_id)
    except SessionNotFound:
        raise HTTPException(status_code=404,
                            detail=f'A session with id {session_id} could not be found')