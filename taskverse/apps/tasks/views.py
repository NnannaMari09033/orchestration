from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

# Exempt CSRF for development/local use; in production use a token-based auth
graphql_view = csrf_exempt(GraphQLView.as_view(graphiql=True))
