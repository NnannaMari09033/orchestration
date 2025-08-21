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


class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        full_name = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, email, full_name, password):
        user = UserModel(
            email=email,
            full_name=full_name,
            is_active=True
        )
        user.set_password(password)
        user.save()
        return CreateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
