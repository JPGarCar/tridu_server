from ninja import NinjaAPI

from tridu_server.api_security import GlobalJWTAuth

jwt_auth = GlobalJWTAuth()
api = NinjaAPI(auth=jwt_auth)

api.add_router("/users/", "accounts.api.router")
