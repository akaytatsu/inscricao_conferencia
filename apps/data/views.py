from pagseguro import PagSeguro
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from apps.data.models import Inscricao, Dependente, Conferencia

from .serializers import (
    ContatoSerializer, InscricaoSerializer, ConferenciaSerializer, DependentesSerializer,
    InscricaoPagSeguroTransactionSerializer
)


class DependentesApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        queryset = Dependente.objects.filter(inscricao_id=request.GET.get("inscricao_id"))
        queryset = queryset.order_by('-idade')
        serializer = DependentesSerializer(queryset, many=True)

        return Response(serializer.data)


class DependenteApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        queryset = Dependente.objects.get(id=request.GET.get("id"), inscricao_id=request.GET.get("inscricao_id"))
        serializer = DependentesSerializer(queryset)

        return Response(serializer.data)

    def post(self, request, format=None):

        if request.data.get("id") is None or request.data.get("id") == "":
            serializer = DependentesSerializer(data=request.data)
        else:
            queryset = Dependente.objects.get(id=request.data.get("id"))
            serializer = DependentesSerializer(queryset, data=request.data)

        if serializer.is_valid():
            dependente = serializer.save()
            inscricao = dependente.inscricao
            inscricao.atualiza_valor_total()

            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)

    def delete(self, request, format=None):

        try:
            dependente = Dependente.objects.get(id=request.GET.get("id"), inscricao_id=request.GET.get("inscricao"))
        except Dependente.DoesNotExist:
            return Response({}, status=400)

        inscricao = dependente.inscricao
        inscricao.atualiza_valor_total()
        dependente.delete()

        return Response({}, status=200)


class ConferenciaApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        queryset = Conferencia.objects.all()
        serializer = ConferenciaSerializer(queryset, many=True)

        return Response(serializer.data)


class InscricaoApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        queryset = Inscricao.objects.get(id=request.GET.get("inscricao_id"), usuario=self.request.user)

        serializer = InscricaoSerializer(queryset)

        return Response(serializer.data)


class ContatoApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        data = request.data.copy()
        data['inscricao'] = Inscricao.objects.get(pk=data['inscricao']).pk
        data['conferencia'] = Conferencia.objects.get(pk=data['conferencia']).pk

        serializer = ContatoSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({}, status=200)

        return Response(serializer.errors, status=400)


class InscricaoStatusPagSeguroApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        data = request.data.copy()

        inscricao = Inscricao.objects.get(pk=data['inscricao'])
        conferencia = Conferencia.objects.get(pk=data['conferencia'])

        data['inscricao'] = inscricao.pk
        data['conferencia'] = conferencia.pk

        serializer = InscricaoPagSeguroTransactionSerializer(inscricao, data=data)

        if inscricao.status != 1:
            return Response({}, status=200)

        if serializer.is_valid():
            serializer.save()
            return Response({}, status=200)

        return Response(serializer.errors, status=400)


class PagamentoApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        conferencia_pk = request.data.get("conferencia")
        inscricao_pk = request.data.get("inscricao")

        inscricao = Inscricao.objects.get(pk=inscricao_pk, conferencia_id=conferencia_pk)
        conferencia = inscricao.conferencia

        pg = PagSeguro(email=settings.PAGSEGURO_EMAIL, token=settings.PAGSEGURO_TOKEN,)

        pg.sender = {
            "name": inscricao.nome,
            "area_code": inscricao.ddd,
            "phone": inscricao.cleanned_telefone(),
            "email": inscricao.email,
        }

        pg.shipping = {
            "type": pg.NONE,
            "street": inscricao.endereco,
            "number": inscricao.numero,
            "complement": inscricao.complemento,
            "district": inscricao.bairro,
            "postal_code": inscricao.cep,
            "city": inscricao.cidade,
            "state": inscricao.uf,
            "country": "BRA"
        }

        pg.reference_prefix = "REFID_"
        pg.reference = inscricao.pk

        pg.items = [
            {
                "id": "0001",
                "description": conferencia.titulo,
                "amount": inscricao.valor_total,
                "quantity": 1,
            },
        ]

        url_base = reverse_lazy('home', kwargs={"conferencia": conferencia.titulo_slug})

        redirect_url = "{}{}".format(settings.BASE_URL, url_base)

        pg.redirect_url = redirect_url
        pg.notification_url = settings.NOTIFICATION_URL

        response = pg.checkout()

        inscricao.payment_reference = pg.reference
        inscricao.status = 1
        inscricao.save()

        return Response({
            "code": response.code,
            "transaction": response.transaction,
            "date": response.date,
            "payment_url": response.payment_url,
            "payment_link": response.payment_link,
            "errors": response.errors,
            "pre_ref": pg.reference_prefix,
            "reference": pg.reference,
        })


@csrf_exempt
def notification_view(request):
    notification_code = request.POST.get('notificationCode')

    pg = PagSeguro(email=settings.PAGSEGURO_EMAIL, token=settings.PAGSEGURO_TOKEN,)
    notification_data = pg.check_notification(notification_code)

    inscricao = Inscricao.objects.get(payment_reference=notification_data.reference)

    inscricao.sit_pagseguro = notification_data.status

    if notification_data.status == 3 or notification_data.status == "3":
        inscricao.status = 2

    inscricao.save()

    return HttpResponse("")


################
# RELATORIOS
################

def sortByQuantity(e):
    return e['inscricao__count'] + e['dependentes__count']


def sortByCidade(e):
    return e['cidade'] + e['cidade']


class RelatorioCidadesApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        response = {}

        for inscricao in Inscricao.objects.all():

            if response.get(inscricao.cidade, None):
                response[inscricao.cidade]['total'] = response[inscricao.cidade]['total'] + 1
                response[inscricao.cidade]['pessoas'].append({
                    'nome': inscricao.nome,
                    'cidade': inscricao.cidade,
                    'uf': inscricao.uf,
                    'dependente': False,
                    'idade': inscricao.idade,
                })
            else:
                response[inscricao.cidade] = {
                    'cidade': inscricao.cidade,
                    'total': 1,
                    'pessoas': [
                        {
                            'nome': inscricao.nome,
                            'cidade': inscricao.cidade,
                            'uf': inscricao.uf,
                            'dependente': False,
                            'idade': inscricao.idade
                        }
                    ]
                }

            for dependente in Dependente.objects.select_related('inscricao').filter(inscricao=inscricao):

                if response.get(dependente.inscricao.cidade, None):
                    response[dependente.inscricao.cidade]['total'] = response[dependente.inscricao.cidade]['total'] + 1
                    response[dependente.inscricao.cidade]['pessoas'].append({
                        'nome': dependente.nome,
                        'cidade': dependente.inscricao.cidade,
                        'uf': dependente.inscricao.uf,
                        'dependente': True,
                        'responsavel': dependente.inscricao.nome,
                        'idade': dependente.idade,
                    })
                else:
                    response[dependente.inscricao.cidade] = {
                        'cidade': dependente.inscricao.cidade,
                        'total': 1,
                        'pessoas': [
                            {
                                'nome': dependente.nome,
                                'cidade': dependente.inscricao.cidade,
                                'uf': dependente.inscricao.uf,
                                'dependente': True,
                                'responsavel': dependente.inscricao.nome,
                                'idade': dependente.idade,
                            }
                        ]
                    }

        response_sorted = {}
        for i in sorted(response.keys()):
            response_sorted[i] = response[i]

        response_arr = []
        for reg in response_sorted.items():
            response_arr.append(
                reg[1]
            )

        return Response(response_arr)


class RelatorioIdadesApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        response = {}

        for inscricao in Inscricao.objects.all():

            if response.get(inscricao.idade, None):
                response[inscricao.idade]['total'] = response[inscricao.idade]['total'] + 1
                response[inscricao.idade]['pessoas'].append({
                    'nome': inscricao.nome,
                    'cidade': inscricao.cidade,
                    'uf': inscricao.uf,
                    'dependente': False,
                })
            else:
                response[inscricao.idade] = {
                    'idade': inscricao.idade,
                    'total': 1,
                    'pessoas': [
                        {
                            'nome': inscricao.nome,
                            'cidade': inscricao.cidade,
                            'uf': inscricao.uf,
                            'dependente': False,
                        }
                    ]
                }

            for dependente in Dependente.objects.select_related('inscricao').filter(inscricao=inscricao):

                if response.get(dependente.idade, None):
                    response[dependente.idade]['total'] = response[dependente.idade]['total'] + 1
                    response[dependente.idade]['pessoas'].append({
                        'nome': dependente.nome,
                        'cidade': dependente.inscricao.cidade,
                        'uf': dependente.inscricao.uf,
                        'dependente': True,
                        'responsavel': dependente.inscricao.nome
                    })
                else:
                    response[dependente.idade] = {
                        'idade': dependente.idade,
                        'total': 1,
                        'pessoas': [
                            {
                                'nome': dependente.nome,
                                'cidade': dependente.inscricao.cidade,
                                'uf': dependente.inscricao.uf,
                                'dependente': True,
                                'responsavel': dependente.inscricao.nome
                            }
                        ]
                    }

        response_sorted = {}
        for i in sorted(response.keys()):
            response_sorted[i] = response[i]

        response_arr = []
        for reg in response_sorted.items():
            response_arr.append(
                reg[1]
            )

        return Response(response_arr)


class RelatorioStatusPagamentoApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        response = []

        pendente = Inscricao.objects.filter(status=1).count()
        pago = Inscricao.objects.filter(status=2).count()
        cancelado = Inscricao.objects.filter(status=3).count()
        aguardando = Inscricao.objects.filter(status=4).count()

        valor_pendente = Inscricao.objects.filter(status=1).aggregate(total=Sum('valor_total')).get("total", 0)
        valor_pago = Inscricao.objects.filter(status=2).aggregate(total=Sum('valor_total')).get("total", 0)
        valor_cancelado = Inscricao.objects.filter(status=3).aggregate(total=Sum('valor_total')).get("total", 0)
        valor_aguardando = Inscricao.objects.filter(status=4).aggregate(total=Sum('valor_total')).get("total", 0)

        response.append({'status_code': 1, 'status': 'Pendente', 'quantidade': pendente,
                         'valor': 0 if valor_pendente is None else valor_pendente})
        response.append({'status_code': 2, 'status': 'Pago', 'quantidade': pago,
                         'valor': 0 if valor_pago is None else valor_pago})
        response.append({'status_code': 3, 'status': 'Cancelado', 'quantidade': cancelado,
                         'valor': 0 if valor_cancelado is None else valor_cancelado})
        response.append({'status_code': 4, 'status': 'Aguardando Confirmação Pagamento',
                         'quantidade': aguardando, 'valor': 0 if valor_aguardando is None else valor_aguardando})

        return Response(response)


class RelatorioHospedagemApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        response = {}

        for inscricao in Inscricao.objects.all():

            hospedagem_nome = inscricao.hospedagem.nome

            if response.get(hospedagem_nome, None):
                response[hospedagem_nome]['total'] = response[hospedagem_nome]['total'] + 1
                response[hospedagem_nome]['pessoas'].append({
                    'nome': inscricao.nome,
                    'cidade': inscricao.cidade,
                    'uf': inscricao.uf,
                    'dependente': False,
                    'detalhe': inscricao.hospedagem_detalhe,
                    'idade': inscricao.idade,
                })
            else:
                response[hospedagem_nome] = {
                    'hospedagem': hospedagem_nome,
                    'total': 1,
                    'pessoas': [
                        {
                            'nome': inscricao.nome,
                            'cidade': inscricao.cidade,
                            'uf': inscricao.uf,
                            'dependente': False,
                            'detalhe': inscricao.hospedagem_detalhe,
                            'idade': inscricao.idade,
                        }
                    ]
                }

            for dependente in Dependente.objects.select_related('inscricao').filter(inscricao=inscricao):

                hospedagem_nome = dependente.hospedagem.nome

                if response.get(hospedagem_nome, None):
                    response[hospedagem_nome]['total'] = response[hospedagem_nome]['total'] + 1
                    response[hospedagem_nome]['pessoas'].append({
                        'nome': dependente.nome,
                        'cidade': dependente.inscricao.cidade,
                        'uf': dependente.inscricao.uf,
                        'dependente': True,
                        'responsavel': dependente.inscricao.nome,
                        'detalhe': dependente.hospedagem_detalhe,
                        'idade': dependente.idade,
                    })
                else:
                    response[hospedagem_nome] = {
                        'hospedagem': hospedagem_nome,
                        'total': 1,
                        'pessoas': [
                            {
                                'nome': dependente.nome,
                                'cidade': dependente.inscricao.cidade,
                                'uf': dependente.dependente.uf,
                                'dependente': True,
                                'responsavel': dependente.inscricao.nome,
                                'detalhe': dependente.hospedagem_detalhe,
                                'idade': dependente.idade,
                            }
                        ]
                    }

        response_arr = []
        for reg in response.items():
            response_arr.append(
                reg[1]
            )

        return Response(response_arr)
