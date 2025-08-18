import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

UserModel = get_user_model()


class UserType(DjangoObjectType):
  class Meta:
    model = UserModel
    fields = ("id", "email", "full_name", "is_active", "is_staff")


class Query(graphene.ObjectType):
  me = graphene.Field(UserType)

  def resolve_me(self, info):
    user = info.context.user
    if user and user.is_authenticated:
      return user
    return None


class Mutation(graphene.ObjectType):
  pass


schema = graphene.Schema(query=Query, mutation=Mutation)


