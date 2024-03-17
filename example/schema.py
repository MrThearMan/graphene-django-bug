import graphene
from graphene_django.rest_framework.mutation import SerializerMutation

from rest_framework.serializers import ModelSerializer

from example.models import Example


class ExampleSerializer(ModelSerializer):
    class Meta:
        model = Example
        fields = [
            "id",
            "choice",
        ]


class ExampleMutation(SerializerMutation):
    class Meta:
        serializer_class = ExampleSerializer
        model_operations = ["create"]


class Query(graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    create_example = ExampleMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
