from django.contrib import admin
from django.urls import reverse
from django.utils.html import escape, mark_safe

from .models import Conferencia, Dependente, Hospedagem, Inscricao, Valores


@admin.register(Conferencia)
class ConferenciaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'max_inscr', 'data_abertura', 'data_encerramento', 'pagina_inicial')
    search_fields = ('titulo', )
    prepopulated_fields = {'titulo': ('titulo_slug',)}

    def pagina_inicial(self, obj):
        # link = reverse("admin:vtex_sku_changelist")
        return mark_safe('<a href="/{}/dashboard" target="_blank">{}</a>'.format(obj.titulo_slug, "Página Inicial"))

    pagina_inicial.allow_tags = True
    pagina_inicial.short_description = "Página Inicial"


@admin.register(Valores)
class ValoresAdmin(admin.ModelAdmin):
    list_display = ('conferencia', 'idade_inicial', 'idade_final', 'valor', )
    search_fields = ('conferencia', 'idade_inicial', )
    list_filter = ('conferencia', 'valor', )

@admin.register(Hospedagem)
class HospedagemAdmin(admin.ModelAdmin):
    list_display = ('conferencia', 'nome', 'limite', 'ativo', )
    search_fields = ('conferencia', 'nome', )
    list_filter = ('conferencia', 'limite', )

@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('conferencia', 'cpf', 'nome', 'nome_cracha', 'data_nascimento', 'email', 'idade', 'hospedagem', 'valor', 'valor_total', )
    search_fields = ('conferencia', 'cpf', 'nome', 'email')
    list_filter = ('conferencia', 'hospedagem', 'idade', )

@admin.register(Dependente)
class DependenteAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'nome', 'nome_cracha', 'data_nascimento', 'grau', 'valor', )
    search_fields = ('inscricao', 'nome', )
    list_filter = ('inscricao', 'grau', )
