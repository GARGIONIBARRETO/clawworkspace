#!/usr/bin/env python3
"""
Sistema de Relatórios Clínicos - Dr. Felipe
Gráficos e comparações automáticas
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from pacientes_manager import PacientesManager

class RelatoriosClinico:
    def __init__(self):
        self.manager = PacientesManager()
    
    def relatorio_bioimpedancia_evolucao(self, paciente_id: int, meses: int = 6):
        """Gera gráfico de evolução da bioimpedância"""
        
        # Busca dados
        bio_data = self.manager.buscar_bioimpedancia_paciente(paciente_id, limite=50)
        
        if not bio_data:
            print("❌ Nenhum dado de bioimpedância encontrado")
            return None
        
        # Converte para DataFrame
        df = pd.DataFrame(bio_data)
        df['data_medicao'] = pd.to_datetime(df['data_medicao'])
        df = df.sort_values('data_medicao')
        
        # Filtra últimos X meses
        data_limite = datetime.now() - timedelta(days=meses*30)
        df_filtrado = df[df['data_medicao'] >= data_limite]
        
        # Gera gráficos
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Evolução Bioimpedância - Últimos {meses} meses', fontsize=16)
        
        # Peso
        axes[0,0].plot(df_filtrado['data_medicao'], df_filtrado['peso'], 'b-o')
        axes[0,0].set_title('Peso (kg)')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # IMC
        axes[0,1].plot(df_filtrado['data_medicao'], df_filtrado['imc'], 'g-o')
        axes[0,1].set_title('IMC')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # Gordura Corporal
        axes[1,0].plot(df_filtrado['data_medicao'], df_filtrado['gordura_corporal'], 'r-o')
        axes[1,0].set_title('Gordura Corporal (%)')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Massa Muscular
        axes[1,1].plot(df_filtrado['data_medicao'], df_filtrado['massa_muscular'], 'purple', marker='o')
        axes[1,1].set_title('Massa Muscular (kg)')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Salva gráfico
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"/root/clawd/relatorios/bioimpedancia_evolucao_p{paciente_id}_{timestamp}.png"
        
        # Cria diretório se não existir
        import os
        os.makedirs("/root/clawd/relatorios", exist_ok=True)
        
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 Gráfico salvo em: {filename}")
        
        return filename
    
    def comparativo_exames_laboratoriais(self, paciente_id: int, tipo_exame: str):
        """Gera comparativo temporal de exames laboratoriais"""
        
        exames = self.manager.buscar_exames_paciente(paciente_id, tipo_exame)
        
        if len(exames) < 2:
            print("❌ Precisa de pelo menos 2 exames para comparação")
            return None
        
        # Organiza dados
        dados_comparacao = []
        for exame in exames:
            parametros = exame['parametros'] if isinstance(exame['parametros'], dict) else json.loads(exame['parametros'])
            for param, valor in parametros.items():
                dados_comparacao.append({
                    'data': exame['data_exame'],
                    'parametro': param,
                    'valor': float(valor) if isinstance(valor, (int, float)) else None
                })
        
        # DataFrame
        df = pd.DataFrame(dados_comparacao)
        df = df[df['valor'].notna()]  # Remove valores nulos
        df['data'] = pd.to_datetime(df['data'])
        
        # Gráfico
        parametros_unicos = df['parametro'].unique()
        num_parametros = len(parametros_unicos)
        
        if num_parametros == 0:
            print("❌ Nenhum parâmetro numérico encontrado")
            return None
        
        # Determina layout do subplot
        cols = 2
        rows = (num_parametros + 1) // 2
        
        fig, axes = plt.subplots(rows, cols, figsize=(12, 4*rows))
        if rows == 1 and cols == 1:
            axes = [axes]
        elif rows == 1:
            axes = axes
        else:
            axes = axes.flatten()
        
        fig.suptitle(f'Evolução {tipo_exame}', fontsize=16)
        
        for i, param in enumerate(parametros_unicos):
            data_param = df[df['parametro'] == param].sort_values('data')
            
            if i < len(axes):
                axes[i].plot(data_param['data'], data_param['valor'], 'o-')
                axes[i].set_title(param.replace('_', ' ').title())
                axes[i].tick_params(axis='x', rotation=45)
                axes[i].grid(True, alpha=0.3)
        
        # Esconde subplots vazios
        for i in range(num_parametros, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        
        # Salva
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"/root/clawd/relatorios/exames_{tipo_exame.replace(' ', '_')}_p{paciente_id}_{timestamp}.png"
        
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 Comparativo salvo em: {filename}")
        
        return filename
    
    def relatorio_completo_paciente(self, paciente_id: int):
        """Gera relatório completo do paciente"""
        
        relatorio = self.manager.gerar_relatorio_evolucao(paciente_id)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"/root/clawd/relatorios/relatorio_completo_p{paciente_id}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📋 Relatório completo salvo em: {filename}")
        
        # Gera também os gráficos
        self.relatorio_bioimpedancia_evolucao(paciente_id)
        
        return filename
    
    def dashboard_paciente(self, paciente_id: int):
        """Cria dashboard visual completo"""
        
        # Busca dados
        paciente_sql = "SELECT nome FROM pacientes WHERE id = %s;"
        self.manager.cursor.execute(paciente_sql, (paciente_id,))
        result = self.manager.cursor.fetchone()
        
        if not result:
            print("❌ Paciente não encontrado")
            return None
        
        paciente_nome = result[0]
        
        bio_data = self.manager.buscar_bioimpedancia_paciente(paciente_id, limite=10)
        exames_data = self.manager.buscar_exames_paciente(paciente_id)
        
        # HTML Dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard - {paciente_nome}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 10px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #e8f4f8; border-radius: 5px; text-align: center; }}
                .metric h3 {{ margin: 0; color: #333; }}
                .metric p {{ margin: 5px 0 0 0; font-size: 18px; font-weight: bold; color: #007acc; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
                th {{ background: #f5f5f5; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 Dashboard Clínico - {paciente_nome}</h1>
                <p>Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M")}</p>
            </div>
        """
        
        # Seção de Bioimpedância
        if bio_data:
            ultima_bio = bio_data[0]
            html_content += f"""
            <div class="section">
                <h2>📊 Última Bioimpedância ({ultima_bio['data_medicao']})</h2>
                <div class="metric">
                    <h3>Peso</h3>
                    <p>{ultima_bio['peso']} kg</p>
                </div>
                <div class="metric">
                    <h3>IMC</h3>
                    <p>{ultima_bio['imc']}</p>
                </div>
                <div class="metric">
                    <h3>Gordura Corporal</h3>
                    <p>{ultima_bio['gordura_corporal']}%</p>
                </div>
                <div class="metric">
                    <h3>Massa Muscular</h3>
                    <p>{ultima_bio['massa_muscular']} kg</p>
                </div>
            </div>
            """
        
        # Seção de Exames
        if exames_data:
            html_content += """
            <div class="section">
                <h2>🧪 Exames Recentes</h2>
                <table>
                    <tr>
                        <th>Data</th>
                        <th>Tipo</th>
                        <th>Laboratório</th>
                        <th>Observações</th>
                    </tr>
            """
            
            for exame in exames_data[:5]:
                html_content += f"""
                <tr>
                    <td>{exame['data_exame']}</td>
                    <td>{exame['tipo_exame']}</td>
                    <td>{exame['laboratorio']}</td>
                    <td>{exame['observacoes'] or '-'}</td>
                </tr>
                """
            
            html_content += "</table></div>"
        
        html_content += "</body></html>"
        
        # Salva HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        html_filename = f"/root/clawd/relatorios/dashboard_p{paciente_id}_{timestamp}.html"
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🌐 Dashboard HTML salvo em: {html_filename}")
        return html_filename

# Exemplo de uso
if __name__ == "__main__":
    relatorios = RelatoriosClinico()
    
    # Exemplo: relatório de bioimpedância para paciente ID 1
    # relatorios.relatorio_bioimpedancia_evolucao(1, meses=6)
    
    # Exemplo: comparativo de exames
    # relatorios.comparativo_exames_laboratoriais(1, "Perfil Lipídico")
    
    print("Sistema de relatórios carregado!")