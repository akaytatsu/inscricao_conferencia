from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth import logout as logout_user
from django.views.generic import FormView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.data.forms import InscricaoForm, AtualizaInscricaoForm
from apps.data.models import Inscricao, Dependente, Conferencia
from apps.accounts.forms import LoginForm


class RedirectMixin(LoginRequiredMixin):

    def get_conferencia(self):
        slug = self.kwargs.get("conferencia")
        conferencia = Conferencia.objects.get(titulo_slug=slug)

        return conferencia

    def get_login_url(self, *args, **kwargs):
        conferencia = self.get_conferencia()

        return reverse_lazy('home', kwargs={"conferencia": conferencia.titulo_slug})


class StartView(TemplateView):
    template_name = 'pregacoes/home.html'

    # def get(self, request):
    #     conferencias = Conferencia.get_all_active()

    #     if len(conferencias) == 1:
    #         conf = conferencias[0]
    #         return redirect( reverse_lazy('home', kwargs={"conferencia": conf.titulo_slug}) )
    #     # elif len(conferencias) > 1:

    #     return super(StartView, self).get(request)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context


class HomeView(RedirectMixin, TemplateView):
    template_name = 'inscricao/dashboard.html'
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        conferencia = Conferencia.objects.get(titulo_slug=kwargs.get('conferencia'))
        inscricao = Inscricao.objects.get(conferencia=conferencia, usuario=self.request.user)
        dependentes = Dependente.objects.filter(inscricao=inscricao)

        inscricao.busca_valor_total()

        context['conferencia'] = conferencia
        context['inscricao'] = inscricao
        context['dependentes'] = dependentes
        context['menu'] = "dashboard"

        return context


class inscricaoView(RedirectMixin, UpdateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = Inscricao
    template_name = 'inscricao/inscricao.html'
    form_class = AtualizaInscricaoForm

    def post(self, request, *args, **kwargs):
        conferencia = self.get_conferencia()
        inscricao = self.get_object()

        context = {}
        context['conferencia'] = self.get_conferencia()
        context['inscricao'] = self.get_object()
        context['edicao'] = True
        context['menu'] = "inscricao"

        data_copy = request.POST.copy()
        data_copy['cpf'] = inscricao.cpf
        data_copy['email'] = inscricao.email
        data_copy['conferencia'] = conferencia.pk

        form = AtualizaInscricaoForm(conferencia, data=data_copy, instance=context['inscricao'])

        if form.is_valid():
            inscricao = form.save()
            inscricao.atualiza_valor_total()

        context['form'] = form
        return super().render_to_response(context)

    def get_form(self, form_class=None):
        conferencia = self.get_conferencia()
        return AtualizaInscricaoForm(conferencia.pk, **self.get_form_kwargs())

    def get_conferencia(self):
        slug = self.kwargs.get("conferencia")
        conferencia = Conferencia.objects.get(titulo_slug=slug)

        return conferencia

    def get_object(self):
        conferencia = self.get_conferencia()
        return Inscricao.objects.get(conferencia=conferencia, usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conferencia'] = self.get_conferencia()
        context['inscricao'] = self.get_object()
        context['edicao'] = True
        context['menu'] = "inscricao"

        return context


class DependentesView(RedirectMixin, TemplateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    template_name = 'inscricao/dependentes.html'

    def get_conferencia(self):
        slug = self.kwargs.get("conferencia")
        conferencia = Conferencia.objects.get(titulo_slug=slug)

        return conferencia

    def get_object(self):
        conferencia = self.get_conferencia()
        return Inscricao.objects.get(conferencia=conferencia, usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conferencia'] = self.get_conferencia()
        context['inscricao'] = self.get_object()
        context['edicao'] = True
        context['menu'] = "dependentes"

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
                inscricao = Inscricao.objects.get(cpf=cpf, data_nascimento=data_nascimento, conferencia=conferencia)
                user = inscricao.usuario
            except:
                context['not_found'] = True
                return super().render_to_response(context)

            login(request, user)

            return redirect(reverse_lazy('dashboard', kwargs={"conferencia": conferencia.titulo_slug}))

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

        data_copy['conferencia'] = conferencia.id

        form = InscricaoForm(conferencia, data=data_copy)

        if form.is_valid():

            inscricao = form.save(commit=False)
            inscricao.conferencia = self.get_conferencia()
            user = inscricao.create_account()
            inscricao.save()

            inscricao.atualiza_valor_total()

            login(request, user)

            return redirect(reverse_lazy('dependentes', kwargs={"conferencia": conferencia.titulo_slug}))

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


class PagarView(RedirectMixin, TemplateView):
    template_name = 'inscricao/pagar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        conferencia = Conferencia.objects.get(titulo_slug=kwargs.get('conferencia'))
        inscricao = Inscricao.objects.get(conferencia=conferencia, usuario=self.request.user)
        dependentes = Dependente.objects.filter(inscricao=inscricao)

        inscricao.busca_valor_total()

        context['conferencia'] = conferencia
        context['inscricao'] = inscricao
        context['dependentes'] = dependentes
        context['menu'] = "pagar"

        return context

    def get_conferencia(self):
        slug = self.kwargs.get("conferencia")
        conferencia = Conferencia.objects.get(titulo_slug=slug)

        return conferencia


class ContatoView(RedirectMixin, TemplateView):
    template_name = 'inscricao/contato.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        conferencia = Conferencia.objects.get(titulo_slug=kwargs.get('conferencia'))
        inscricao = Inscricao.objects.get(conferencia=conferencia, usuario=self.request.user,)

        context['conferencia'] = conferencia
        context['inscricao'] = inscricao
        context['menu'] = "contato"

        return context

    def get_conferencia(self):
        slug = self.kwargs.get("conferencia")
        conferencia = Conferencia.objects.get(titulo_slug=slug)

        return conferencia


class LogoutView(TemplateView):
    template_name = 'inscricao/dashboard.html'

    def get(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        logout_user(request)

        conferencia = Conferencia.objects.get(titulo_slug=kwargs.get('conferencia'))

        return redirect(reverse_lazy('home', kwargs={"conferencia": conferencia.titulo_slug}))
