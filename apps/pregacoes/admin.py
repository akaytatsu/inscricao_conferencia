from django.contrib import admin

from .models import Local, Pregacao, Preletor, ArquivoReferencia


class ArquivoReferenciaInline(admin.TabularInline):
    model = ArquivoReferencia
    extra = 1


@admin.register(Local)
class LocalPregacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco', )
    search_fields = ('nome', 'endereco',)


@admin.register(Preletor)
class PreletorAdmin(admin.ModelAdmin):
    list_display = ('nome', )
    search_fields = ('nome',)


@admin.register(Pregacao)
class PregacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'preletor', 'local', 'data_pregacao',)
    search_fields = ('titulo', )
    list_filter = ('preletor', 'local', )

    inlines = [
        ArquivoReferenciaInline,
    ]
