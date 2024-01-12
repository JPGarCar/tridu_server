from ninja import NinjaAPI

from tridu_server.api_security import GlobalJWTAuth

jwt_auth = GlobalJWTAuth()
api = NinjaAPI(
    auth=jwt_auth, title="Tridu API", version="0.1", description="API for Tridu Server"
)

api.add_router("/users/", "accounts.api.router")
api.add_router("/participants/", "participants.api.router")
