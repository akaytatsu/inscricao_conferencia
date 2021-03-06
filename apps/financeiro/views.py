from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.financeiro.models import Despesas, Comprovantes
from apps.financeiro.serializers import (
    DespesasSerializer, NovaDespesaSerializer, ComprovantesSerializer, DespesaImageSerializer
)


class ComprovantesViewSet(APIView):
    parser_classes = (MultiPartParser, FormParser)
    queryset = Comprovantes.objects.all()
    serializer_class = ComprovantesSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):

        despesa_id = request.GET.get('id', None)

        if despesa_id is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        data = Comprovantes.objects.filter(despesa_id=despesa_id)

        serializer = ComprovantesSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        file_serializer = DespesaImageSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response({}, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):

        try:
            qs = Comprovantes.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_200_OK)

        qs.delete()

        return Response(status=status.HTTP_200_OK)


class FinanceiroViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def solicitacao(self, request):
        solicitacao = Despesas.objects.get(pk=request.GET.get("id"))

        serializer = DespesasSerializer(solicitacao)

        return Response(serializer.data, status=200)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def solicitacoes(self, request):

        solicitacoes = Despesas.objects

        if request.user.can_aprove is True:
            solicitacoes = solicitacoes

        elif request.user.can_pay is True:
            solicitacoes = solicitacoes.filter(status__gte=2).exclude(status=8)

        else:
            solicitacoes = solicitacoes.filter(usuario_solicitacao=request.user)

        solicitacoes = solicitacoes.order_by('status')

        serializer = DespesasSerializer(solicitacoes, many=True)

        return Response(serializer.data, status=200)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def nova_solicitacao(self, request):

        serializer = NovaDespesaSerializer(data=request.data)

        if serializer.is_valid():
            obj = serializer.save(usuario_solicitacao=request.user, status=1,
                                  usuario_aprovacao=None, usuario_comprovacao=None)
            obj.notifica_nova_despesa()

            return Response(DespesasSerializer(obj).data, status=200)

        return Response(serializer.errors, status=400)

    @action(methods=['put'], detail=False, permission_classes=[IsAuthenticated])
    def aprova_solicitacao(self, request):

        pk = request.data.get("pk", None)

        if pk is None:
            return Response({"error": "Pk não informada"}, status=400)

        try:
            despesa = Despesas.objects.get(pk=pk)
        except Despesas.DoesNotExist:
            return Response({"error": "Registro não encontrado"}, status=400)

        if despesa.status != 1:
            return Response({"error": "Status atual não permite aprovação"}, status=400)

        despesa.status = 2
        despesa.aprovado = True
        despesa.save()
        despesa.notifica_aprovacao()

        return Response(DespesasSerializer(despesa).data, status=200)

    @action(methods=['put'], detail=False, permission_classes=[IsAuthenticated])
    def reprova_solicitacao(self, request):

        pk = request.data.get("pk", None)
        justificativa = request.data.get("justificativa", None)

        if pk is None:
            return Response({"error": "Pk não informada"}, status=400)

        try:
            despesa = Despesas.objects.get(pk=pk)
        except Despesas.DoesNotExist:
            return Response({"error": "Registro não encontrado"}, status=400)

        if despesa.status != 1:
            return Response({"error": "Status atual não permite aprovação"}, status=400)

        despesa.status = 8
        despesa.reprovado = True
        despesa.justificativa_reprovacao = justificativa
        despesa.save()
        despesa.notifica_reprovacao()

        return Response(DespesasSerializer(despesa).data, status=200)

    @action(methods=['put'], detail=False, permission_classes=[IsAuthenticated])
    def confirma_repasse_solicitacao(self, request):

        pk = request.data.get("pk", None)

        if pk is None:
            return Response({"error": "Pk não informada"}, status=400)

        try:
            despesa = Despesas.objects.get(pk=pk)
        except Despesas.DoesNotExist:
            return Response({"error": "Registro não encontrado"}, status=400)

        if despesa.status != 2:
            return Response({"error": "Status atual não permite aprovação"}, status=400)

        despesa.status = 4
        despesa.save()
        despesa.notifica_repasse_recurso()

        return Response(DespesasSerializer(despesa).data, status=200)

    @action(methods=['put'], detail=False, permission_classes=[IsAuthenticated])
    def confirma_aprovacao_solicitacao(self, request):

        pk = request.data.get("pk", None)

        if pk is None:
            return Response({"error": "Pk não informada"}, status=400)

        try:
            despesa = Despesas.objects.get(pk=pk)
        except Despesas.DoesNotExist:
            return Response({"error": "Registro não encontrado"}, status=400)

        if despesa.status != 5:
            return Response({"error": "Status atual não permite aprovação"}, status=400)

        despesa.status = 6
        despesa.comprovado = True
        despesa.save()
        despesa.notifica_aprovacao_comprovacao()

        return Response(DespesasSerializer(despesa).data, status=200)

    @action(methods=['put'], detail=False, permission_classes=[IsAuthenticated])
    def reprova_aprovacao_solicitacao(self, request):

        pk = request.data.get("pk", None)

        if pk is None:
            return Response({"error": "Pk não informada"}, status=400)

        try:
            despesa = Despesas.objects.get(pk=pk)
        except Despesas.DoesNotExist:
            return Response({"error": "Registro não encontrado"}, status=400)

        if despesa.status != 5:
            return Response({"error": "Status atual não permite aprovação"}, status=400)

        despesa.status = 4
        despesa.save()
        despesa.notifica_reprovacao_comprovacao()

        return Response(DespesasSerializer(despesa).data, status=200)

    @action(methods=['put'], detail=False, permission_classes=[IsAuthenticated])
    def enviar_comprovante(self, request):
        despesa = Despesas.objects.get(pk=request.data.get("id"))

        if Comprovantes.objects.filter(despesa=despesa).count() < 1:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        despesa.status = 5
        despesa.save()
        despesa.notifica_envio_comprovacao()

        return Response({}, status=200)
