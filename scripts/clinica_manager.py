#!/usr/bin/env python3
"""
Sistema Principal de Gestão da Clínica - Dr. Felipe
Interface unificada para todos os módulos
"""

import sys
import os
from datetime import datetime, date
from pacientes_manager import PacientesManager
from relatorios_clinicos import RelatoriosClinico
from import_dados import ImportadorDados

class ClinicaManager:
    def __init__(self):
        self.manager = PacientesManager()
        self.relatorios = RelatoriosClinico()
        self.importador = ImportadorDados()
    
    def menu_principal(self):
        """Menu principal do sistema"""
        
        while True:
            print("\n" + "="*50)
            print("🏥 SISTEMA DE GESTÃO DA CLÍNICA - DR. FELIPE")
            print("="*50)
            print("1. 👥 Gestão de Pacientes")
            print("2. 🧪 Exames Laboratoriais")
            print("3. 📊 Bioimpedância")
            print("4. 📈 Relatórios")
            print("5. 📥 Importação de Dados")
            print("6. 🔧 Utilitários")
            print("0. ❌ Sair")
            print("-" * 50)
            
            opcao = input("Escolha uma opção: ").strip()
            
            try:
                if opcao == "1":
                    self.menu_pacientes()
                elif opcao == "2":
                    self.menu_exames()
                elif opcao == "3":
                    self.menu_bioimpedancia()
                elif opcao == "4":
                    self.menu_relatorios()
                elif opcao == "5":
                    self.menu_importacao()
                elif opcao == "6":
                    self.menu_utilitarios()
                elif opcao == "0":
                    print("👋 Até logo!")
                    break
                else:
                    print("❌ Opção inválida!")
                    
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    def menu_pacientes(self):
        """Menu de gestão de pacientes"""
        
        while True:
            print("\n👥 GESTÃO DE PACIENTES")
            print("1. Adicionar novo paciente")
            print("2. Buscar paciente")
            print("3. Listar todos")
            print("0. Voltar")
            
            opcao = input("Opção: ").strip()
            
            if opcao == "1":
                self.adicionar_paciente_interativo()
            elif opcao == "2":
                self.buscar_paciente_interativo()
            elif opcao == "3":
                self.listar_pacientes()
            elif opcao == "0":
                break
    
    def adicionar_paciente_interativo(self):
        """Adiciona paciente de forma interativa"""
        
        print("\n➕ ADICIONAR NOVO PACIENTE")
        nome = input("Nome completo: ").strip()
        if not nome:
            print("❌ Nome é obrigatório!")
            return
        
        cpf = input("CPF (opcional): ").strip() or None
        telefone = input("Telefone (opcional): ").strip() or None
        email = input("Email (opcional): ").strip() or None
        endereco = input("Endereço (opcional): ").strip() or None
        observacoes = input("Observações (opcional): ").strip() or None
        
        # Data de nascimento
        data_nascimento = None
        data_str = input("Data nascimento (DD/MM/AAAA) (opcional): ").strip()
        if data_str:
            try:
                data_nascimento = datetime.strptime(data_str, "%d/%m/%Y").date()
            except:
                print("⚠️ Data inválida, continuando sem data de nascimento")
        
        paciente_id = self.manager.adicionar_paciente(
            nome=nome,
            cpf=cpf,
            data_nascimento=data_nascimento,
            telefone=telefone,
            email=email,
            endereco=endereco,
            observacoes=observacoes
        )
        
        if paciente_id:
            print(f"✅ Paciente {nome} adicionado com ID: {paciente_id}")
        else:
            print("❌ Erro ao adicionar paciente")
    
    def buscar_paciente_interativo(self):
        """Busca paciente de forma interativa"""
        
        termo = input("🔍 Digite nome ou CPF para buscar: ").strip()
        if not termo:
            return
        
        pacientes = self.manager.buscar_paciente(termo)
        
        if not pacientes:
            print("❌ Nenhum paciente encontrado")
            return
        
        print(f"\n📋 Encontrados {len(pacientes)} paciente(s):")
        for p in pacientes:
            print(f"ID: {p['id']} | Nome: {p['nome']} | CPF: {p['cpf']} | Telefone: {p['telefone']}")
    
    def listar_pacientes(self):
        """Lista todos os pacientes (limitado)"""
        
        sql = "SELECT id, nome, cpf, telefone FROM pacientes ORDER BY nome LIMIT 20;"
        self.manager.cursor.execute(sql)
        resultados = self.manager.cursor.fetchall()
        
        if not resultados:
            print("❌ Nenhum paciente cadastrado")
            return
        
        print(f"\n📋 Primeiros 20 pacientes:")
        for p in resultados:
            print(f"ID: {p[0]} | Nome: {p[1]} | CPF: {p[2]} | Telefone: {p[3]}")
    
    def menu_bioimpedancia(self):
        """Menu de bioimpedância"""
        
        while True:
            print("\n📊 BIOIMPEDÂNCIA")
            print("1. Adicionar medição")
            print("2. Ver histórico de paciente")
            print("3. Gráfico de evolução")
            print("0. Voltar")
            
            opcao = input("Opção: ").strip()
            
            if opcao == "1":
                self.adicionar_bioimpedancia_interativo()
            elif opcao == "2":
                self.ver_historico_bioimpedancia()
            elif opcao == "3":
                self.gerar_grafico_bioimpedancia()
            elif opcao == "0":
                break
    
    def adicionar_bioimpedancia_interativo(self):
        """Adiciona bioimpedância de forma interativa"""
        
        try:
            paciente_id = int(input("ID do paciente: "))
        except ValueError:
            print("❌ ID inválido")
            return
        
        # Data da medição
        data_str = input("Data da medição (DD/MM/AAAA) ou ENTER para hoje: ").strip()
        if data_str:
            try:
                data_medicao = datetime.strptime(data_str, "%d/%m/%Y").date()
            except:
                print("❌ Data inválida")
                return
        else:
            data_medicao = date.today()
        
        # Coleta dados (todos opcionais)
        dados = {}
        
        for campo, descricao in [
            ('peso', 'Peso (kg)'),
            ('altura', 'Altura (cm)'),
            ('imc', 'IMC'),
            ('gordura_corporal', 'Gordura corporal (%)'),
            ('massa_muscular', 'Massa muscular (kg)'),
            ('massa_ossea', 'Massa óssea (kg)'),
            ('agua_corporal', 'Água corporal (%)'),
            ('metabolismo_basal', 'Metabolismo basal (kcal)'),
            ('gordura_visceral', 'Gordura visceral (nível)')
        ]:
            valor = input(f"{descricao} (opcional): ").strip()
            if valor:
                try:
                    if campo in ['metabolismo_basal', 'gordura_visceral']:
                        dados[campo] = int(valor)
                    else:
                        dados[campo] = float(valor)
                except ValueError:
                    print(f"⚠️ Valor inválido para {descricao}, ignorando")
        
        observacoes = input("Observações (opcional): ").strip() or None
        
        bio_id = self.manager.adicionar_bioimpedancia(
            paciente_id=paciente_id,
            data_medicao=data_medicao,
            observacoes=observacoes,
            **dados
        )
        
        if bio_id:
            print(f"✅ Bioimpedância adicionada com ID: {bio_id}")
        else:
            print("❌ Erro ao adicionar bioimpedância")
    
    def ver_historico_bioimpedancia(self):
        """Mostra histórico de bioimpedância"""
        
        try:
            paciente_id = int(input("ID do paciente: "))
        except ValueError:
            print("❌ ID inválido")
            return
        
        medicoes = self.manager.buscar_bioimpedancia_paciente(paciente_id)
        
        if not medicoes:
            print("❌ Nenhuma medição encontrada")
            return
        
        print(f"\n📊 Histórico de bioimpedância (últimas {len(medicoes)} medições):")
        for m in medicoes:
            print(f"Data: {m['data_medicao']} | Peso: {m['peso']}kg | IMC: {m['imc']} | Gordura: {m['gordura_corporal']}%")
    
    def gerar_grafico_bioimpedancia(self):
        """Gera gráfico de evolução"""
        
        try:
            paciente_id = int(input("ID do paciente: "))
            meses = int(input("Últimos quantos meses (padrão 6): ") or "6")
        except ValueError:
            print("❌ Valores inválidos")
            return
        
        arquivo = self.relatorios.relatorio_bioimpedancia_evolucao(paciente_id, meses)
        if arquivo:
            print(f"📊 Gráfico gerado: {arquivo}")
    
    def menu_relatorios(self):
        """Menu de relatórios"""
        
        while True:
            print("\n📈 RELATÓRIOS")
            print("1. Dashboard completo do paciente")
            print("2. Evolução bioimpedância")
            print("3. Comparativo de exames")
            print("4. Relatório completo (JSON)")
            print("0. Voltar")
            
            opcao = input("Opção: ").strip()
            
            if opcao == "1":
                self.gerar_dashboard()
            elif opcao == "2":
                self.gerar_grafico_bioimpedancia()
            elif opcao == "3":
                self.gerar_comparativo_exames()
            elif opcao == "4":
                self.gerar_relatorio_completo()
            elif opcao == "0":
                break
    
    def gerar_dashboard(self):
        """Gera dashboard HTML"""
        
        try:
            paciente_id = int(input("ID do paciente: "))
        except ValueError:
            print("❌ ID inválido")
            return
        
        arquivo = self.relatorios.dashboard_paciente(paciente_id)
        if arquivo:
            print(f"🌐 Dashboard gerado: {arquivo}")
    
    def menu_importacao(self):
        """Menu de importação"""
        
        while True:
            print("\n📥 IMPORTAÇÃO DE DADOS")
            print("1. Gerar templates CSV")
            print("2. Importar pacientes")
            print("3. Importar bioimpedância")
            print("4. Importar exames")
            print("0. Voltar")
            
            opcao = input("Opção: ").strip()
            
            if opcao == "1":
                self.gerar_templates()
            elif opcao == "2":
                arquivo = input("Caminho do arquivo CSV: ").strip()
                self.importador.importar_pacientes_csv(arquivo)
            elif opcao == "3":
                arquivo = input("Caminho do arquivo CSV: ").strip()
                self.importador.importar_bioimpedancia_csv(arquivo)
            elif opcao == "4":
                arquivo = input("Caminho do arquivo CSV: ").strip()
                self.importador.importar_exames_laboratoriais_csv(arquivo)
            elif opcao == "0":
                break
    
    def gerar_templates(self):
        """Gera todos os templates"""
        
        self.importador.gerar_template_pacientes_csv()
        self.importador.gerar_template_bioimpedancia_csv()
        self.importador.gerar_template_exames_csv()
        print("✅ Templates gerados em /root/clawd/templates/")
    
    def menu_utilitarios(self):
        """Menu de utilitários"""
        
        while True:
            print("\n🔧 UTILITÁRIOS")
            print("1. Testar conexão com banco")
            print("2. Status do sistema")
            print("3. Backup dados")
            print("0. Voltar")
            
            opcao = input("Opção: ").strip()
            
            if opcao == "1":
                if self.manager.test_connection():
                    print("✅ Conexão OK!")
                else:
                    print("❌ Problema de conexão")
            elif opcao == "2":
                self.mostrar_status()
            elif opcao == "3":
                print("🔄 Função de backup será implementada quando a conexão estiver ativa")
            elif opcao == "0":
                break
    
    def mostrar_status(self):
        """Mostra status do sistema"""
        
        print("\n🏥 STATUS DO SISTEMA")
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Conexão: {'✅ OK' if hasattr(self.manager, 'connection') else '❌ Erro'}")
        print(f"Diretórios:")
        print(f"  - Templates: /root/clawd/templates/")
        print(f"  - Relatórios: /root/clawd/relatorios/")
        print(f"  - Scripts: /root/clawd/scripts/")

def main():
    """Função principal"""
    
    try:
        print("🚀 Iniciando Sistema de Gestão da Clínica...")
        clinica = ClinicaManager()
        clinica.menu_principal()
        
    except KeyboardInterrupt:
        print("\n👋 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        print("💡 Verifique se o banco de dados está acessível")

if __name__ == "__main__":
    main()