from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as logout_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView, UpdateView, FormView
from django.urls import reverse_lazy

from apps.data.models import Inscricao, Conferencia
from apps.data.forms import InscricaoForm
from apps.accounts.forms import LoginForm
from apps.accounts.models import Account

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'inscricao/dashboard.html'
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['conferencia'] = Conferencia.objects.get(titulo_slug=kwargs.get('conferencia'))
        
        return context

class inscricaoView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = Inscricao
    template_name = 'inscricao/inscricao.html'
    form_class = InscricaoForm

    def post(self, request, *args, **kwargs):
        conferencia = self.get_conferencia()
        context = {}
        context['conferencia'] = conferencia
        context['edicao'] = True

        data_copy = request.POST.copy()
        data_copy['cpf'] = request.user.cpf

        form = InscricaoForm(conferencia, data=data_copy, instance=self.get_object())

        if form.is_valid():
            form.save()

        context['form'] = form
        return super().render_to_response(context)

    def get_form(self, form_class=None):
        conferencia = self.get_conferencia()
        return InscricaoForm(conferencia.pk, **self.get_form_kwargs())

    def get_conferencia(self):
        slug = self.kwargs.get("conferencia")
        conferencia = Conferencia.objects.get(titulo_slug=slug)
        
        return conferencia

    def get_object(self):
        conferencia = self.get_conferencia()
        return Inscricao.objects.get(conferencia=conferencia, cpf=self.request.user.cpf)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conferencia'] = self.get_conferencia()
        context['edicao'] = True

        return context

class LoginView(TemplateView):
    template_name = 'inscricao/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['conferencia'] = Conferencia.objects.get(titulo_slug=kwargs.get('conferencia'))

        form = LoginForm(self.request.POST or None)  # instance= None
        context["form"] = form
        context["redirect_to"] = self.request.GET.get("redirect_to", "None")
        context["next"] = self.request.GET.get("next", "None")
        
        return context

    def get_conferencia(self):
        slug = self.kwargs.get("conferencia")
        conferencia = Conferencia.objects.get(titulo_slug=slug)
        
        return conferencia

    def post(self, request, *args, **kwargs):
        conferencia = self.get_conferencia()
        context = self.get_context_data(**kwargs)
        context['not_found'] = None

        form = LoginForm(request.POST)

        if form.is_valid():

            cpf = form.cleaned_data['cpf'].replace(".", "").replace("-", "")
            data_nascimento = form.cleaned_data['data_nascimento']

            try:
                user = Account.objects.get(cpf=cpf, data_nascimento=data_nascimento)
            except Account.DoesNotExist:
                context['not_found'] = True
                return super().render_to_response(context)

            login(request, user)

            return redirect( reverse_lazy('dashboard', kwargs={"conferencia": conferencia.titulo_slug}) )

        return super().render_to_response(context)

class NovaInscricaoView(FormView):
    redirect_field_name = 'redirect_to'
    template_name = 'inscricao/nova_inscricao.html'
    form_class = InscricaoForm

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['not_found'] = None

        data_copy = request.POST.copy()
        data_copy['cpf'] = data_copy['cpf'].replace(".", "").replace("-", "")
        data_copy['cep'] = data_copy['cep'].replace(".", "").replace("-", "")

        conferencia = self.get_conferencia()
        form = InscricaoForm(conferencia, data=data_copy)

        if form.is_valid():
            inscricao = form.save(commit=False)
            inscricao.conferencia = self.get_conferencia()
            inscricao.save()

            user = inscricao.create_account()

            rest = login(request, user)

            return redirect( reverse_lazy('dashboard', kwargs={"conferencia": conferencia.titulo_slug}) )

        context['form'] = form
        return super().render_to_response(context)

    def get_form(self, form_class=None):
        conferencia = self.get_conferencia()
        return InscricaoForm(conferencia.pk, **self.get_form_kwargs())

    def get_conferencia(self):
        slug = self.kwargs.get("conferencia")
        conferencia = Conferencia.objects.get(titulo_slug=slug)
        
        return conferencia

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)

        context['conferencia'] = self.get_conferencia()

        return context