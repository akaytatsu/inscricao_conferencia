from django.db import models

class RelatorioCidade(models.Model):
    class Meta:
        db_table = "relatorio_cidade"
        verbose_name = 'Relatório por Cidade'
        verbose_name_plural = 'Relatório por Cidades'

class RelatorioIdade(models.Model):
    class Meta:
        db_table = "relatorio_idade"
        verbose_name = 'Relatório por Idade'
        verbose_name_plural = 'Relatório por Idades'

class RelatorioStatusPagamento(models.Model):
    class Meta:
        db_table = "relatorio_status_pag"
        verbose_name = 'Relatório Status Pagamento'
        verbose_name_plural = 'Relatório Status Pagamento'

class RelatorioIdadeEspecifico(models.Model):
    class Meta:
        db_table = "relatorio_idade_especifico"
        verbose_name = 'Relatório por Idade Especifico'
        verbose_name_plural = 'Relatório por Idades Especificas'