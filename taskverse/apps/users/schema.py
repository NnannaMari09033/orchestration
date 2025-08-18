import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required
from django.contrib.auth import get_user_model
from graphene_django.types import DjangoObjectType

user = get_user_model()

class UserType(DjangoObjectType):
  class Meta:
    model = user
    fields = ('id, email, password')

class Query(graphene.ObjectType):
  me = graphene.Field(UserType)

  @login_required
  def Resolve_me(self, info):
    return info.context.user
  
class ObtainJsonWebToken(graphql_jwt.ObtainJSONWebToken):
  user = graphene.Field(UserType)

  @classmethod
  def resolve(cls, root, info, **kwargs):
    return cls(user=info.context.User)


class Mutation(graphene.ObjectType):
  Token_auth = ObtainJsonWebToken.Field()
  Verify_token = graphql_jwt.Verify.Field()
  Refresh_token = graphql_jwt.Refresh.Field()
  Revoke_auth = graphql_jwt.Revoke.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)


