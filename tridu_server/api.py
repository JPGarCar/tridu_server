from ninja import NinjaAPI

from tridu_server.api_security import GlobalJWTAuth

jwt_auth = GlobalJWTAuth()
api = NinjaAPI(
    auth=jwt_auth, title="Tridu API", version="1.0", description="API for Tridu Server"
)

api.add_router("/users/", "accounts.api.router")
api.add_router("/races/", "race.api.race_api.router")
api.add_router("/race_types/", "race.api.race_type_api.router")
api.add_router("/heats/", "heats.api.router")
api.add_router("/participants/", "participants.api.participant_api.router")
api.add_router("/relay_teams/", "participants.api.relay_team_api.router")
